import React from 'react';

import { Alignment, Box, Button, ContainingView, Dialog, Direction, getVariant, Image, KibaIcon, PaddingSize, SelectableView, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { Eip6963ProviderDetail, useIsReownInitialized, useOnLinkWeb3AccountsClicked, useWeb3Account, useWeb3OnReownLoginClicked, useWeb3Providers } from '@kibalabs/web3-react';

interface IProviderDialogProps {
  isOpen: boolean;
  providers: Eip6963ProviderDetail[];
  onProviderSelected: (provider: Eip6963ProviderDetail) => void;
  onSignInWithReownClicked: () => void;
  isReownAvailable: boolean;
  onClose: () => void;
}

function ProviderDialog(props: IProviderDialogProps): React.ReactElement {
  return (
    <Dialog isOpen={props.isOpen} onCloseClicked={props.onClose} isClosableByBackdrop={true} isClosableByEscape={true} maxWidth='calc(min(90%, 600px))' maxHeight='90%'>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} shouldAddGutters={true} paddingHorizontal={PaddingSize.Wide} paddingVertical={PaddingSize.Wide}>
        <Text variant='header2' alignment={TextAlignment.Center}>Connect Wallet</Text>
        <Spacing />
        {props.providers.map((provider: Eip6963ProviderDetail): React.ReactElement => (
          <Box key={provider.info.uuid} maxWidth='400px'>
            <SelectableView onClicked={(): void => props.onProviderSelected(provider)} isSelected={false} isFullWidth={true}>
              <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isFullWidth={true}>
                <Box width='2.5rem' height='2.5rem'>
                  <Image source={provider.info.icon} alternativeText={`${provider.info.name} icon`} isFullWidth={true} isFullHeight={true} />
                </Box>
                <Spacing variant={PaddingSize.Wide} />
                <Stack.Item growthFactor={1} shrinkFactor={1}>
                  <Text variant={getVariant('bold')}>{provider.info.name}</Text>
                </Stack.Item>
                <Spacing variant={PaddingSize.Wide} />
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack>
            </SelectableView>
          </Box>
        ))}
        {props.isReownAvailable && (
          <Box maxWidth='400px'>
            <SelectableView onClicked={props.onSignInWithReownClicked} isSelected={false} isFullWidth={true}>
              <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isFullWidth={true}>
                <Stack.Item growthFactor={1} shrinkFactor={1}>
                  <Text variant={getVariant('bold')}>More wallets (WalletConnect)</Text>
                </Stack.Item>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack>
            </SelectableView>
          </Box>
        )}
      </Stack>
    </Dialog>
  );
}

export function HomePage(): React.ReactElement {
  const account = useWeb3Account();
  const [web3Providers, chooseEip1193Provider] = useWeb3Providers();
  const onLinkAccountsClicked = useOnLinkWeb3AccountsClicked();
  const onSignInWithReownClicked = useWeb3OnReownLoginClicked();
  const isReownInitialized = useIsReownInitialized();
  const [isProviderDialogOpen, setIsProviderDialogOpen] = React.useState(false);

  const onConnectWalletClicked = React.useCallback(async (): Promise<void> => {
    const accountsLinked = await onLinkAccountsClicked();
    if (!accountsLinked) {
      setIsProviderDialogOpen(true);
    }
  }, [onLinkAccountsClicked]);

  const onSignInWithReownButtonClicked = async (): Promise<void> => {
    setIsProviderDialogOpen(false);
    await onSignInWithReownClicked();
  };

  const onProviderSelected = React.useCallback(async (provider: Eip6963ProviderDetail): Promise<void> => {
    chooseEip1193Provider(provider.info.rdns);
    setIsProviderDialogOpen(false);
    await onLinkAccountsClicked();
  }, [chooseEip1193Provider, onLinkAccountsClicked]);

  return (
    <ContainingView maxWidth='600px'>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} isFullHeight={true} isFullWidth={true} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
        <Text variant='header1' alignment={TextAlignment.Center}>Agent Barbell</Text>
        <Text variant='note' alignment={TextAlignment.Center}>A risk-budget barbell agent for Robinhood Chain. Connect a wallet to get started.</Text>
        <Spacing variant={PaddingSize.Wide} />
        {account ? (
          <Text variant='bold'>{`Connected: ${account.address.slice(0, 6)}...${account.address.slice(-4)}`}</Text>
        ) : (
          <Button variant='primary' text='Connect Wallet' onClicked={onConnectWalletClicked} />
        )}
      </Stack>
      <ProviderDialog
        isOpen={isProviderDialogOpen}
        providers={web3Providers}
        onProviderSelected={onProviderSelected}
        onSignInWithReownClicked={onSignInWithReownButtonClicked}
        isReownAvailable={isReownInitialized}
        onClose={(): void => setIsProviderDialogOpen(false)}
      />
    </ContainingView>
  );
}
