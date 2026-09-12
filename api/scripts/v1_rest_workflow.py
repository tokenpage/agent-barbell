# ruff: noqa: T201
"""Drive the whole v1 REST surface with a throwaway SIWE-signed wallet.

Proves auth, barbell creation, portfolio pricing and risk state end to end without a browser:
    cd api && direnv exec . uv run --active python scripts/v1_rest_workflow.py [apiUrl]
"""

import asyncio
import base64
import json
import sys
import uuid

from core.requester import Requester
from core.util import date_util
from eth_account import Account
from eth_account.messages import encode_defunct

import _path_fix  # type: ignore[import-not-found]  # noqa: F401

DEFAULT_API_URL = 'http://127.0.0.1:5100'
DEFAULT_DOMAIN = '127.0.0.1:3100'
HTTP_OK = 200


def _build_auth_token(privateKey: str, address: str, domain: str) -> str:
    issuedAt = date_util.datetime_to_string(dt=date_util.datetime_from_now()).replace(' ', 'T')
    message = f'{domain} wants you to sign in with your Ethereum account:\n{address}\n\nSign in to Agent Barbell\n\nURI: http://{domain}\nVersion: 1\nChain ID: 4663\nNonce: {uuid.uuid4().hex[:16]}\nIssued At: {issuedAt}Z'
    signature = Account.sign_message(encode_defunct(text=message), private_key=privateKey).signature.hex()
    if not signature.startswith('0x'):
        signature = f'0x{signature}'
    return base64.b64encode(json.dumps({'message': message, 'signature': signature}).encode('utf-8')).decode('utf-8')


async def do_stuff(apiUrl: str, domain: str) -> None:
    requester = Requester()
    account = Account.create()
    authToken = _build_auth_token(privateKey=account.key.hex(), address=account.address, domain=domain)
    authHeaders = {'Content-Type': 'application/json', 'Authorization': f'Signature {authToken}'}
    results: list[bool] = []

    def _check(description: str, isOk: bool, detail: str = '') -> None:
        print(f'{"PASS" if isOk else "FAIL"}  {description}{f" — {detail}" if detail else ""}')
        results.append(isOk)

    print(f'=== signing in as {account.address} ===')
    createUserResponse = await requester.post_json(url=f'{apiUrl}/v1/users', dataDict={'walletAddress': account.address, 'username': None, 'signatureString': authToken})
    _check('POST /v1/users creates a user', createUserResponse.status_code == HTTP_OK, str(createUserResponse.status_code))
    loginResponse = await requester.post_json(url=f'{apiUrl}/v1/logins', dataDict={}, headers=authHeaders)
    _check('POST /v1/logins authenticates', loginResponse.status_code == HTTP_OK, str(loginResponse.status_code))

    print('=== barbell ===')
    emptyBarbellResponse = await requester.get(url=f'{apiUrl}/v1/barbells', headers=authHeaders)
    _check('GET /v1/barbells is empty before creation', emptyBarbellResponse.json()['barbell'] is None)
    createBarbellResponse = await requester.post_json(url=f'{apiUrl}/v1/barbells', dataDict={}, headers=authHeaders)
    _check('POST /v1/barbells creates a barbell', createBarbellResponse.status_code == HTTP_OK, str(createBarbellResponse.status_code))
    barbell = createBarbellResponse.json()['barbell']
    barbellId = barbell['barbellId']
    print(f'      wallet={barbell["walletAddress"]} deployed={barbell["isWalletDeployed"]}')
    _check('the wallet address is counterfactual, not zero', barbell['walletAddress'] != '0x0000000000000000000000000000000000000000')

    print('=== portfolio ===')
    portfolioResponse = await requester.get(url=f'{apiUrl}/v1/barbells/{barbellId}/portfolio', headers=authHeaders)
    _check('GET portfolio succeeds', portfolioResponse.status_code == HTTP_OK, str(portfolioResponse.status_code))
    portfolio = portfolioResponse.json()['portfolio']
    print(f'      total=${portfolio["totalValueUsd"]:,.2f} anchor={portfolio["anchor"]["symbol"]}@${portfolio["anchor"]["priceUsd"]:,.2f} satellite={portfolio["satellite"]["symbol"]}@${portfolio["satellite"]["priceUsd"]:,.2f}')
    _check('anchor is priced from a live pool', portfolio['anchor']['priceUsd'] > 0)
    _check('satellite is priced from a live pool', portfolio['satellite']['priceUsd'] > 0)

    print('=== risk state ===')
    riskStateResponse = await requester.get(url=f'{apiUrl}/v1/barbells/{barbellId}/risk-state', headers=authHeaders)
    _check('GET risk-state succeeds', riskStateResponse.status_code == HTTP_OK, str(riskStateResponse.status_code))
    riskState = riskStateResponse.json()['riskState']
    print(f'      {riskState["decisionTrace"]}')
    _check('a default policy is applied', riskState['policy']['maxDrawdownBps'] > 0)

    print('=== set risk budget ===')
    setBudgetResponse = await requester.post_json(url=f'{apiUrl}/v1/barbells/{barbellId}/risk-budget', dataDict={'maxDrawdownBps': 2500, 'targetSatelliteBps': 3500, 'maxSatelliteBps': 6000}, headers=authHeaders)
    _check('POST risk-budget succeeds', setBudgetResponse.status_code == HTTP_OK, str(setBudgetResponse.status_code))
    updatedPolicy = setBudgetResponse.json()['riskState']['policy']
    _check('the new budget is persisted', updatedPolicy['maxDrawdownBps'] == 2500, str(updatedPolicy))  # noqa: PLR2004
    _check('the policy is not yet published on-chain', updatedPolicy['transactionHash'] is None)

    print('=== snapshots and actions ===')
    snapshotsResponse = await requester.get(url=f'{apiUrl}/v1/barbells/{barbellId}/snapshots', headers=authHeaders)
    _check('GET snapshots succeeds', snapshotsResponse.status_code == HTTP_OK, str(snapshotsResponse.status_code))
    actionsResponse = await requester.get(url=f'{apiUrl}/v1/barbells/{barbellId}/actions', headers=authHeaders)
    _check('GET actions succeeds', actionsResponse.status_code == HTTP_OK, str(actionsResponse.status_code))

    await requester.close_connections()
    print()
    print(f'{sum(results)}/{len(results)} checks passed')
    if not all(results):
        raise SystemExit(1)


async def main() -> None:
    apiUrl = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_API_URL
    domain = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DOMAIN  # noqa: PLR2004
    await do_stuff(apiUrl=apiUrl, domain=domain)


if __name__ == '__main__':
    asyncio.run(main())
