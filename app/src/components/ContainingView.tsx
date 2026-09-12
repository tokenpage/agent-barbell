import React from 'react';

import { ISingleAnyChildProps, useLocation, useNavigator } from '@kibalabs/core-react';

import { useAuth } from '../AuthContext';

// NOTE: trimmed port of yieldseeker-app's ContainingView.tsx redirect state
// machine — landing -> attempt login -> NO_USER -> create-user -> dashboard.
// No agents/navbar/banner concerns here yet.
interface IContainingViewProps extends ISingleAnyChildProps {
}

export function ContainingView(props: IContainingViewProps): React.ReactElement {
  const location = useLocation();
  const navigator = useNavigator();
  const { isWeb3AccountConnecting, isWeb3AccountConnected, isWeb3AccountLoggedIn, isAuthenticated, loginWithWallet } = useAuth();
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
    if (isWeb3AccountConnecting) {
      return;
    }
    if (needsRegistration && location.pathname !== '/create-user') {
      navigator.navigateTo('/create-user');
      return;
    }
    if (isAuthenticated) {
      if (location.pathname === '/' || location.pathname === '/create-user') {
        navigator.navigateTo('/dashboard');
      }
      return;
    }
    // Not authenticated and not mid-registration: any other page (including a
    // direct deep-link to /dashboard or /create-user) redirects home.
    if (location.pathname !== '/' && !(location.pathname === '/create-user' && needsRegistration)) {
      navigator.navigateTo('/');
    }
  }, [isWeb3AccountConnecting, needsRegistration, isAuthenticated, location.pathname, navigator]);

  return <React.Fragment>{props.children}</React.Fragment>;
}
