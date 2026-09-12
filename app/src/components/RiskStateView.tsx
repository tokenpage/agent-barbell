import React from 'react';

import { Alignment, Box, Direction, LoadingSpinner, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { Resources } from '../client';

interface IStatProps {
  label: string;
  value: string;
  note?: string;
}

function Stat(props: IStatProps): React.ReactElement {
  return (
    <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} shouldAddGutters={false}>
      <Text variant='note' alignment={TextAlignment.Center}>{props.label}</Text>
      <Text variant='bold' alignment={TextAlignment.Center}>{props.value}</Text>
      {props.note && <Text variant='note' alignment={TextAlignment.Center}>{props.note}</Text>}
    </Stack>
  );
}

interface IRiskStateViewProps {
  riskState: Resources.RiskState | undefined;
}

export function RiskStateView(props: IRiskStateViewProps): React.ReactElement {
  if (props.riskState == null) {
    return (
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isFullWidth={true} paddingVertical={PaddingSize.Wide2}>
        <LoadingSpinner />
      </Stack>
    );
  }
  const { riskState } = props;
  const budgetUsedPercent = riskState.policy.maxDrawdownBps > 0 ? Math.min(100, (riskState.drawdownBps / riskState.policy.maxDrawdownBps) * 100) : 0;
  const barColor = riskState.isKillSwitchTriggered ? '#e0603a' : '#3ba55d';
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={true}>
      <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={false}>
        <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center}>
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            <Text variant='bold'>Drawdown against your budget</Text>
          </Stack.Item>
          <Text variant='bold'>{`${(riskState.drawdownBps / 100).toFixed(2)}% of ${(riskState.policy.maxDrawdownBps / 100).toFixed(2)}%`}</Text>
        </Stack>
        <Box height='0.75rem' width='100%' variant='rounded' isFullWidth={true}>
          <div style={{ width: `${Math.max(1, budgetUsedPercent)}%`, height: '100%', background: barColor, borderRadius: '0.375rem' }} />
        </Box>
      </Stack>
      <Stack direction={Direction.Horizontal} isFullWidth={true} contentAlignment={Alignment.Fill} shouldAddGutters={true}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Stat label='Realized vol' value={`${(riskState.volatility * 100).toFixed(1)}%`} />
        </Stack.Item>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Stat label='Momentum' value={`${(riskState.momentum * 100).toFixed(2)}%`} />
        </Stack.Item>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Stat label='Satellite' value={`${(riskState.currentSatelliteBps / 100).toFixed(1)}%`} note={`target ${(riskState.targetSatelliteBps / 100).toFixed(1)}%`} />
        </Stack.Item>
      </Stack>
      <Text variant='note'>{riskState.decisionTrace}</Text>
    </Stack>
  );
}
