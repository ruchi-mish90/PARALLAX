/**
 * Central API Client for PARALLAX Cross-Instrument Registration Backend
 * Handles network requests, timeouts, graceful fallback, and typed error handling.
 */

export interface BackendHealthResponse {
  status: 'ok' | 'degraded' | 'offline';
  service: string;
  version?: string;
  device?: string; // e.g., "cuda:0 (NVIDIA RTX 4090)" or "cpu"
  torchVersion?: string;
  opencvVersion?: string;
  availableModels?: string[];
  uptimeSeconds?: number;
  timestamp?: string;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any,
    message?: string
  ) {
    super(message || `API Error ${status}: ${statusText}`);
    this.name = 'ApiError';
  }
}

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS) || 120000;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiClient {
  private baseUrl: string;
  private timeoutMs: number;

  constructor(baseUrl: string = API_BASE_URL, timeoutMs: number = DEFAULT_TIMEOUT_MS) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.timeoutMs = timeoutMs;
  }

  public isLiveApiEnabled(): boolean {
    return import.meta.env.VITE_ENABLE_LIVE_API !== 'false';
  }

  private getFullUrl(endpoint: string): string {
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${this.baseUrl}${cleanEndpoint}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    customTimeoutMs?: number
  ): Promise<T> {
    const url = this.getFullUrl(endpoint);
    const timeout = customTimeoutMs || this.timeoutMs;

    const executeFetch = async (fetchUrl: string) => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      try {
        const res = await fetch(fetchUrl, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
            ...options.headers,
          },
        });
        clearTimeout(timeoutId);
        return res;
      } catch (err) {
        clearTimeout(timeoutId);
        throw err;
      }
    };

    let response: Response;
    try {
      response = await executeFetch(url);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        throw new ApiError(408, 'Request Timeout', null, `Request timed out after ${timeout}ms`);
      }
      const directUrl = url.startsWith('http') ? url : `http://127.0.0.1:8000${url.startsWith('/') ? url : `/${url}`}`;
      try {
        response = await executeFetch(directUrl);
      } catch (directErr: any) {
        if (directErr.name === 'AbortError') {
          throw new ApiError(408, 'Request Timeout', null, `Request timed out after ${timeout}ms`);
        }
        throw directErr;
      }
    }

    if (!response.ok) {
      let errorData: any = null;
      try {
        errorData = await response.json();
      } catch {
        errorData = await response.text();
      }
      throw new ApiError(
        response.status,
        response.statusText,
        errorData,
        errorData?.message || errorData?.detail || `Request failed with status ${response.status}`
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  }

  public async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  public async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
  }

  public async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  /**
   * Safe Health Check
   * Checks /api/health and direct http://127.0.0.1:8000/api/health
   */
  public async checkHealth(): Promise<BackendHealthResponse> {
    try {
      const res = await this.get<BackendHealthResponse>('/health', {
        headers: { 'Cache-Control': 'no-cache' },
      });
      if (res && res.status === 'ok') return res;
    } catch {
      try {
        const directResp = await fetch('http://127.0.0.1:8000/api/health', {
          headers: { 'Cache-Control': 'no-cache' },
        });
        if (directResp.ok) {
          const directData = await directResp.json();
          return directData;
        }
      } catch {}
    }

    return {
      status: 'offline',
      service: 'PARALLAX CV Backend (Unreachable / Offline)',
    };
  }
}

export const apiClient = new ApiClient();
export default apiClient;
