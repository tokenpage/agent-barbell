import React from 'react';

import { IMultiAnyChildProps } from '@kibalabs/core-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { useAuth } from './AuthContext';
import { CreateBarbellConfig, Resources } from './client';
import { useGlobals } from './GlobalsContext';

const REFETCH_INTERVAL_MILLIS = 30 * 1000;

interface BarbellContextType {
  barbell: Resources.Barbell | null | undefined;
  portfolio: Resources.Portfolio | undefined;
  riskState: Resources.RiskState | undefined;
  isLoading: boolean;
  error: Error | null;
  deactivationError: Error | null;
  createBarbell: (config: CreateBarbellConfig) => Promise<Resources.Barbell>;
  deactivateBarbell: () => Promise<void>;
  setRiskBudget: (maxDrawdownBps: number, targetSatelliteBps: number, maxSatelliteBps: number) => Promise<Resources.RiskState>;
  refresh: () => void;
}

const BarbellContext = React.createContext<BarbellContextType | undefined>(undefined);

interface BarbellProviderProps extends IMultiAnyChildProps {
}

export function BarbellProvider(props: BarbellProviderProps): React.ReactElement {
  const { agentBarbellClient } = useGlobals();
  const { authToken, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const barbellQuery = useQuery({
    queryKey: ['barbell'],
    queryFn: async (): Promise<Resources.Barbell | null> => agentBarbellClient.getBarbell(authToken as string),
    enabled: isAuthenticated && authToken != null,
  });
  const barbellId = barbellQuery.data?.barbellId;

  const portfolioQuery = useQuery({
    queryKey: ['portfolio', barbellId],
    queryFn: async (): Promise<Resources.Portfolio> => agentBarbellClient.getBarbellPortfolio(barbellId as string, authToken as string),
    enabled: barbellId != null && authToken != null,
    refetchInterval: REFETCH_INTERVAL_MILLIS,
  });

  const riskStateQuery = useQuery({
    queryKey: ['riskState', barbellId],
    queryFn: async (): Promise<Resources.RiskState> => agentBarbellClient.getBarbellRiskState(barbellId as string, authToken as string),
    enabled: barbellId != null && authToken != null,
    refetchInterval: REFETCH_INTERVAL_MILLIS,
  });

  const createBarbellMutation = useMutation({
    mutationFn: async (config: CreateBarbellConfig): Promise<Resources.Barbell> => agentBarbellClient.createBarbell(authToken as string, config),
    onSuccess: (barbell: Resources.Barbell): void => {
      console.info('[BarbellContext] create:success', { barbellId: barbell.barbellId });
      queryClient.setQueryData(['barbell'], barbell);
    },
  });
  const deactivateBarbellMutation = useMutation({
    mutationFn: async (): Promise<void> => {
      if (barbellId == null || authToken == null) {
        throw new Error('No active barbell');
      }
      await agentBarbellClient.deactivateBarbell(barbellId, authToken);
    },
    onSuccess: (): void => {
      queryClient.setQueryData(['barbell'], null);
      queryClient.removeQueries({ queryKey: ['portfolio', barbellId] });
      queryClient.removeQueries({ queryKey: ['riskState', barbellId] });
    },
  });

  const setRiskBudgetMutation = useMutation({
    mutationFn: async (variables: { maxDrawdownBps: number; targetSatelliteBps: number; maxSatelliteBps: number }): Promise<Resources.RiskState> => (
      agentBarbellClient.setRiskBudget(barbellId as string, variables.maxDrawdownBps, variables.targetSatelliteBps, variables.maxSatelliteBps, authToken as string)
    ),
    onSuccess: (riskState: Resources.RiskState): void => {
      queryClient.setQueryData(['riskState', barbellId], riskState);
    },
  });

  const createBarbell = React.useCallback(async (config: CreateBarbellConfig): Promise<Resources.Barbell> => {
    console.info('[BarbellContext] create:start', config);
    try {
      return await createBarbellMutation.mutateAsync(config);
    } catch (caughtError: unknown) {
      console.error('[BarbellContext] create:failed', caughtError);
      throw caughtError;
    }
  }, [createBarbellMutation]);
  const deactivateBarbell = React.useCallback(async (): Promise<void> => {
    return deactivateBarbellMutation.mutateAsync();
  }, [deactivateBarbellMutation]);

  const setRiskBudget = React.useCallback(async (maxDrawdownBps: number, targetSatelliteBps: number, maxSatelliteBps: number): Promise<Resources.RiskState> => {
    return setRiskBudgetMutation.mutateAsync({ maxDrawdownBps, targetSatelliteBps, maxSatelliteBps });
  }, [setRiskBudgetMutation]);

  const refresh = React.useCallback((): void => {
    queryClient.invalidateQueries({ queryKey: ['portfolio', barbellId] });
    queryClient.invalidateQueries({ queryKey: ['riskState', barbellId] });
  }, [queryClient, barbellId]);

  const contextValue = React.useMemo((): BarbellContextType => ({
    barbell: barbellQuery.data,
    portfolio: portfolioQuery.data,
    riskState: riskStateQuery.data,
    isLoading: barbellQuery.isLoading || deactivateBarbellMutation.isPending,
    error: (barbellQuery.error ?? portfolioQuery.error ?? riskStateQuery.error) as Error | null,
    deactivationError: deactivateBarbellMutation.error as Error | null,
    createBarbell,
    deactivateBarbell,
    setRiskBudget,
    refresh,
  }), [
    barbellQuery.data, barbellQuery.isLoading, barbellQuery.error,
    portfolioQuery.data, portfolioQuery.error,
    riskStateQuery.data, riskStateQuery.error,
    deactivateBarbellMutation.isPending, deactivateBarbellMutation.error,
    createBarbell, deactivateBarbell, setRiskBudget, refresh,
  ]);

  return (
    <BarbellContext.Provider value={contextValue}>
      {props.children}
    </BarbellContext.Provider>
  );
}

export const useBarbell = (): BarbellContextType => {
  const barbellContext = React.useContext(BarbellContext);
  if (!barbellContext) {
    throw new Error('Cannot use barbell context without a provider');
  }
  return barbellContext;
};
