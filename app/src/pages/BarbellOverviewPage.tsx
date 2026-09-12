import React from 'react';

import { useNavigator } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, LoadingSpinner, PaddingSize, Stack, Text } from '@kibalabs/ui-react';

import { useBarbell } from '../BarbellContext';
import { CreateBarbellForm } from '../components/CreateBarbellForm';
import { PolicyPanel } from '../components/PolicyPanel';
import { PortfolioView } from '../components/PortfolioView';
import { RiskStateView } from '../components/RiskStateView';

export function BarbellOverviewPage(): React.ReactElement {
  const navigator = useNavigator();
  const { barbell, portfolio, riskState, isLoading, error, deactivationError, deactivateBarbell } = useBarbell();
  const [isConfirmingDeactivation, setIsConfirmingDeactivation] = React.useState(false);
  const deactivationErrorMessage = deactivationError?.message === 'AGENT_HAS_BAR_BELL_HOLDINGS'
    ? 'Move all anchor and satellite holdings out before deactivating this agent.'
    : deactivationError?.message;

  const onFundClicked = React.useCallback((): void => {
    navigator.navigateTo('/barbell/fund');
  }, [navigator]);

  const onChatClicked = React.useCallback((): void => {
    navigator.navigateTo('/barbell/chat');
  }, [navigator]);
  const onDeactivateClicked = React.useCallback((): void => {
    setIsConfirmingDeactivation(true);
  }, []);
  const onDeactivateConfirmed = React.useCallback(async (): Promise<void> => {
    try {
      await deactivateBarbell();
    } catch {
      setIsConfirmingDeactivation(false);
    }
  }, [deactivateBarbell]);

  if (isLoading) {
    return (
      <ContainingView maxWidth='640px' className='ab-page'>
        <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isFullHeight={true} paddingVertical={PaddingSize.Wide2}>
          <LoadingSpinner />
        </Stack>
      </ContainingView>
    );
  }

  if (barbell == null) {
    return <CreateBarbellForm error={error?.message ?? null} />;
  }

  return (
    <ContainingView maxWidth='640px' className='ab-page'>
      <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullWidth={true} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
        <Text variant='header2'>{barbell.name}</Text>
        <Text variant='note'>{`Wallet ${barbell.walletAddress}${barbell.isWalletDeployed ? '' : ' (not yet deployed — fundable, deploys on first agent action)'}`}</Text>
        <Box variant='card' isFullWidth={true}>
          <RiskStateView riskState={riskState} />
        </Box>
        <Box variant='card' isFullWidth={true}>
          <PortfolioView portfolio={portfolio} />
        </Box>
        <Box variant='card' isFullWidth={true}>
          <PolicyPanel policy={riskState?.policy} />
        </Box>
        <Button variant='primary' text='Talk to your agent' onClicked={onChatClicked} />
        <Button variant='secondary' text='Fund this barbell' onClicked={onFundClicked} />
        {isConfirmingDeactivation ? (
          <Box variant='card' isFullWidth={true}>
            <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullWidth={true}>
              <Text variant='note'>Deactivate only after both anchor and satellite holdings are empty.</Text>
              <Button variant='tertiary' text='Cancel' onClicked={(): void => setIsConfirmingDeactivation(false)} />
              <Button variant='secondary' text='Deactivate agent' onClicked={onDeactivateConfirmed} />
            </Stack>
          </Box>
        ) : (
          <Button variant='tertiary' text='Deactivate agent' onClicked={onDeactivateClicked} />
        )}
        {deactivationErrorMessage && <Text variant='note-error'>{deactivationErrorMessage}</Text>}
      </Stack>
    </ContainingView>
  );
}
