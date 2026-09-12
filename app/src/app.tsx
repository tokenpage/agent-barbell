import React from 'react';

import { LocalStorageClient, Requester } from '@kibalabs/core';
import { IRoute, MockStorage, Router, SubRouter, useFavicon } from '@kibalabs/core-react';
import { KibaApp } from '@kibalabs/ui-react';
import { Web3AccountControlProvider, web3Initialize } from '@kibalabs/web3-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import './theme.scss';
import { AuthProvider } from './AuthContext';
import { BarbellProvider } from './BarbellContext';
import { AgentBarbellClient } from './client/client';
import { ContainingView } from './components/ContainingView';
import { GlobalsProvider, IGlobals } from './GlobalsContext';
import { BarbellOverviewPage } from './pages/BarbellOverviewPage';
import { ChatPage } from './pages/ChatPage';
import { CreateUserPage } from './pages/CreateUserPage';
import { FundBarbellPage } from './pages/FundBarbellPage';
import { HomePage } from './pages/HomePage';
import { REOWN_PROJECT_ID } from './util/constants';
import { usePrefersDarkMode } from './util/theme';

declare global {
  export interface Window {
    KIBA_RENDERED_PATH?: string;
    KIBA_PAGE_DATA?: unknown;
    KRT_API_URL?: string;
  }
}

const localStorageClient = new LocalStorageClient(typeof window !== 'undefined' ? window.localStorage : new MockStorage());
const apiUrl = (typeof window !== 'undefined' && window.KRT_API_URL) || 'https://agent-barbell-api.yieldseeker.xyz';
const requester = new Requester();
const agentBarbellClient = new AgentBarbellClient(requester, apiUrl);

web3Initialize({
  reownConfig: {
    projectId: REOWN_PROJECT_ID,
    name: 'Agent Barbell',
    description: 'Agent Barbell — a risk-budget barbell agent for Robinhood Chain',
    url: typeof window !== 'undefined' ? window.location.origin : 'https://agent-barbell.yieldseeker.xyz',
    icons: ['https://agent-barbell.yieldseeker.xyz/assets/icon.png'],
  },
});

const globals: IGlobals = {
  localStorageClient,
  requester,
  agentBarbellClient,
};

const queryClient = new QueryClient();

const routes: IRoute<IGlobals>[] = [
  { path: '/', page: HomePage },
  { path: '/create-user', page: CreateUserPage },
  { path: '/barbell/overview', page: BarbellOverviewPage },
  { path: '/barbell/fund', page: FundBarbellPage },
  { path: '/barbell/chat', page: ChatPage },
];

interface IAppProps {
  staticPath?: string;
}

export function App(props: IAppProps): React.ReactElement {
  const prefersDarkMode = usePrefersDarkMode();
  useFavicon(prefersDarkMode ? '/assets/icon.png' : '/assets/icon.png');

  React.useLayoutEffect((): void => {
    document.documentElement.setAttribute('data-theme', prefersDarkMode ? 'dark' : 'light');
  }, [prefersDarkMode]);

  const onWeb3AccountError = React.useCallback((error: Error): void => {
    console.error(error);
  }, []);

  return (
    <KibaApp isFullPageApp={true}>
      <GlobalsProvider globals={globals}>
        <QueryClientProvider client={queryClient}>
          <Router staticPath={props.staticPath}>
            <Web3AccountControlProvider localStorageClient={localStorageClient} onError={onWeb3AccountError}>
              <AuthProvider>
                <BarbellProvider>
                  <ContainingView>
                    <SubRouter routes={routes} />
                  </ContainingView>
                </BarbellProvider>
              </AuthProvider>
            </Web3AccountControlProvider>
          </Router>
        </QueryClientProvider>
      </GlobalsProvider>
    </KibaApp>
  );
}
