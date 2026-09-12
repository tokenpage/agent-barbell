import React from 'react';

import { Alignment, Box, Button, ContainingView, Direction, PaddingSize, SelectableView, SingleLineInput, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { useBarbell } from '../BarbellContext';
import { CreateBarbellConfig } from '../client';
import { BarbellAsset } from '../client/resources';
import { ROBINHOOD_CHAIN_ID } from '../util/constants';
import { useBarbellAssetsQuery } from '../util/useBarbellAssetsQuery';
import { BarbellAssetOptionSelect } from './BarbellAssetOptionSelect';
import { CreateBarbellDiscuss } from './CreateBarbellDiscuss';

const AGENT_NAME_MIN_LENGTH = 3;
const AGENT_NAME_MAX_LENGTH = 30;
const AGENT_NAME_REGEX = /^[A-Za-z0-9 ._&$'-]+$/;

interface IRiskBudgetPreset {
  name: string;
  description: string;
  maxDrawdownBps: number;
  targetSatelliteBps: number;
  maxSatelliteBps: number;
}

const RISK_BUDGET_PRESETS: IRiskBudgetPreset[] = [
  { name: 'Conservative', description: 'Never lose more than 10% from peak', maxDrawdownBps: 1000, targetSatelliteBps: 1000, maxSatelliteBps: 2000 },
  { name: 'Balanced', description: 'Never lose more than 15% from peak', maxDrawdownBps: 1500, targetSatelliteBps: 2000, maxSatelliteBps: 4000 },
  { name: 'Aggressive', description: 'Never lose more than 25% from peak', maxDrawdownBps: 2500, targetSatelliteBps: 3500, maxSatelliteBps: 6000 },
];

interface CreateBarbellFormProps {
  error: string | null;
}

export function CreateBarbellForm(props: CreateBarbellFormProps): React.ReactElement {
  const { createBarbell } = useBarbell();
  const { data: loadedAssets, isLoading: areAssetsLoading, error: assetsError } = useBarbellAssetsQuery(ROBINHOOD_CHAIN_ID);
  const [agentName, setAgentName] = React.useState<string>('');
  const [selectedSatelliteAssetAddress, setSelectedSatelliteAssetAddress] = React.useState<string>('');
  const [selectedPreset, setSelectedPreset] = React.useState<IRiskBudgetPreset>(RISK_BUDGET_PRESETS[1]);
  const [validationError, setValidationError] = React.useState<string | null>(null);
  const [isCreating, setIsCreating] = React.useState<boolean>(false);

  const assets = loadedAssets ?? [];
  const safeAssets = assets.filter((asset: BarbellAsset): boolean => asset.isAnchor);
  const satelliteAssets = assets.filter((asset: BarbellAsset): boolean => !asset.isAnchor);
  const safeAssetAddress = safeAssets[0]?.address ?? '';
  const selectedSatelliteAsset = satelliteAssets.find((asset: BarbellAsset): boolean => asset.address === selectedSatelliteAssetAddress);

  React.useEffect((): void => {
    const defaultSatelliteAsset = satelliteAssets.find((asset: BarbellAsset): boolean => asset.symbol.toUpperCase() === 'GME') ?? satelliteAssets[0];
    if (defaultSatelliteAsset != null && !satelliteAssets.some((asset: BarbellAsset): boolean => asset.address === selectedSatelliteAssetAddress)) {
      setSelectedSatelliteAssetAddress(defaultSatelliteAsset.address);
    }
  }, [satelliteAssets, selectedSatelliteAssetAddress]);

  const config = React.useMemo((): CreateBarbellConfig => ({
    name: agentName.trim(),
    satelliteAssetAddress: selectedSatelliteAssetAddress,
    maxDrawdownBps: selectedPreset.maxDrawdownBps,
    targetSatelliteBps: selectedPreset.targetSatelliteBps,
    maxSatelliteBps: selectedPreset.maxSatelliteBps,
  }), [agentName, selectedSatelliteAssetAddress, selectedPreset]);

  const onAgentNameChanged = (value: string): void => {
    setAgentName(value);
    setValidationError(null);
  };

  const onCreateClicked = async (): Promise<void> => {
    const normalizedName = agentName.trim();
    if (!normalizedName) {
      setValidationError('Please enter a name for your barbell.');
      return;
    }
    if (normalizedName.length < AGENT_NAME_MIN_LENGTH) {
      setValidationError(`Name must be at least ${AGENT_NAME_MIN_LENGTH} characters long.`);
      return;
    }
    if (normalizedName.length > AGENT_NAME_MAX_LENGTH) {
      setValidationError(`Name must be at most ${AGENT_NAME_MAX_LENGTH} characters long.`);
      return;
    }
    if (!AGENT_NAME_REGEX.test(normalizedName)) {
      setValidationError('Name can only contain letters, numbers, spaces, and . _ - & $.');
      return;
    }
    if (!selectedSatelliteAssetAddress) {
      setValidationError('Choose a stock for the satellite end.');
      return;
    }
    setValidationError(null);
    setIsCreating(true);
    console.info('[CreateBarbellForm] create:start', config);
    try {
      const barbell = await createBarbell(config);
      console.info('[CreateBarbellForm] create:success', { barbellId: barbell.barbellId });
    } catch (caughtError: unknown) {
      console.error('[CreateBarbellForm] create:failed', caughtError);
      setValidationError(caughtError instanceof Error ? caughtError.message : 'Failed to create your barbell.');
      setIsCreating(false);
    }
  };

  const displayedError = validationError ?? props.error;
  if (isCreating) {
    return (
      <ContainingView maxWidth='760px' className='ab-page ab-create-page'>
        <div className='ab-creation-progress' role='status' aria-live='polite'>
          <div className='ab-creation-progress-barbell' aria-hidden='true'>
            <div className='ab-creation-progress-token anchor'>{safeAssets[0]?.symbol ?? 'SAFE'}</div>
            <div className='ab-creation-progress-beam'>
              <div className='ab-creation-progress-beam-line' />
              <span className='ab-creation-progress-pulse' />
              <span className='ab-creation-progress-pulse' />
              <span className='ab-creation-progress-pulse' />
            </div>
            <div className='ab-creation-progress-token satellite'>{selectedSatelliteAsset?.symbol ?? 'STOCK'}</div>
          </div>
          <Text variant='header1' className='ab-creation-progress-title'>{`Creating ${agentName.trim()}`}</Text>
          <Text className='ab-creation-progress-copy'>Deploying the wallet, connecting both legs, and applying your strategy.</Text>
          <div className='ab-creation-progress-status' aria-hidden='true'>
            <span />
            <span />
            <span />
          </div>
        </div>
      </ContainingView>
    );
  }


  return (
    <ContainingView maxWidth='760px' className='ab-page ab-create-page'>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Fill} isFullWidth={true} shouldAddGutters={true}>
        <Text variant='header1'>Create your agent</Text>
        <Text>Give your agent a name, choose the two ends, and set the strategy it should defend.</Text>
        <Spacing variant={PaddingSize.Wide} />

          <Text>Agent name</Text>
          <SingleLineInput
            label='Agent name'
            value={agentName}
            onValueChanged={onAgentNameChanged}
            placeholderText='e.g. Alpha Agent'
          />

          <Spacing/>
          {areAssetsLoading && <Text variant='note'>Loading supported assets…</Text>}
          {assetsError && <Text variant='note-error'>Unable to load supported assets.</Text>}
          <Text>Safe end</Text>
          <BarbellAssetOptionSelect
            assets={safeAssets}
            selectedAssetAddress={safeAssetAddress}
            isDisabled={true}
            placeholderText='Safe asset unavailable'
          />
          <Text variant='note'>The safe end is fixed by the API's anchor asset configuration.</Text>
        
        <Spacing/>
          <Text>Satellite end</Text>
          <BarbellAssetOptionSelect
            assets={satelliteAssets}
            selectedAssetAddress={selectedSatelliteAssetAddress}
            isDisabled={areAssetsLoading || assetsError != null || satelliteAssets.length === 0}
            onAssetSelected={setSelectedSatelliteAssetAddress}
            placeholderText='Choose a stock token'
          />
          <Text variant='note'>Choose a supported stock token for upside and volatility.</Text>

          <Spacing/>
          <Text>Strategy settings</Text>
          <Text variant='note'>The loss budget is measured from the portfolio peak. The engine uses it to scale or cut the satellite leg.</Text>
          <div className='ab-create-strategy'>
            <Stack className='ab-risk-budget-selector' direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={true}>
              {RISK_BUDGET_PRESETS.map((preset: IRiskBudgetPreset): React.ReactElement => (
                <Box key={preset.name} isFullWidth={true}>
                  <SelectableView
                    onClicked={(): void => setSelectedPreset(preset)}
                    isSelected={selectedPreset.maxDrawdownBps === preset.maxDrawdownBps}
                    isFullWidth={true}
                  >
                    <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} shouldAddGutters={false} paddingHorizontal={PaddingSize.Default} paddingVertical={PaddingSize.Narrow}>
                      <Text variant='bold'>{preset.name}</Text>
                      <Text variant='note'>{preset.description}</Text>
                      <Text variant='note'>{`Satellite target ${preset.targetSatelliteBps / 100}%, capped at ${preset.maxSatelliteBps / 100}%`}</Text>
                    </Stack>
                  </SelectableView>
                </Box>
              ))}
            </Stack>
          </div>

          <Spacing/>
          <CreateBarbellDiscuss config={config} />

        {displayedError && <Text variant='error'>{displayedError}</Text>}
        <Button
          variant='primary'
          text={isCreating ? 'Creating…' : 'Create barbell agent'}
          onClicked={onCreateClicked}
          isEnabled={!isCreating && selectedSatelliteAssetAddress.length > 0 && safeAssets.length > 0 && !areAssetsLoading && assetsError == null}
          isFullWidth={true}
        />
      </Stack>
    </ContainingView>
  );
}
