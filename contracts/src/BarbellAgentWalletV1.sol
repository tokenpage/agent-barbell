// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {AWKAgentWalletV1} from "./agentwalletkit/AWKAgentWalletV1.sol";

/**
 * @title BarbellAgentWalletV1
 * @notice Concrete agent wallet for the barbell agent.
 * @dev Ported from yieldseeker-app/contracts/src/AgentWalletV1.sol, which exists for the same
 *      reason: AWKAgentWalletV1 is abstract and each product supplies its own initializer.
 *      YieldSeeker's version adds a baseAsset and a FeeTracker; a barbell has two legs rather
 *      than one base asset, and charges no fee, so neither is needed and no extra storage
 *      namespace is declared.
 */
contract BarbellAgentWalletV1 is AWKAgentWalletV1 {
    constructor(address factory) AWKAgentWalletV1(factory) {}

}
