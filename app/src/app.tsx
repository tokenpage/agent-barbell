import React from 'react';

import { LocalStorageClient } from '@kibalabs/core';
import { IRoute, MockStorage, Router, SubRouter, useFavicon } from '@kibalabs/core-react';
import { KibaApp } from '@kibalabs/ui-react';
import { Web3AccountControlProvider, web3Initialize } from '@kibalabs/web3-react';

import './theme.scss';
import { AuthProvider } from './AuthContext';
import { AgentBarbellClient } from './client/client';
import { ContainingView } from './components/ContainingView';
import { GlobalsProvider, IGlobals } from './GlobalsContext';
import { CreateUserPage } from './pages/CreateUserPage';
import { DashboardPage } from './pages/DashboardPage';
import { HomePage } from './pages/HomePage';
import { REOWN_PROJECT_ID } from './util/constants';

declare global {
  export interface Window {
    KIBA_RENDERED_PATH?: string;
    KIBA_PAGE_DATA?: unknown;
    KRT_API_URL?: string;
  }
}

const localStorageClient = new LocalStorageClient(typeof window !== 'undefined' ? window.localStorage : new MockStorage());
const apiUrl = (typeof window !== 'undefined' && window.KRT_API_URL) || 'https://agent-barbell-api.yieldseeker.xyz';
const agentBarbellClient = new AgentBarbellClient(apiUrl);

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
  agentBarbellClient,
};

const routes: IRoute<IGlobals>[] = [
  { path: '/', page: HomePage },
  { path: '/create-user', page: CreateUserPage },
  { path: '/dashboard', page: DashboardPage },
];

interface IAppProps {
  staticPath?: string;
}

export function App(props: IAppProps): React.ReactElement {
  useFavicon('/assets/icon.png');

  const onWeb3AccountError = React.useCallback((error: Error): void => {
    console.error(error);
  }, []);

  return (
    <KibaApp isFullPageApp={true}>
      <GlobalsProvider globals={globals}>
        <Router staticPath={props.staticPath}>
          <Web3AccountControlProvider localStorageClient={localStorageClient} onError={onWeb3AccountError}>
            <AuthProvider>
              <ContainingView>
                <SubRouter routes={routes} />
              </ContainingView>
            </AuthProvider>
          </Web3AccountControlProvider>
        </Router>
      </GlobalsProvider>
    </KibaApp>
  );
}
