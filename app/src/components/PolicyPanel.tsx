import React from 'react';

import { Alignment, Direction, Link, Stack, Text } from '@kibalabs/ui-react';

import { Resources } from '../client';
import { ROBINHOOD_EXPLORER_URL } from '../util/constants';

interface IPolicyPanelProps {
  policy: Resources.RiskPolicy | undefined;
}

export function PolicyPanel(props: IPolicyPanelProps): React.ReactElement | null {
  if (props.policy == null) {
    return null;
  }
  const { policy } = props;
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={true}>
      <Text variant='bold'>Active policy</Text>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Text variant='note'>Loss budget from peak</Text>
        </Stack.Item>
        <Text>{`${(policy.maxDrawdownBps / 100).toFixed(2)}%`}</Text>
      </Stack>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Text variant='note'>Satellite target / cap</Text>
        </Stack.Item>
        <Text>{`${(policy.targetSatelliteBps / 100).toFixed(1)}% / ${(policy.maxSatelliteBps / 100).toFixed(1)}%`}</Text>
      </Stack>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Text variant='note'>Kill switch</Text>
        </Stack.Item>
        <Text>{policy.isKilled ? 'Triggered' : 'Armed'}</Text>
      </Stack>
      {policy.transactionHash ? (
        <Link target={`${ROBINHOOD_EXPLORER_URL}/tx/${policy.transactionHash}`} text='View the on-chain policy record' />
      ) : (
        <Text variant='note'>Not yet published to RiskBudgetRegistry — the policy drives the engine but is not publicly verifiable until it is written on-chain.</Text>
      )}
    </Stack>
  );
}
