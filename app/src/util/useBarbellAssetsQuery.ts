import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { BarbellAsset } from '../client/resources';
import { useGlobals } from '../GlobalsContext';

const ASSET_CACHE_MS = 60 * 60 * 1000;

export const useBarbellAssetsQuery = (chainId: number): UseQueryResult<BarbellAsset[], Error> => {
  const { agentBarbellClient } = useGlobals();
  return useQuery({
    queryKey: ['barbellAssets', chainId],
    queryFn: (): Promise<BarbellAsset[]> => agentBarbellClient.listBarbellAssets(chainId),
    staleTime: ASSET_CACHE_MS,
    refetchOnWindowFocus: false,
  });
};
