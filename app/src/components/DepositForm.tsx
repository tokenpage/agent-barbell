import React from 'react';

import { Alignment, Button, Direction, InputType, Link, LoadingSpinner, SingleLineInput, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { parseWeb3Units, useOnSwitchToWeb3ChainIdClicked, useWeb3Account, useWeb3ChainId, useWeb3Transaction, useWeb3WritableContract } from '@kibalabs/web3-react';

import { ROBINHOOD_CHAIN_ID, ROBINHOOD_EXPLORER_URL, USDG_ADDRESS } from '../util/constants';

const ERC20_TRANSFER_ABI = ['function transfer(address to, uint256 amount) public returns (bool)'];
const USDG_DECIMALS = 6;

interface IDepositFormProps {
  agentWalletAddress: string;
  onDepositSuccess: () => void;
}

export function DepositForm(props: IDepositFormProps): React.ReactElement {
  const account = useWeb3Account();
  const chainId = useWeb3ChainId();
  const onSwitchToWeb3ChainIdClicked = useOnSwitchToWeb3ChainIdClicked();
  const [transactionDetails, setTransactionPromise, , clearTransaction] = useWeb3Transaction();
  const writableTokenContract = useWeb3WritableContract({ [ROBINHOOD_CHAIN_ID]: USDG_ADDRESS }, ERC20_TRANSFER_ABI, account?.signer);
  const [amount, setAmount] = React.useState('');

  const amountUnits = React.useMemo((): bigint => {
    try {
      return amount.trim() === '' ? 0n : parseWeb3Units(amount, USDG_DECIMALS);
    } catch {
      return 0n;
    }
  }, [amount]);
  const isAmountValid = amountUnits > 0n;
  const isTransferring = transactionDetails.transactionPromise != null || transactionDetails.transaction != null;
  const isNetworkReady = chainId === ROBINHOOD_CHAIN_ID;

  const onDepositClicked = async (): Promise<void> => {
    if (!account || !writableTokenContract || !isAmountValid || !isNetworkReady) {
      return;
    }
    const transactionPromise = writableTokenContract.transfer(props.agentWalletAddress, amountUnits);
    setTransactionPromise(transactionPromise);
  };
  const onDoneClicked = (): void => {
    clearTransaction();
    props.onDepositSuccess();
  };

  if (transactionDetails.error) {
    return (
      <Stack direction={Direction.Vertical} shouldAddGutters={true} childAlignment={Alignment.Center} isFullWidth={true}>
        <Text variant='error' alignment={TextAlignment.Center}>Deposit failed</Text>
        <Text variant='error' alignment={TextAlignment.Center}>{transactionDetails.errorMessage || transactionDetails.error.message}</Text>
        <Spacing />
        <Button variant='tertiary' text='Try Again' onClicked={clearTransaction} />
      </Stack>
    );
  }

  if (transactionDetails.receipt) {
    return (
      <Stack direction={Direction.Vertical} shouldAddGutters={true} childAlignment={Alignment.Center} isFullWidth={true}>
        <Text variant='success' alignment={TextAlignment.Center}>Deposit successful</Text>
        <Text variant='note' alignment={TextAlignment.Center}>The USDG transfer is confirmed on Robinhood Chain.</Text>
        <Link text='View transaction' target={`${ROBINHOOD_EXPLORER_URL}/tx/${transactionDetails.receipt.hash}`} />
        <Button variant='primary' text='Done' onClicked={onDoneClicked} isFullWidth={true} />
      </Stack>
    );
  }

  if (isTransferring) {
    return (
      <Stack direction={Direction.Vertical} shouldAddGutters={true} childAlignment={Alignment.Center} isFullWidth={true}>
        <Text variant='note' alignment={TextAlignment.Center}>Processing deposit...</Text>
        <LoadingSpinner />
        <Text variant='note' alignment={TextAlignment.Center}>Do not close this page.</Text>
      </Stack>
    );
  }

  if (!isNetworkReady) {
    return (
      <Stack direction={Direction.Vertical} shouldAddGutters={true} childAlignment={Alignment.Center} isFullWidth={true}>
        <Text variant='note' alignment={TextAlignment.Center}>Switch to Robinhood Chain to deposit USDG.</Text>
        <Button variant='primary' text='Switch Network' onClicked={(): Promise<void> => onSwitchToWeb3ChainIdClicked(ROBINHOOD_CHAIN_ID)} isFullWidth={true} />
      </Stack>
    );
  }

  return (
    <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullWidth={true}>
      <Text variant='note'>Amount in USDG</Text>
      <SingleLineInput inputType={InputType.Number} value={amount} onValueChanged={setAmount} placeholderText='0.00' />
      <Button variant='primary' text='Deposit USDG' onClicked={onDepositClicked} isEnabled={isAmountValid && account != null && writableTokenContract != null} isFullWidth={true} />
    </Stack>
  );
}
