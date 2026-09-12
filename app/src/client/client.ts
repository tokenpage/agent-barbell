import { RestMethod, ServiceClient } from '@kibalabs/core';

import * as Endpoints from './endpoints';
import * as Resources from './resources';

export interface AuthToken {
  message: string;
  signature: string;
}

export class AgentBarbellClient extends ServiceClient {
  // eslint-disable-next-line class-methods-use-this
  private getHeaders = (authToken: string | null = null): Record<string, string> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      skip_zrok_interstitial: 'true',
    };
    if (authToken) {
      headers.Authorization = `Signature ${authToken}`;
    }
    return headers;
  };

  public login = async (authToken: string): Promise<Resources.User> => {
    const request = new Endpoints.LoginRequest();
    const response = await this.makeRequest(RestMethod.POST, 'v1/logins', request, Endpoints.LoginResponse, this.getHeaders(authToken));
    return response.user;
  };

  public createUser = async (walletAddress: string, username: string | null, signatureString: string): Promise<Resources.User> => {
    const request = new Endpoints.CreateUserRequest(walletAddress, username, signatureString);
    const response = await this.makeRequest(RestMethod.POST, 'v1/users', request, Endpoints.CreateUserResponse, this.getHeaders());
    return response.user;
  };

  public listBarbellAssets = async (chainId: number): Promise<Resources.BarbellAsset[]> => {
    const request = new Endpoints.ListBarbellAssetsRequest();
    const response = await this.makeRequest(RestMethod.GET, `v1/chains/${chainId}/barbell-assets`, request, Endpoints.ListBarbellAssetsResponse, this.getHeaders());
    return response.assets;
  };

  public getBarbell = async (authToken: string): Promise<Resources.Barbell | null> => {
    const request = new Endpoints.GetBarbellRequest();
    const response = await this.makeRequest(RestMethod.GET, 'v1/barbells', request, Endpoints.GetBarbellResponse, this.getHeaders(authToken));
    return response.barbell;
  };

  public createBarbell = async (authToken: string, config: Endpoints.CreateBarbellConfig): Promise<Resources.Barbell> => {
    const request = new Endpoints.CreateBarbellRequest(config);
    const response = await this.makeRequest(RestMethod.POST, 'v1/barbells', request, Endpoints.CreateBarbellResponse, this.getHeaders(authToken));
    return response.barbell;
  };

  public deactivateBarbell = async (barbellId: string, authToken: string): Promise<void> => {
    const request = new Endpoints.DeactivateBarbellRequest();
    await this.makeRequest(RestMethod.POST, `v1/barbells/${barbellId}/deactivate`, request, Endpoints.DeactivateBarbellResponse, this.getHeaders(authToken));
  };

  public getBarbellPortfolio = async (barbellId: string, authToken: string): Promise<Resources.Portfolio> => {
    const request = new Endpoints.GetBarbellPortfolioRequest();
    const response = await this.makeRequest(RestMethod.GET, `v1/barbells/${barbellId}/portfolio`, request, Endpoints.GetBarbellPortfolioResponse, this.getHeaders(authToken));
    return response.portfolio;
  };

  public getBarbellRiskState = async (barbellId: string, authToken: string): Promise<Resources.RiskState> => {
    const request = new Endpoints.GetBarbellRiskStateRequest();
    const response = await this.makeRequest(RestMethod.GET, `v1/barbells/${barbellId}/risk-state`, request, Endpoints.GetBarbellRiskStateResponse, this.getHeaders(authToken));
    return response.riskState;
  };

  public setRiskBudget = async (barbellId: string, maxDrawdownBps: number, targetSatelliteBps: number, maxSatelliteBps: number, authToken: string): Promise<Resources.RiskState> => {
    const request = new Endpoints.SetRiskBudgetRequest(maxDrawdownBps, targetSatelliteBps, maxSatelliteBps);
    const response = await this.makeRequest(RestMethod.POST, `v1/barbells/${barbellId}/risk-budget`, request, Endpoints.SetRiskBudgetResponse, this.getHeaders(authToken));
    return response.riskState;
  };

  public listBarbellSnapshots = async (barbellId: string, authToken: string): Promise<Resources.RiskSnapshot[]> => {
    const request = new Endpoints.ListBarbellSnapshotsRequest();
    const response = await this.makeRequest(RestMethod.GET, `v1/barbells/${barbellId}/snapshots`, request, Endpoints.ListBarbellSnapshotsResponse, this.getHeaders(authToken));
    return response.snapshots;
  };

  public listChatMessages = async (barbellId: string, authToken: string): Promise<Resources.ChatMessage[]> => {
    const request = new Endpoints.ListChatMessagesRequest();
    const response = await this.makeRequest(RestMethod.GET, `v1/barbells/${barbellId}/messages`, request, Endpoints.ListChatMessagesResponse, this.getHeaders(authToken));
    return response.messages;
  };

  public addUserMessageStreamed = async (barbellId: string, content: string, authToken: string, onMessage: (message: Resources.ChatMessage) => void): Promise<void> => {
    const request = new Endpoints.AddUserMessageStreamedRequest(content);
    const response = await fetch(`${this.baseUrl}/v1/barbells/${barbellId}/messages-streamed`, {
      method: RestMethod.POST,
      headers: this.getHeaders(authToken),
      body: JSON.stringify(request.toObject()),
    });
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    if (!response.body) {
      throw new Error('Response body is null');
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let isDone = false;
    while (!isDone) {
      // eslint-disable-next-line no-await-in-loop
      const result = await reader.read();
      if (result.done) {
        isDone = true;
        break;
      }
      buffer += decoder.decode(result.value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      lines.forEach((line: string): void => {
        if (!line.trim()) {
          return;
        }
        try {
          const data = JSON.parse(line);
          if (data.message) {
            onMessage(Resources.ChatMessage.fromObject(data.message));
          }
        } catch (error) {
          console.error('Error parsing streamed response:', error);
        }
      });
    }
  };

  public addCreationMessageStreamed = async (
    conversationId: string,
    content: string,
    config: Endpoints.CreateBarbellConfig,
    authToken: string,
    onMessage: (message: Resources.ChatMessage) => void,
  ): Promise<void> => {
    const request = new Endpoints.AddCreationMessageStreamedRequest(content, config);
    const response = await fetch(`${this.baseUrl}/v1/barbells/creation-conversations/${conversationId}/messages-streamed`, {
      method: RestMethod.POST,
      headers: this.getHeaders(authToken),
      body: JSON.stringify(request.toObject()),
    });
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    if (!response.body) {
      throw new Error('Response body is null');
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let isDone = false;
    while (!isDone) {
      // eslint-disable-next-line no-await-in-loop
      const result = await reader.read();
      if (result.done) {
        isDone = true;
        break;
      }
      buffer += decoder.decode(result.value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      lines.forEach((line: string): void => {
        if (!line.trim()) {
          return;
        }
        try {
          const data = JSON.parse(line);
          if (data.message) {
            onMessage(Resources.ChatMessage.fromObject(data.message));
          }
        } catch (error) {
          console.error('Error parsing streamed response:', error);
        }
      });
    }
  };

  public listBarbellActions = async (barbellId: string, authToken: string): Promise<Resources.BarbellAction[]> => {
    const request = new Endpoints.ListBarbellActionsRequest();
    const response = await this.makeRequest(RestMethod.GET, `v1/barbells/${barbellId}/actions`, request, Endpoints.ListBarbellActionsResponse, this.getHeaders(authToken));
    return response.actions;
  };
}
