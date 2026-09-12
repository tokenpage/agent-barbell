import { dateFromString } from '@kibalabs/core';

import { RawObject } from './endpoints';

// The API returns naive UTC datetime strings (no timezone suffix). dateFromString parses
// timezone-less strings as local time, so we append 'Z' when no offset is already present
// to make sure they're always interpreted as UTC.
const dateFromUtcString = (dateString: string): Date => {
  const hasTimezone = /(Z|[+-]\d{2}:?\d{2})$/.test(dateString);
  if (hasTimezone) {
    return dateFromString(dateString);
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    return dateFromString(`${dateString}T00:00:00Z`);
  }
  return dateFromString(`${dateString}Z`);
};

export class User {
  public constructor(
    readonly userId: string,
    readonly walletAddress: string,
    readonly username: string | null,
  ) { }

  public static fromObject = (obj: RawObject): User => {
    return new User(
      String(obj.userId),
      String(obj.walletAddress),
      obj.username ? String(obj.username) : null,
    );
  };
}

export class BarbellAsset {
  public constructor(
    readonly chainId: number,
    readonly address: string,
    readonly decimals: number,
    readonly name: string,
    readonly symbol: string,
    readonly logoUri: string | null,
    readonly isAnchor: boolean,
  ) { }

  public static fromObject = (obj: RawObject): BarbellAsset => {
    return new BarbellAsset(
      Number(obj.chainId),
      String(obj.address),
      Number(obj.decimals),
      String(obj.name),
      String(obj.symbol),
      obj.logoUri ? String(obj.logoUri) : null,
      Boolean(obj.isAnchor),
    );
  };
}

export class Barbell {
  public constructor(
    readonly barbellId: string,
    readonly name: string,
    readonly chainId: number,
    readonly walletAddress: string,
    readonly ownerAddress: string,
    readonly anchorAssetAddress: string,
    readonly satelliteAssetAddress: string,
    readonly isWalletDeployed: boolean,
    readonly createdDate: Date,
  ) { }

  public static fromObject = (obj: RawObject): Barbell => {
    return new Barbell(
      String(obj.barbellId),
      String(obj.name),
      Number(obj.chainId),
      String(obj.walletAddress),
      String(obj.ownerAddress),
      String(obj.anchorAssetAddress),
      String(obj.satelliteAssetAddress),
      Boolean(obj.isWalletDeployed),
      dateFromUtcString(obj.createdDate as string),
    );
  };
}

export class LegBalance {
  public constructor(
    readonly assetAddress: string,
    readonly symbol: string,
    readonly decimals: number,
    readonly balance: bigint,
    readonly priceUsd: number,
    readonly valueUsd: number,
  ) { }

  public static fromObject = (obj: RawObject): LegBalance => {
    return new LegBalance(
      String(obj.assetAddress),
      String(obj.symbol),
      Number(obj.decimals),
      BigInt(obj.balance as string),
      Number(obj.priceUsd),
      Number(obj.valueUsd),
    );
  };
}

export class Portfolio {
  public constructor(
    readonly chainId: number,
    readonly walletAddress: string,
    readonly anchor: LegBalance,
    readonly satellite: LegBalance,
    readonly cash: LegBalance,
    readonly totalValueUsd: number,
    readonly satelliteBps: number,
  ) { }

  public static fromObject = (obj: RawObject): Portfolio => {
    return new Portfolio(
      Number(obj.chainId),
      String(obj.walletAddress),
      LegBalance.fromObject(obj.anchor as RawObject),
      LegBalance.fromObject(obj.satellite as RawObject),
      LegBalance.fromObject(obj.cash as RawObject),
      Number(obj.totalValueUsd),
      Number(obj.satelliteBps),
    );
  };
}

export class RiskPolicy {
  public constructor(
    readonly maxDrawdownBps: number,
    readonly targetSatelliteBps: number,
    readonly maxSatelliteBps: number,
    readonly isKilled: boolean,
    readonly transactionHash: string | null,
  ) { }

  public static fromObject = (obj: RawObject): RiskPolicy => {
    return new RiskPolicy(
      Number(obj.maxDrawdownBps),
      Number(obj.targetSatelliteBps),
      Number(obj.maxSatelliteBps),
      Boolean(obj.isKilled),
      obj.transactionHash ? String(obj.transactionHash) : null,
    );
  };
}

export class RiskState {
  public constructor(
    readonly volatility: number,
    readonly momentum: number,
    readonly peakValueUsd: number,
    readonly totalValueUsd: number,
    readonly drawdownBps: number,
    readonly currentSatelliteBps: number,
    readonly targetSatelliteBps: number,
    readonly isKillSwitchTriggered: boolean,
    readonly shouldRebalance: boolean,
    readonly decisionTrace: string,
    readonly policy: RiskPolicy,
  ) { }

  public static fromObject = (obj: RawObject): RiskState => {
    return new RiskState(
      Number(obj.volatility),
      Number(obj.momentum),
      Number(obj.peakValueUsd),
      Number(obj.totalValueUsd),
      Number(obj.drawdownBps),
      Number(obj.currentSatelliteBps),
      Number(obj.targetSatelliteBps),
      Boolean(obj.isKillSwitchTriggered),
      Boolean(obj.shouldRebalance),
      String(obj.decisionTrace),
      RiskPolicy.fromObject(obj.policy as RawObject),
    );
  };
}

export class RiskSnapshot {
  public constructor(
    readonly snapshotDate: Date,
    readonly totalValueUsd: number,
    readonly satelliteBps: number,
    readonly drawdownBps: number,
    readonly volatility: number,
    readonly momentum: number,
    readonly targetSatelliteBps: number,
  ) { }

  public static fromObject = (obj: RawObject): RiskSnapshot => {
    return new RiskSnapshot(
      dateFromUtcString(obj.snapshotDate as string),
      Number(obj.totalValueUsd),
      Number(obj.satelliteBps),
      Number(obj.drawdownBps),
      Number(obj.volatility),
      Number(obj.momentum),
      Number(obj.targetSatelliteBps),
    );
  };
}

export class BarbellAction {
  public constructor(
    readonly barbellActionId: string,
    readonly createdDate: Date,
    readonly actionType: string,
    readonly fromSatelliteBps: number,
    readonly toSatelliteBps: number,
    readonly reason: string,
    readonly decisionTrace: string,
    readonly transactionHash: string | null,
  ) { }

  public static fromObject = (obj: RawObject): BarbellAction => {
    return new BarbellAction(
      String(obj.barbellActionId),
      dateFromUtcString(obj.createdDate as string),
      String(obj.actionType),
      Number(obj.fromSatelliteBps),
      Number(obj.toSatelliteBps),
      String(obj.reason),
      String(obj.decisionTrace),
      obj.transactionHash ? String(obj.transactionHash) : null,
    );
  };
}

export class ChatMessage {
  public constructor(
    readonly chatEventId: string,
    readonly createdDate: Date,
    readonly content: string,
    readonly isUser: boolean,
  ) { }

  public static fromObject = (obj: RawObject): ChatMessage => {
    return new ChatMessage(
      String(obj.chatEventId),
      dateFromUtcString(obj.createdDate as string),
      String(obj.content),
      Boolean(obj.isUser),
    );
  };
}
