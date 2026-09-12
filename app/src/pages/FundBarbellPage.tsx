import React from 'react';

import { useNavigator } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { useBarbell } from '../BarbellContext';
import { DepositForm } from '../components/DepositForm';
import { ASSET_SYMBOL_MAP, ROBINHOOD_CHAIN_ID, ROBINHOOD_EXPLORER_URL, USDG_ADDRESS } from '../util/constants';

export function FundBarbellPage(): React.ReactElement {
  const navigator = useNavigator();
  const { barbell, refresh } = useBarbell();
  const [hasCopied, setHasCopied] = React.useState(false);

  const onCopyClicked = React.useCallback(async (): Promise<void> => {
    if (barbell == null) {
      return;
    }
    await window.navigator.clipboard.writeText(barbell.walletAddress);
    setHasCopied(true);
  }, [barbell]);

  const onDoneClicked = React.useCallback((): void => {
    refresh();
    navigator.navigateTo('/barbell/overview');
  }, [navigator, refresh]);

  if (barbell == null) {
    return (
      <ContainingView maxWidth='640px' className='ab-page'>
        <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} paddingVertical={PaddingSize.Wide2}>
          <Text alignment={TextAlignment.Center}>Create a barbell first.</Text>
        </Stack>
      </ContainingView>
    );
  }

  return (
    <ContainingView maxWidth='640px' className='ab-page'>
      <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullWidth={true} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
        <Text variant='header2'>Fund your barbell</Text>
        <Text variant='note'>
          {`Send ${ASSET_SYMBOL_MAP[USDG_ADDRESS]} on Robinhood Chain (chain ${ROBINHOOD_CHAIN_ID}) to the address below. The agent buys both legs from this balance.`}
        </Text>
        <Box variant='card' isFullWidth={true}>
          <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullWidth={true}>
            <Text variant='note'>Your barbell wallet</Text>
            <Text variant='bold'>{barbell.walletAddress}</Text>
            <Button variant='secondary' text={hasCopied ? 'Copied' : 'Copy address'} onClicked={onCopyClicked} />
          </Stack>
        </Box>
        <Text variant='note'>
          {barbell.isWalletDeployed
            ? 'This wallet is deployed on-chain.'
            : 'Wallet deployment is pending. Refresh before sending funds.'}
        </Text>
        <Box variant='card' isFullWidth={true}>
          <DepositForm agentWalletAddress={barbell.walletAddress} onDepositSuccess={onDoneClicked} />
        </Box>
        <Text variant='note'>{`Track it on ${ROBINHOOD_EXPLORER_URL}`}</Text>
      </Stack>
    </ContainingView>
  );
}
