import React from 'react';

import { ISingleAnyChildProps, useLocation, useNavigator } from '@kibalabs/core-react';

import { useAuth } from '../AuthContext';
import { usePrefersDarkMode } from '../util/theme';

interface IContainingViewProps extends ISingleAnyChildProps {
}

export function ContainingView(props: IContainingViewProps): React.ReactElement {
  const location = useLocation();
  const navigator = useNavigator();
  const { isWeb3AccountConnecting, isWeb3AccountConnected, isWeb3AccountLoggedIn, isAuthenticated, loginWithWallet } = useAuth();
  const prefersDarkMode = usePrefersDarkMode();
  const [needsRegistration, setNeedsRegistration] = React.useState(false);
  const isLoggingInRef = React.useRef(false);

  React.useEffect((): void => {
    if (isWeb3AccountConnecting) {
      return;
    }
    if (!isWeb3AccountConnected || !isWeb3AccountLoggedIn || isAuthenticated || needsRegistration || isLoggingInRef.current) {
      return;
    }
    isLoggingInRef.current = true;
    loginWithWallet()
      .catch((error: Error): void => {
        if (error.message === 'NO_USER') {
          setNeedsRegistration(true);
        } else {
          console.error('[ContainingView] Error during loginWithWallet:', error);
        }
      })
      .finally((): void => {
        isLoggingInRef.current = false;
      });
  }, [isWeb3AccountConnecting, isWeb3AccountConnected, isWeb3AccountLoggedIn, isAuthenticated, needsRegistration, loginWithWallet]);

  React.useEffect((): void => {
    if (isAuthenticated && needsRegistration) {
      setNeedsRegistration(false);
    }
  }, [isAuthenticated, needsRegistration]);

  React.useEffect((): void => {
    if (isWeb3AccountConnecting) {
      return;
    }
    if (needsRegistration && !isAuthenticated && location.pathname !== '/create-user') {
      navigator.navigateTo('/create-user');
      return;
    }
    if (isAuthenticated) {
      if (location.pathname === '/' || location.pathname === '/create-user') {
        navigator.navigateTo('/barbell/overview');
      }
      return;
    }
    // The wallet is signed in but the user fetch is still in flight — redirecting now would
    // bounce a deep link back to the landing page before auth has had a chance to resolve.
    if (isWeb3AccountLoggedIn && !needsRegistration) {
      return;
    }
    // Not authenticated and not mid-registration: any other page redirects home.
    if (location.pathname !== '/' && !(location.pathname === '/create-user' && needsRegistration)) {
      navigator.navigateTo('/');
    }
  }, [isWeb3AccountConnecting, isWeb3AccountLoggedIn, needsRegistration, isAuthenticated, location.pathname, navigator]);

  const onBrandClicked = React.useCallback((): void => {
    navigator.navigateTo('/');
  }, [navigator]);


  return (
    <div className='ab-shell'>
      <header className='ab-nav'>
        <button className='ab-brand' type='button' onClick={onBrandClicked} aria-label='Go to Agent Barbell home'>
          <img src={prefersDarkMode ? '/assets/wordmark-dark.svg' : '/assets/wordmark-light.svg'} alt='Agent Barbell' />
        </button>
        <div className='ab-nav-tools'>
          <span className='ab-network-pill'>Robinhood Chain · 4663</span>
        </div>
      </header>
      <main className='ab-main'>{props.children}</main>
      <footer className='ab-footer'>
        <span>Agent Barbell · a yieldseeker agent</span>
        <span>{isAuthenticated ? 'Wallet connected' : 'non-custodial · withdraw whenever you like'}</span>
      </footer>
    </div>
  );
}
