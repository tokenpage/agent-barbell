import asyncio
import typing

from core.exceptions import BadRequestException
from core.exceptions import InternalServerErrorException
from core.util import chain_util
from core.web3.eth_client import EncodedCall
from core.web3.eth_client import RestEthClient
from core.web3.eth_client import TransactionFailedException as EthClientTransactionFailedException
from eth_account import Account
from eth_typing import ABI
from eth_typing import HexStr
from web3.types import TxParams
from web3.types import Wei

from agent_barbell.eth_client_manager import EthClientManager

DictStrAny = dict[str, typing.Any]  # type: ignore[explicit-any]
MAX_RETRY_COUNT = 3


class TransactionManager:
    def __init__(self, ethClientManager: EthClientManager, serverPrivateKey: str) -> None:
        self.ethClientManager = ethClientManager
        self.serverPrivateKey = serverPrivateKey
        self.serverAddress = Account.from_key(serverPrivateKey).address
        self.serverTransactionLock = asyncio.Lock()

    def _get_eth_client_for_chain(self, chainId: int) -> RestEthClient:
        return self.ethClientManager.get_regular_client(chainId=chainId)

    async def send_contract_transaction(
        self,
        chainId: int,
        toAddress: str,
        contractAbi: ABI,
        functionName: str,
        arguments: DictStrAny,
    ) -> str:
        callData = chain_util.encode_transaction_data_by_name(contractAbi=contractAbi, functionName=functionName, arguments=arguments)
        return await self.send_transaction(
            chainId=chainId,
            calls=[EncodedCall(toAddress=toAddress, data=callData)],
        )

    async def send_transaction(self, chainId: int, calls: list[EncodedCall]) -> str:
        if len(calls) == 0:
            raise InternalServerErrorException('No calls provided for transaction')
        ethClient = self._get_eth_client_for_chain(chainId=chainId)
        async with self.serverTransactionLock:
            lastTransactionHash: str | None = None
            for call in calls:
                params: TxParams = {
                    'to': chain_util.normalize_address(value=call.toAddress),
                    'from': self.serverAddress,
                    'data': typing.cast(HexStr, call.data),
                    'value': typing.cast(Wei, hex(call.value)),
                }
                baseParams = await ethClient.fill_transaction_params(params=params, fromAddress=self.serverAddress, chainId=chainId)
                for retryCount in range(MAX_RETRY_COUNT):
                    paramsToSend = dict(baseParams)
                    if retryCount > 0:
                        maxPriorityFeePerGas = await ethClient.get_max_priority_fee_per_gas()
                        maxFeePerGas = await ethClient.get_max_fee_per_gas(maxPriorityFeePerGas=maxPriorityFeePerGas)
                        multiplier = 1 + (retryCount * 0.15)
                        paramsToSend['maxPriorityFeePerGas'] = hex(int(maxPriorityFeePerGas * multiplier))
                        paramsToSend['maxFeePerGas'] = hex(int(maxFeePerGas * multiplier))
                    try:
                        signedParams = ethClient.w3.eth.account.sign_transaction(transaction_dict=paramsToSend, private_key=self.serverPrivateKey)
                        lastTransactionHash = await ethClient.send_raw_transaction(transactionData=signedParams.raw_transaction.hex())
                        await ethClient.wait_for_transaction_receipt(transactionHash=lastTransactionHash)
                        break
                    except EthClientTransactionFailedException as exception:
                        raise InternalServerErrorException(f'Transaction failed: {lastTransactionHash}') from exception
                    except BadRequestException as exception:
                        message = exception.message or ''
                        isStaleFeeError = 'max fee per gas less than block base fee' in message or 'replacement transaction underpriced' in message
                        if not isStaleFeeError or retryCount >= MAX_RETRY_COUNT - 1:
                            raise
                else:
                    raise InternalServerErrorException('Transaction retries exhausted')
            if lastTransactionHash is None:
                raise InternalServerErrorException('No transaction was sent')
            return lastTransactionHash
