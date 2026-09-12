// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {RiskBudgetRegistry} from "../src/RiskBudgetRegistry.sol";
import {BarbellSellPolicy} from "../src/adapters/BarbellSellPolicy.sol";
import {BarbellUniswapV3SwapAdapter} from "../src/adapters/BarbellUniswapV3SwapAdapter.sol";
import {AWKAdapterRegistry as AdapterRegistry} from "../src/agentwalletkit/AWKAdapterRegistry.sol";
import {BarbellAgentWalletFactory as AgentWalletFactory} from "../src/BarbellAgentWalletFactory.sol";
import {BarbellAgentWalletV1 as AgentWallet} from "../src/BarbellAgentWalletV1.sol";
import {Script} from "forge-std/Script.sol";
import {stdJson} from "forge-std/StdJson.sol";
import {console2} from "forge-std/console2.sol";

/**
 * @title DeployScript
 * @notice Deploys the Agent Barbell system with selective contract deployment.
 * @dev Ported from yieldseeker-app/contracts/script/Deploy.s.sol.
 *      Usage: forge script script/Deploy.s.sol:DeployScript --rpc-url $ETH_RPC_URL --broadcast
 */
contract DeployScript is Script {
    using stdJson for string;

    // NOTE: deliberately not yieldseeker's 0x711 — a shared salt could collide addresses
    // with the production Base deployment.
    uint256 constant SALT = 0xBA12;

    struct Deployments {
        address adapterRegistry;
        address agentWalletFactory;
        address agentWalletImplementation;
        address riskBudgetRegistry;
        address sellPolicy;
        address uniswapV3SwapAdapter;
    }

    function safeReadAddress(string memory json, string memory key) internal pure returns (address) {
        try vm.parseJsonAddress(json, key) returns (address addr) {
            return addr;
        } catch {
            return address(0);
        }
    }

    function getUniswapV3Router(uint256 chainId) internal pure returns (address) {
        if (chainId == 4663) {
            return 0xCaf681a66D020601342297493863E78C959E5cb2;
        }
        revert(string.concat("Unsupported chain id for Uniswap V3 router: ", vm.toString(chainId)));
    }

    function getUsdg(uint256 chainId) internal pure returns (address) {
        if (chainId == 4663) {
            return 0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168;
        }
        revert(string.concat("Unsupported chain id for USDG: ", vm.toString(chainId)));
    }

    function getAnchorAsset(uint256 chainId) internal pure returns (address) {
        if (chainId == 4663) {
            return 0x92FD66527192E3e61d4DDd13322Aa222DE86F9B5;
        }
        revert(string.concat("Unsupported chain id for anchor asset: ", vm.toString(chainId)));
    }

    function getSatelliteAsset(uint256 chainId) internal pure returns (address) {
        if (chainId == 4663) {
            return 0x1b0E319c6A659F002271B69dB8A7df2F911c153E;
        }
        revert(string.concat("Unsupported chain id for satellite asset: ", vm.toString(chainId)));
    }

    function run() public {
        address serverAddress = vm.envAddress("SERVER_ADDRESS");
        uint256 deployerPrivateKey = vm.envUint("AB_DEPLOYER_PRIVATE_KEY");
        address deployerAddress = vm.addr(deployerPrivateKey);
        // NOTE: falls back to the deployer when unset. Acceptable for the hackathon, but it
        // means the hot deploy key retains admin over the registry and the sell policy.
        address multisigAdminAddress = vm.envOr("MULTISIG_ADMIN_ADDRESS", deployerAddress);
        address emergencyAdminAddress = deployerAddress;
        address uniswapV3Router = getUniswapV3Router(block.chainid);

        console2.log("=================================================");
        console2.log("AGENT BARBELL DEPLOYMENT SCRIPT");
        console2.log("=================================================");
        console2.log("Chain:", block.chainid);
        console2.log("Deployer:", deployerAddress);
        console2.log("Admin:", multisigAdminAddress);
        console2.log("Server:", serverAddress);
        console2.log("Uniswap V3 Router:", uniswapV3Router);
        console2.log("");

        Deployments memory deployments;
        string memory path = "./deployments.json";
        if (vm.exists(path)) {
            // forge-lint: disable-next-line(unsafe-cheatcode)
            string memory deployJson = vm.readFile(path);
            deployments = Deployments({
                adapterRegistry: safeReadAddress(deployJson, ".adapterRegistry"),
                agentWalletFactory: safeReadAddress(deployJson, ".agentWalletFactory"),
                agentWalletImplementation: safeReadAddress(deployJson, ".agentWalletImplementation"),
                riskBudgetRegistry: safeReadAddress(deployJson, ".riskBudgetRegistry"),
                sellPolicy: safeReadAddress(deployJson, ".sellPolicy"),
                uniswapV3SwapAdapter: safeReadAddress(deployJson, ".uniswapV3SwapAdapter")
            });
        }

        vm.startBroadcast(deployerPrivateKey);

        if (deployments.agentWalletFactory == address(0)) {
            AgentWalletFactory newAgentWalletFactory = new AgentWalletFactory{salt: bytes32(SALT)}(deployerAddress, serverAddress);
            deployments.agentWalletFactory = address(newAgentWalletFactory);
            console2.log("-> AgentWalletFactory deployed at:", address(newAgentWalletFactory));
        } else {
            console2.log("-> Using existing agentWalletFactory:", deployments.agentWalletFactory);
        }

        if (deployments.agentWalletImplementation == address(0)) {
            AgentWallet newAgentWalletImplementation = new AgentWallet{salt: bytes32(SALT)}(deployments.agentWalletFactory);
            deployments.agentWalletImplementation = address(newAgentWalletImplementation);
            console2.log("-> AgentWalletImplementation deployed at:", address(newAgentWalletImplementation));
        } else {
            console2.log("-> Using existing agentWalletImplementation:", deployments.agentWalletImplementation);
        }

        if (deployments.adapterRegistry == address(0)) {
            AdapterRegistry newAdapterRegistry = new AdapterRegistry{salt: bytes32(SALT)}(deployerAddress, emergencyAdminAddress);
            deployments.adapterRegistry = address(newAdapterRegistry);
            console2.log("-> AdapterRegistry deployed at:", address(newAdapterRegistry));
        } else {
            console2.log("-> Using existing adapterRegistry:", deployments.adapterRegistry);
        }

        if (deployments.sellPolicy == address(0)) {
            address[] memory initialTokens = new address[](3);
            initialTokens[0] = getAnchorAsset(block.chainid);
            initialTokens[1] = getSatelliteAsset(block.chainid);
            initialTokens[2] = getUsdg(block.chainid);
            BarbellSellPolicy newSellPolicy = new BarbellSellPolicy{salt: bytes32(SALT)}(deployerAddress, emergencyAdminAddress, initialTokens);
            deployments.sellPolicy = address(newSellPolicy);
            console2.log("-> BarbellSellPolicy deployed at:", address(newSellPolicy));
        } else {
            console2.log("-> Using existing sellPolicy:", deployments.sellPolicy);
        }

        if (deployments.uniswapV3SwapAdapter == address(0)) {
            BarbellUniswapV3SwapAdapter newUniswapV3SwapAdapter = new BarbellUniswapV3SwapAdapter{salt: bytes32(SALT)}(uniswapV3Router, deployments.sellPolicy);
            deployments.uniswapV3SwapAdapter = address(newUniswapV3SwapAdapter);
            console2.log("-> BarbellUniswapV3SwapAdapter deployed at:", address(newUniswapV3SwapAdapter));
        } else {
            console2.log("-> Using existing uniswapV3SwapAdapter:", deployments.uniswapV3SwapAdapter);
        }

        if (deployments.riskBudgetRegistry == address(0)) {
            RiskBudgetRegistry newRiskBudgetRegistry = new RiskBudgetRegistry{salt: bytes32(SALT)}(multisigAdminAddress, serverAddress);
            deployments.riskBudgetRegistry = address(newRiskBudgetRegistry);
            console2.log("-> RiskBudgetRegistry deployed at:", address(newRiskBudgetRegistry));
        } else {
            console2.log("-> Using existing riskBudgetRegistry:", deployments.riskBudgetRegistry);
        }

        console2.log("");
        console2.log("=================================================");
        console2.log("POST-DEPLOYMENT CONFIGURATION");
        console2.log("=================================================");
        AdapterRegistry adapterRegistry = AdapterRegistry(deployments.adapterRegistry);
        AgentWalletFactory agentWalletFactory = AgentWalletFactory(deployments.agentWalletFactory);

        if (address(agentWalletFactory.agentWalletImplementation()) != deployments.agentWalletImplementation) {
            agentWalletFactory.setAgentWalletImplementation(AgentWallet(payable(deployments.agentWalletImplementation)));
            console2.log("-> Factory implementation set");
        }
        if (address(agentWalletFactory.adapterRegistry()) != deployments.adapterRegistry) {
            agentWalletFactory.setAdapterRegistry(adapterRegistry);
            console2.log("-> Factory adapterRegistry set");
        }
        if (adapterRegistry.getTargetAdapter(uniswapV3Router) != deployments.uniswapV3SwapAdapter) {
            adapterRegistry.registerAdapter(deployments.uniswapV3SwapAdapter);
            adapterRegistry.setTargetAdapter(uniswapV3Router, deployments.uniswapV3SwapAdapter);
            console2.log("-> Uniswap V3 router registered to adapter");
        }

        vm.stopBroadcast();

        string memory json = "json";
        vm.serializeAddress(json, "adapterRegistry", deployments.adapterRegistry);
        vm.serializeAddress(json, "agentWalletFactory", deployments.agentWalletFactory);
        vm.serializeAddress(json, "agentWalletImplementation", deployments.agentWalletImplementation);
        vm.serializeAddress(json, "riskBudgetRegistry", deployments.riskBudgetRegistry);
        vm.serializeAddress(json, "sellPolicy", deployments.sellPolicy);
        string memory finalJson = vm.serializeAddress(json, "uniswapV3SwapAdapter", deployments.uniswapV3SwapAdapter);
        vm.writeJson(finalJson, "./deployments.json");
        console2.log("-> Deployments saved to ./deployments.json");
    }
}
