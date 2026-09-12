export interface User {
  userId: string;
  createdDate: string;
  updatedDate: string;
  walletAddress: string;
  username: string | null;
}

interface RequestOptions {
  method: string;
  body?: unknown;
  authToken?: string;
}

// NOTE: hand-written fetch wrapper rather than @kibalabs/core's ServiceClient — this
// skeleton only needs two endpoints; swap to ServiceClient once there are enough
// endpoints for its generated Request/Response classes to earn their keep.
export class AgentBarbellClient {
  public constructor(private readonly baseUrl: string) {
  }

  private request = async <T>(path: string, options: RequestOptions): Promise<T> => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (options.authToken) {
      headers.Authorization = `Signature ${options.authToken}`;
    }
    const response = await fetch(`${this.baseUrl}/${path}`, {
      method: options.method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const json = await response.json();
    if (!response.ok) {
      throw new Error(json.message || `Request failed: ${response.status}`);
    }
    return json as T;
  };

  public login = async (authToken: string): Promise<User> => {
    const result = await this.request<{ user: User }>('v1/logins', { method: 'POST', authToken });
    return result.user;
  };

  public createUser = async (walletAddress: string, username: string | null, signatureString: string): Promise<User> => {
    const result = await this.request<{ user: User }>('v1/users', { method: 'POST', body: { walletAddress, username, signatureString } });
    return result.user;
  };
}
