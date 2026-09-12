import React from 'react';

import { Alignment, Box, Button, Dialog, Direction, getVariant, Image, KibaIcon, PaddingSize, SelectableView, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { Eip6963ProviderDetail, useIsReownInitialized, useOnLinkWeb3AccountsClicked, useWeb3Account, useWeb3LoginSignature, useWeb3OnLoginClicked, useWeb3OnReownLoginClicked, useWeb3Providers } from '@kibalabs/web3-react';

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
function BarbellDiagram(): React.ReactElement {
  return (
    <div className='ab-barbell-diagram' aria-label='The agent moves capital between an anchor and a satellite'>
      <div className='ab-leg'>
        <div className='ab-token-mark anchor'>SGOV</div>
        <div>
          <div className='ab-leg-label anchor'>Anchor</div>
          <div className='ab-leg-copy'>Tokenized short treasuries</div>
        </div>
      </div>
      <div className='ab-track'>
        <div className='ab-track-line' />
        <div className='ab-flow ab-flow-out' aria-hidden='true'>
          <span className='ab-flow-dot' />
          <span className='ab-flow-dot' />
          <span className='ab-flow-dot' />
          <span className='ab-flow-dot' />
        </div>
        <div className='ab-flow ab-flow-back' aria-hidden='true'>
          <span className='ab-flow-dot' />
          <span className='ab-flow-dot' />
          <span className='ab-flow-dot' />
          <span className='ab-flow-dot' />
        </div>
        <div className='ab-spike'>volatility spike · 68% → 143%</div>
        <div className='ab-track-caption'>
          <span className='ab-track-caption-out'>capital moving out to the satellite →</span>
          <span className='ab-track-caption-back'>← agent pulling it back to the anchor</span>
        </div>
      </div>
      <div className='ab-leg'>
        <div className='ab-token-mark satellite'>GME</div>
        <div>
          <div className='ab-leg-label satellite'>Satellite</div>
          <div className='ab-leg-copy'>Volatile upside, sized down when vol spikes</div>
        </div>
      </div>
    </div>
  );
}

export function HomePage(): React.ReactElement {
  const account = useWeb3Account();
  const [web3Providers, chooseEip1193Provider] = useWeb3Providers();
  const onLinkAccountsClicked = useOnLinkWeb3AccountsClicked();
  const onSignInWithReownClicked = useWeb3OnReownLoginClicked();
  const isReownInitialized = useIsReownInitialized();
  const onLoginClicked = useWeb3OnLoginClicked();
  const loginSignature = useWeb3LoginSignature();
  const [isProviderDialogOpen, setIsProviderDialogOpen] = React.useState(false);
  const [signInError, setSignInError] = React.useState<string | null>(null);

  const onSignInClicked = React.useCallback(async (): Promise<void> => {
    setSignInError(null);
    try {
      await onLoginClicked('Sign in to Agent Barbell');
    } catch (error: unknown) {
      setSignInError((error as Error).message);
    }
  }, [onLoginClicked]);

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
    <div className='ab-home'>
      <section className='ab-hero'>
        <img className='ab-hero-icon' src='/assets/icon.svg' alt='Agent Barbell mark' />
        <Text variant='note' className='ab-eyebrow'>Robinhood Chain · 4663 · mainnet</Text>
        <Text variant='header1' className='ab-display'>
          Own both ends.
          <br />
          The agent sizes them.
        </Text>
        <Text variant='note' className='ab-lede'>
          Treasuries on one end, stocks on the other, both native to Robinhood Chain. You set the limit you want defended. The agent decides when the volatile end is too big and acts on its own.
        </Text>
      </section>

      <BarbellDiagram />

      <section className='ab-home-cta'>
        {!account && (
          <Button variant='primary-large' text='Connect wallet' onClicked={onConnectWalletClicked} />
        )}
        {account && !loginSignature && (
          <div className='ab-auth-card'>
            <Text variant='bold'>{`Connected: ${account.address.slice(0, 6)}...${account.address.slice(-4)}`}</Text>
            <Text variant='note' alignment={TextAlignment.Center}>Sign a message to prove you own this wallet. No transaction, no gas.</Text>
            <Button variant='primary' text='Sign in' onClicked={onSignInClicked} />
          </div>
        )}
        {account && loginSignature && (
          <Text variant='bold'>Signing you in…</Text>
        )}
        {signInError && <Text variant='note-error'>{signInError}</Text>}
        <Text variant='note' className='ab-trust-note'>non-custodial · withdraw whenever you like</Text>
      </section>

      <section className='ab-built-on' aria-label='Built on'>
        <div className='ab-built-on-label'>Built on</div>
        <div className='ab-built-on-items'>
          <span>The Graph</span>
          <span>Uniswap v3</span>
          <span>AgentWalletKit</span>
          <span>Ledger Key Ring</span>
          <span>MCP</span>
        </div>
      </section>
      <section className='ab-home-steps' aria-label='How Agent Barbell works'>
        <div className='ab-home-step'>
          <div className='ab-step-number'>01</div>
          <h2>Tell it what to defend</h2>
          <p>One sentence in chat becomes a bounded policy on-chain — the limits the agent has to work inside.</p>
        </div>
        <div className='ab-home-step'>
          <div className='ab-step-number'>02</div>
          <h2>It watches and decides</h2>
          <p>Realized volatility and momentum guide decisions when the position drifts out of line, not on a clock.</p>
        </div>
        <div className='ab-home-step'>
          <div className='ab-step-number'>03</div>
          <h2>It defends without asking</h2>
          <p>At your limit the satellite goes to zero and the event lands on-chain. Only you can re-arm it.</p>
        </div>
      </section>

      <ProviderDialog
        isOpen={isProviderDialogOpen}
        providers={web3Providers}
        onProviderSelected={onProviderSelected}
        onSignInWithReownClicked={onSignInWithReownButtonClicked}
        isReownAvailable={isReownInitialized}
        onClose={(): void => setIsProviderDialogOpen(false)}
      />
    </div>
  );
}
