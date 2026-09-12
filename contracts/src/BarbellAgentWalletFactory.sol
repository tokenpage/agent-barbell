// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {BarbellAgentWalletV1 as AgentWallet} from "./BarbellAgentWalletV1.sol";
import {AWKAgentWalletFactory} from "./agentwalletkit/AWKAgentWalletFactory.sol";

/**
 * @title BarbellAgentWalletFactory
 * @notice Factory for deploying barbell agent wallets.
 * @dev Ported from yieldseeker-app/contracts/src/AgentWalletFactory.sol. AWKAgentWalletFactory
 *      is abstract because createAgentWallet's signature is product-specific; YieldSeeker's takes
 *      a baseAsset, ours does not.
 */
contract BarbellAgentWalletFactory is AWKAgentWalletFactory {
    /// @param admin Address that gets the admin role for dangerous operations
    /// @param agentOperator Address that can create agent wallets (the backend server)
    constructor(address admin, address agentOperator) AWKAgentWalletFactory(admin, agentOperator) {}

    function createAgentWallet(address owner, uint256 ownerAgentIndex) public onlyRole(AGENT_OPERATOR_ROLE) returns (AgentWallet ret) {
        ret = AgentWallet(payable(address(_deployWallet(owner, ownerAgentIndex))));
        ret.initialize(owner, ownerAgentIndex);
        emit AgentWalletCreated(address(ret), owner, ownerAgentIndex);
    }
}
