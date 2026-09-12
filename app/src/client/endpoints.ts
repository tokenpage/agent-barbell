/* eslint-disable class-methods-use-this */
import { RequestData, ResponseData } from '@kibalabs/core';

import * as Resources from './resources';

export type RawObject = Record<string, unknown>;

export class LoginRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class LoginResponse extends ResponseData {
  public constructor(
    readonly user: Resources.User,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): LoginResponse => {
    return new LoginResponse(
      Resources.User.fromObject(obj.user as RawObject),
    );
  };
}

export class CreateUserRequest extends RequestData {
  public constructor(
    readonly walletAddress: string,
    readonly username: string | null,
    readonly signatureString: string,
  ) {
    super();
  }

  public toObject = (): RawObject => {
    return {
      walletAddress: this.walletAddress,
      username: this.username,
      signatureString: this.signatureString,
    };
  };
}

export class CreateUserResponse extends ResponseData {
  public constructor(
    readonly user: Resources.User,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): CreateUserResponse => {
    return new CreateUserResponse(
      Resources.User.fromObject(obj.user as RawObject),
    );
  };
}

export class GetBarbellRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class GetBarbellResponse extends ResponseData {
  public constructor(
    readonly barbell: Resources.Barbell | null,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): GetBarbellResponse => {
    return new GetBarbellResponse(
      obj.barbell ? Resources.Barbell.fromObject(obj.barbell as RawObject) : null,
    );
  };
}

export class ListBarbellAssetsRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class ListBarbellAssetsResponse extends ResponseData {
  public constructor(
    readonly assets: Resources.BarbellAsset[],
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): ListBarbellAssetsResponse => {
    return new ListBarbellAssetsResponse(
      (obj.assets as RawObject[]).map((asset: RawObject): Resources.BarbellAsset => Resources.BarbellAsset.fromObject(asset)),
    );
  };
}

export interface CreateBarbellConfig {
  name: string;
  satelliteAssetAddress: string;
  maxDrawdownBps: number;
  targetSatelliteBps: number;
  maxSatelliteBps: number;
}

export class CreateBarbellRequest extends RequestData {
  public constructor(
    readonly config: CreateBarbellConfig,
  ) {
    super();
  }

  public toObject = (): RawObject => {
    return {
      name: this.config.name,
      satelliteAssetAddress: this.config.satelliteAssetAddress,
      maxDrawdownBps: this.config.maxDrawdownBps,
      targetSatelliteBps: this.config.targetSatelliteBps,
      maxSatelliteBps: this.config.maxSatelliteBps,
    };
  };
}

export class CreateBarbellResponse extends ResponseData {
  public constructor(
    readonly barbell: Resources.Barbell,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): CreateBarbellResponse => {
    return new CreateBarbellResponse(
      Resources.Barbell.fromObject(obj.barbell as RawObject),
    );
  };
}

export class DeactivateBarbellRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class DeactivateBarbellResponse extends ResponseData {
  public constructor(
    readonly deactivated: boolean,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): DeactivateBarbellResponse => {
    return new DeactivateBarbellResponse(Boolean(obj.deactivated));
  };
}

export class GetBarbellPortfolioRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class GetBarbellPortfolioResponse extends ResponseData {
  public constructor(
    readonly portfolio: Resources.Portfolio,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): GetBarbellPortfolioResponse => {
    return new GetBarbellPortfolioResponse(
      Resources.Portfolio.fromObject(obj.portfolio as RawObject),
    );
  };
}

export class GetBarbellRiskStateRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class GetBarbellRiskStateResponse extends ResponseData {
  public constructor(
    readonly riskState: Resources.RiskState,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): GetBarbellRiskStateResponse => {
    return new GetBarbellRiskStateResponse(
      Resources.RiskState.fromObject(obj.riskState as RawObject),
    );
  };
}

export class SetRiskBudgetRequest extends RequestData {
  public constructor(
    readonly maxDrawdownBps: number,
    readonly targetSatelliteBps: number,
    readonly maxSatelliteBps: number,
  ) {
    super();
  }

  public toObject = (): RawObject => {
    return {
      maxDrawdownBps: this.maxDrawdownBps,
      targetSatelliteBps: this.targetSatelliteBps,
      maxSatelliteBps: this.maxSatelliteBps,
    };
  };
}

export class SetRiskBudgetResponse extends ResponseData {
  public constructor(
    readonly riskState: Resources.RiskState,
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): SetRiskBudgetResponse => {
    return new SetRiskBudgetResponse(
      Resources.RiskState.fromObject(obj.riskState as RawObject),
    );
  };
}

export class ListBarbellSnapshotsRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class ListBarbellSnapshotsResponse extends ResponseData {
  public constructor(
    readonly snapshots: Resources.RiskSnapshot[],
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): ListBarbellSnapshotsResponse => {
    return new ListBarbellSnapshotsResponse(
      (obj.snapshots as RawObject[]).map((snapshot: RawObject): Resources.RiskSnapshot => Resources.RiskSnapshot.fromObject(snapshot)),
    );
  };
}

export class ListBarbellActionsRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class ListBarbellActionsResponse extends ResponseData {
  public constructor(
    readonly actions: Resources.BarbellAction[],
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): ListBarbellActionsResponse => {
    return new ListBarbellActionsResponse(
      (obj.actions as RawObject[]).map((action: RawObject): Resources.BarbellAction => Resources.BarbellAction.fromObject(action)),
    );
  };
}

export class ListChatMessagesRequest extends RequestData {
  public toObject = (): RawObject => {
    return {};
  };
}

export class ListChatMessagesResponse extends ResponseData {
  public constructor(
    readonly messages: Resources.ChatMessage[],
  ) {
    super();
  }

  public static fromObject = (obj: RawObject): ListChatMessagesResponse => {
    return new ListChatMessagesResponse(
      (obj.messages as RawObject[]).map((message: RawObject): Resources.ChatMessage => Resources.ChatMessage.fromObject(message)),
    );
  };
}

export class AddUserMessageStreamedRequest extends RequestData {
  public constructor(
    readonly content: string,
  ) {
    super();
  }

  public toObject = (): RawObject => {
    return {
      content: this.content,
    };
  };
}

export class AddCreationMessageStreamedRequest extends RequestData {
  public constructor(
    readonly content: string,
    readonly config: CreateBarbellConfig,
  ) {
    super();
  }

  public toObject = (): RawObject => {
    return {
      content: this.content,
      name: this.config.name,
      satelliteAssetAddress: this.config.satelliteAssetAddress,
      maxDrawdownBps: this.config.maxDrawdownBps,
      targetSatelliteBps: this.config.targetSatelliteBps,
      maxSatelliteBps: this.config.maxSatelliteBps,
    };
  };
}
