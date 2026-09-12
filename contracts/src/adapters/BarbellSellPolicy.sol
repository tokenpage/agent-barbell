// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {AWKErrors} from "../agentwalletkit/AWKErrors.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {EnumerableSet} from "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

error TokenNotAllowed(address token);

interface IBarbellSellPolicy {
    function isAllowedToken(address token) external view returns (bool);
    function validateAllowedToken(address token) external view;
}

/**
 * @title BarbellSellPolicy
 * @notice Allowlist of tokens the barbell agent may trade.
 * @dev Ported from yieldseeker-app/contracts/src/adapters/SwapSellPolicy.sol.
 *      Unlike YieldSeeker's version there is no "sell only" direction: a barbell rotates
 *      between its two legs, so both sides of every swap are validated against one list.
 */
contract BarbellSellPolicy is AccessControl, IBarbellSellPolicy {
    using EnumerableSet for EnumerableSet.AddressSet;

    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");

    EnumerableSet.AddressSet private allowedTokens;

    event AllowedTokenAdded(address indexed token);
    event AllowedTokenRemoved(address indexed token);

    constructor(address admin, address emergencyAdmin, address[] memory initialTokens) {
        if (admin == address(0)) revert AWKErrors.ZeroAddress();
        if (emergencyAdmin == address(0)) revert AWKErrors.ZeroAddress();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(EMERGENCY_ROLE, emergencyAdmin);
        for (uint256 i = 0; i < initialTokens.length; i++) {
            if (initialTokens[i] == address(0)) revert AWKErrors.ZeroAddress();
            if (allowedTokens.add(initialTokens[i])) {
                emit AllowedTokenAdded(initialTokens[i]);
            }
        }
    }

    function addAllowedToken(address token) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (token == address(0)) revert AWKErrors.ZeroAddress();
        if (allowedTokens.add(token)) {
            emit AllowedTokenAdded(token);
        }
    }

    function addAllowedTokens(address[] calldata tokens) external onlyRole(DEFAULT_ADMIN_ROLE) {
        for (uint256 i = 0; i < tokens.length; i++) {
            if (tokens[i] == address(0)) revert AWKErrors.ZeroAddress();
            if (allowedTokens.add(tokens[i])) {
                emit AllowedTokenAdded(tokens[i]);
            }
        }
    }

    function removeAllowedToken(address token) external onlyRole(EMERGENCY_ROLE) {
        if (allowedTokens.remove(token)) {
            emit AllowedTokenRemoved(token);
        }
    }

    function isAllowedToken(address token) external view returns (bool) {
        return allowedTokens.contains(token);
    }

    function validateAllowedToken(address token) external view {
        if (!allowedTokens.contains(token)) revert TokenNotAllowed(token);
    }

    function getAllowedTokens() external view returns (address[] memory) {
        return allowedTokens.values();
    }
}
