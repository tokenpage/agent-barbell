import React from 'react';

import { Alignment, ContainingView, Direction, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { useAuth } from '../AuthContext';

export function DashboardPage(): React.ReactElement {
  const { user } = useAuth();

  return (
    <ContainingView maxWidth='600px'>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} isFullHeight={true} isFullWidth={true} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
        <Text variant='header1' alignment={TextAlignment.Center}>Barbell Dashboard</Text>
        <Text variant='note' alignment={TextAlignment.Center}>{`Signed in as ${user?.username || user?.walletAddress}. Risk-budget barbell controls land in a later phase.`}</Text>
      </Stack>
    </ContainingView>
  );
}
