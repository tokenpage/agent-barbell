declare global {
  export interface Window {
    KRT_API_URL?: string;
    KRT_REOWN_PROJECT_ID?: string;
  }
}

// NOTE: create a project at https://cloud.reown.com and set KRT_REOWN_PROJECT_ID —
// WalletConnect/Reown login won't work without it, but
// injected-provider connect still will.
export const REOWN_PROJECT_ID = (typeof window !== 'undefined' && window.KRT_REOWN_PROJECT_ID) || '';

export const ROBINHOOD_CHAIN_ID = 4663;
export const ROBINHOOD_CHAIN_NAME = 'Robinhood';
export const ROBINHOOD_RPC_URL = 'https://rpc.mainnet.chain.robinhood.com';
export const ROBINHOOD_EXPLORER_URL = 'https://robinhoodchain.blockscout.com';

// Robinhood Chain's stablecoin is USDG (Global Dollar, 6dp) — there is no canonical
// USDC on 4663.
export const USDG_ADDRESS = '0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168';
export const WETH_ADDRESS = '0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73';
export const ANCHOR_ASSET_ADDRESS = '0x92FD66527192E3e61d4DDd13322Aa222DE86F9B5';
export const SATELLITE_ASSET_ADDRESS = '0x1b0E319c6A659F002271B69dB8A7df2F911c153E';

export const ASSET_SYMBOL_MAP: Record<string, string> = {
  [USDG_ADDRESS]: 'USDG',
  [WETH_ADDRESS]: 'WETH',
  [ANCHOR_ASSET_ADDRESS]: 'SGOV',
  [SATELLITE_ASSET_ADDRESS]: 'GME',
};

export const ASSET_DECIMALS_MAP: Record<string, number> = {
  [USDG_ADDRESS]: 6,
  [WETH_ADDRESS]: 18,
  [ANCHOR_ASSET_ADDRESS]: 18,
  [SATELLITE_ASSET_ADDRESS]: 18,
};

export const DEFAULT_MAX_DRAWDOWN_BPS = 1500;
export const DEFAULT_TARGET_SATELLITE_BPS = 2000;
export const DEFAULT_MAX_SATELLITE_BPS = 4000;
