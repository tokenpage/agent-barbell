import React from 'react';

import { IMultiAnyChildProps } from '@kibalabs/core-react';
import { useIsRestoringWeb3Session, useWeb3Account, useWeb3LoginSignature } from '@kibalabs/web3-react';

import { User } from './client/client';
import { useGlobals } from './GlobalsContext';

interface AuthContextType {
  user: User | null | undefined;
  isWeb3AccountConnecting: boolean;
  isWeb3AccountConnected: boolean;
  isWeb3AccountLoggedIn: boolean;
  isAuthenticated: boolean;
  accountAddress: string | undefined;
  loginWithWallet: () => Promise<User>;
  createUser: (username: string | null) => Promise<User>;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps extends IMultiAnyChildProps {
}

export function AuthProvider(props: AuthProviderProps): React.ReactElement {
  const { agentBarbellClient } = useGlobals();
  const account = useWeb3Account();
  const loginSignature = useWeb3LoginSignature();
  const isRestoringWeb3Session = useIsRestoringWeb3Session();
  const accountAddress = account?.address;
  const isWeb3AccountConnecting = account === undefined || isRestoringWeb3Session;
  const isWeb3AccountConnected = account != null;
  const isWeb3AccountLoggedIn = account != null && loginSignature != null;
  const [user, setUser] = React.useState<User | null | undefined>(undefined);
  const isAuthenticated = isWeb3AccountLoggedIn && user != null;

  const authToken = React.useMemo((): string | null => {
    if (!loginSignature) {
      return null;
    }
    return btoa(JSON.stringify(loginSignature));
  }, [loginSignature]);

  const logout = React.useCallback((): void => {
    setUser(null);
    window.location.reload();
  }, []);

  const loginWithWallet = React.useCallback(async (): Promise<User> => {
    if (!authToken) {
      throw new Error('No authToken available');
    }
    const newUser = await agentBarbellClient.login(authToken);
    setUser(newUser);
    return newUser;
  }, [agentBarbellClient, authToken]);

  const createUser = React.useCallback(async (username: string | null): Promise<User> => {
    if (!authToken || !accountAddress) {
      throw new Error('No authToken/accountAddress available');
    }
    const newUser = await agentBarbellClient.createUser(accountAddress, username, authToken);
    setUser(newUser);
    return newUser;
  }, [agentBarbellClient, authToken, accountAddress]);

  const contextValue = React.useMemo((): AuthContextType => ({
    user,
    isWeb3AccountConnecting,
    isWeb3AccountConnected,
    isWeb3AccountLoggedIn,
    isAuthenticated,
    accountAddress,
    loginWithWallet,
    createUser,
    logout,
  }), [
    user,
    isWeb3AccountConnecting,
    isWeb3AccountConnected,
    isWeb3AccountLoggedIn,
    isAuthenticated,
    accountAddress,
    loginWithWallet,
    createUser,
    logout,
  ]);

  return (
    <AuthContext.Provider value={contextValue}>
      {props.children}
    </AuthContext.Provider>
  );
}

export const useAuth = (): AuthContextType => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('Cannot use auth context without a provider');
  }
  return context;
};
