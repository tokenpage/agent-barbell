import React from 'react';

import { Alignment, Box, Direction, LoadingSpinner, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { Resources } from '../client';

const usdFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 });

interface ILegRowProps {
  label: string;
  leg: Resources.LegBalance;
  totalValueUsd: number;
  color: string;
}

function LegRow(props: ILegRowProps): React.ReactElement {
  const sharePercent = props.totalValueUsd > 0 ? (props.leg.valueUsd / props.totalValueUsd) * 100 : 0;
  const balance = Number(props.leg.balance) / (10 ** props.leg.decimals);
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={false}>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Text variant='bold'>{`${props.label} · ${props.leg.symbol}`}</Text>
        </Stack.Item>
        <Text variant='bold'>{usdFormatter.format(props.leg.valueUsd)}</Text>
      </Stack>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Text variant='note'>{`${balance.toLocaleString('en-US', { maximumFractionDigits: 4 })} @ ${usdFormatter.format(props.leg.priceUsd)}`}</Text>
        </Stack.Item>
        <Text variant='note'>{`${sharePercent.toFixed(1)}%`}</Text>
      </Stack>
      <Box height='0.5rem' width='100%' variant='rounded' isFullWidth={true}>
        <div style={{ width: `${Math.max(1, sharePercent)}%`, height: '100%', background: props.color, borderRadius: '0.25rem' }} />
      </Box>
    </Stack>
  );
}

interface IPortfolioViewProps {
  portfolio: Resources.Portfolio | undefined;
}

export function PortfolioView(props: IPortfolioViewProps): React.ReactElement {
  if (props.portfolio == null) {
    return (
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isFullWidth={true} paddingVertical={PaddingSize.Wide2}>
        <LoadingSpinner />
      </Stack>
    );
  }
  const { portfolio } = props;
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={true}>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isFullWidth={true}>
        <Text variant='note' alignment={TextAlignment.Center}>Total value</Text>
        <Text variant='header2' alignment={TextAlignment.Center}>{usdFormatter.format(portfolio.totalValueUsd)}</Text>
        <Text variant='note' alignment={TextAlignment.Center}>{`Satellite is ${(portfolio.satelliteBps / 100).toFixed(2)}% of the book`}</Text>
      </Stack>
      <LegRow label='Anchor' leg={portfolio.anchor} totalValueUsd={portfolio.totalValueUsd} color='#3ba55d' />
      <LegRow label='Satellite' leg={portfolio.satellite} totalValueUsd={portfolio.totalValueUsd} color='#e0603a' />
      <LegRow label='Cash' leg={portfolio.cash} totalValueUsd={portfolio.totalValueUsd} color='#7a7f87' />
    </Stack>
  );
}
