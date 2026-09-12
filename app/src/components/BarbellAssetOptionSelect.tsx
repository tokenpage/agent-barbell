import React from 'react';

import { getClassName } from '@kibalabs/core';
import { Alignment, Box, Direction, HidingView, IComponentProps, IListItemProps, Image, InputFrame, KibaIcon, List, Stack, Text } from '@kibalabs/ui-react';

import { BarbellAsset } from '../client/resources';

import './BarbellAssetOptionSelect.scss';

interface AssetItemViewProps {
  asset: BarbellAsset;
}

function AssetItemView(props: AssetItemViewProps): React.ReactElement {
  return (
    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
      {props.asset.logoUri != null && (
        <Image source={props.asset.logoUri} alternativeText={props.asset.symbol} width='1.5rem' height='1.5rem' />
      )}
      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Baseline} contentAlignment={Alignment.Start} shouldAddGutters={true}>
        <Text>{props.asset.symbol}</Text>
        <Text variant='note'>{props.asset.name}</Text>
      </Stack>
    </Stack>
  );
}

interface BarbellAssetOptionSelectProps extends IComponentProps {
  assets: BarbellAsset[];
  selectedAssetAddress?: string;
  isDisabled?: boolean;
  placeholderText?: string;
  onAssetSelected?: (assetAddress: string) => void;
}

export function BarbellAssetOptionSelect(props: BarbellAssetOptionSelectProps): React.ReactElement {
  const [isOpen, setIsOpen] = React.useState<boolean>(false);
  const selectedAsset = props.assets.find((asset: BarbellAsset): boolean => asset.address.toLowerCase() === props.selectedAssetAddress?.toLowerCase());

  const onItemClicked = (itemKey: string): void => {
    props.onAssetSelected?.(itemKey);
    setIsOpen(false);
  };

  return (
    <div
      id={props.id}
      className={getClassName(BarbellAssetOptionSelect.displayName, props.className ?? '')}
      style={props.style}
    >
      <InputFrame
        onClicked={(): void => setIsOpen((current: boolean): boolean => !current)}
        isEnabled={!props.isDisabled}
      >
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} shouldAddGutters={true}>
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            {selectedAsset != null ? <AssetItemView asset={selectedAsset} /> : <Text>{props.placeholderText ?? 'Select an asset'}</Text>}
          </Stack.Item>
          <KibaIcon iconId={isOpen ? 'ion-close' : 'ion-chevron-down'} />
        </Stack>
      </InputFrame>
      <HidingView isHidden={!isOpen}>
        <Box variant='card-unpadded-unmargined' maxHeight='300px' zIndex={999} isFullWidth={true} position='absolute' isScrollableVertically={true}>
          <List itemVariant='slim' onItemClicked={onItemClicked} shouldShowDividers={true} isFullWidth={true}>
            {props.assets.map((asset: BarbellAsset): React.ReactElement<IListItemProps> => (
              <List.Item key={asset.address} itemKey={asset.address}>
                <AssetItemView asset={asset} />
              </List.Item>
            ))}
          </List>
        </Box>
      </HidingView>
    </div>
  );
}

BarbellAssetOptionSelect.displayName = 'KibaBarbellAssetOptionSelect';
