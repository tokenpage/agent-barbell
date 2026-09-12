// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {AWKErrors} from "./agentwalletkit/AWKErrors.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

error NotWalletOwner(address caller, address wallet);
error InvalidPolicy();
error KillSwitchNotTriggered(address wallet);

interface IAWKAgentWalletOwner {
    function owner() external view returns (address);
}

/**
 * @title RiskBudgetRegistry
 * @notice Public, verifiable record of what each barbell promised and whether it defended it.
 * @dev Modelled on yieldseeker-app/contracts/src/adapters/SwapSellPolicy.sol — AccessControl,
 *      small state, one event per mutation. The event log is the product: the Substreams
 *      pipeline indexes it, and anyone can check the agent's narration against the chain.
 *
 *      Authority is deliberately split. The operator may record a kill switch (a defensive,
 *      risk-reducing action) but may never clear one; only the wallet owner can re-arm.
 *      The language model has no path to either.
 */
contract RiskBudgetRegistry is AccessControl {
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    uint16 public constant MAX_BPS = 10000;

    struct Policy {
        uint16 maxDrawdownBps;
        uint16 targetSatelliteBps;
        uint16 maxSatelliteBps;
        uint64 updatedAt;
        bool isKilled;
    }

    mapping(address wallet => Policy) private policies;

    event PolicyUpdated(address indexed wallet, uint16 maxDrawdownBps, uint16 targetSatelliteBps, uint16 maxSatelliteBps);
    event SatelliteResized(address indexed wallet, uint16 fromBps, uint16 toBps, string reason);
    event KillSwitchTriggered(address indexed wallet, uint16 drawdownBps, uint16 newSatelliteBps, string reason);
    event KillSwitchCleared(address indexed wallet);

    constructor(address admin, address operator) {
        if (admin == address(0)) revert AWKErrors.ZeroAddress();
        if (operator == address(0)) revert AWKErrors.ZeroAddress();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(OPERATOR_ROLE, operator);
    }

    modifier onlyWalletOwner(address wallet) {
        if (IAWKAgentWalletOwner(wallet).owner() != msg.sender) revert NotWalletOwner(msg.sender, wallet);
        _;
    }

    function setPolicy(address wallet, Policy calldata policy) external onlyWalletOwner(wallet) {
        if (policy.maxDrawdownBps == 0 || policy.maxDrawdownBps > MAX_BPS) revert InvalidPolicy();
        if (policy.maxSatelliteBps > MAX_BPS) revert InvalidPolicy();
        if (policy.targetSatelliteBps > policy.maxSatelliteBps) revert InvalidPolicy();
        Policy storage stored = policies[wallet];
        stored.maxDrawdownBps = policy.maxDrawdownBps;
        stored.targetSatelliteBps = policy.targetSatelliteBps;
        stored.maxSatelliteBps = policy.maxSatelliteBps;
        stored.updatedAt = uint64(block.timestamp);
        emit PolicyUpdated(wallet, policy.maxDrawdownBps, policy.targetSatelliteBps, policy.maxSatelliteBps);
    }

    function recordSatelliteResize(address wallet, uint16 fromBps, uint16 toBps, string calldata reason) external onlyRole(OPERATOR_ROLE) {
        if (fromBps > MAX_BPS || toBps > MAX_BPS) revert InvalidPolicy();
        emit SatelliteResized(wallet, fromBps, toBps, reason);
    }

    function recordKillSwitch(address wallet, uint16 drawdownBps, uint16 newSatelliteBps, string calldata reason) external onlyRole(OPERATOR_ROLE) {
        if (drawdownBps > MAX_BPS || newSatelliteBps > MAX_BPS) revert InvalidPolicy();
        policies[wallet].isKilled = true;
        emit KillSwitchTriggered(wallet, drawdownBps, newSatelliteBps, reason);
    }

    function clearKillSwitch(address wallet) external onlyWalletOwner(wallet) {
        if (!policies[wallet].isKilled) revert KillSwitchNotTriggered(wallet);
        policies[wallet].isKilled = false;
        emit KillSwitchCleared(wallet);
    }

    function getPolicy(address wallet) external view returns (Policy memory) {
        return policies[wallet];
    }

    function isKilled(address wallet) external view returns (bool) {
        return policies[wallet].isKilled;
    }
}
