// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {AWKErrors} from "../agentwalletkit/AWKErrors.sol";
import {AWKUniswapV3SwapAdapter} from "../agentwalletkit/adapters/AWKUniswapV3SwapAdapter.sol";
import {IBarbellSellPolicy} from "./BarbellSellPolicy.sol";

/**
 * @title BarbellUniswapV3SwapAdapter
 * @notice Uniswap V3 swap adapter constrained to the barbell's allowed tokens.
 * @dev Ported from yieldseeker-app/contracts/src/adapters/UniswapV3SwapAdapter.sol.
 *      YieldSeeker's version forces every swap to buy the wallet's base asset and records
 *      a fee. A barbell rotates between two risk legs in both directions and charges no
 *      fee, so instead both sides of the swap are checked against the allowlist.
 */
contract BarbellUniswapV3SwapAdapter is AWKUniswapV3SwapAdapter {
    address public immutable SELL_POLICY;

    constructor(address uniswapV3Router, address sellPolicy) AWKUniswapV3SwapAdapter(uniswapV3Router) {
        if (sellPolicy == address(0)) revert AWKErrors.ZeroAddress();
        SELL_POLICY = sellPolicy;
    }

    function _beforeSwap(address sellToken, address buyToken) internal view override {
        IBarbellSellPolicy(SELL_POLICY).validateAllowedToken(sellToken);
        IBarbellSellPolicy(SELL_POLICY).validateAllowedToken(buyToken);
    }
}
