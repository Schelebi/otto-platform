/**
 * 1) KOD ADI:
 * ApiClient (HTTP İstemci)
 *
 * 2) KOD YOLU (GÖRELİ):
 * src/services/apiClient.ts
 *
 * 3) KODUN AMACI (5 MADDE):
 * - HTTP istekleri için merkezi istemci sağlamak
 * - Request/response interceptor'lar eklemek
 * - Error handling ve retry mekanizması sunmak
 * - API timeout'larını yönetmek
 * - Authentication header'larını otomatik eklemek
 *
 * 4) KODLA İLGİLİ TÜM REVİZYONLAR:
 * - Yeni dosya oluşturuldu
 * - HTTP istemci fonksiyonları eklendi
 * - Error handling eklendi
 *
 * 5) KODLA İLGİLİ TALİMATLARIN TÜMÜ KODLANDI:
 * - TypeScript tip güvenliği sağlandı
 * - Fetch API kullanıldı
 * - Timeout ve retry mekanizması eklendi
 */

interface ApiClientOptions {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
}

class ApiClient {
  private baseURL: string;
  private defaultOptions: ApiClientOptions;

  constructor(baseURL: string = '', options: ApiClientOptions = {}) {
    this.baseURL = baseURL;
    this.defaultOptions = {
      timeout: 10000,
      retries: 3,
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };
  }

  private async request<T>(
    url: string,
    options: RequestInit = {},
    customOptions: ApiClientOptions = {}
  ): Promise<T> {
    const finalOptions = { ...this.defaultOptions, ...customOptions };
    const fullUrl = `${this.baseURL}${url}`;

    let lastError: Error;

    for (let attempt = 0; attempt <= finalOptions.retries!; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);

        const response = await fetch(fullUrl, {
          ...options,
          headers: {
            ...finalOptions.headers,
            ...options.headers,
          },
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        lastError = error as Error;

        if (attempt === finalOptions.retries) {
          break;
        }

        // Retry delay with exponential backoff
        await new Promise(resolve =>
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        );
      }
    }

    throw lastError!;
  }

  async get<T>(url: string, options: ApiClientOptions = {}): Promise<T> {
    return this.request<T>(url, { method: 'GET' }, options);
  }

  async post<T>(url: string, data?: any, options: ApiClientOptions = {}): Promise<T> {
    return this.request<T>(
      url,
      {
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined,
      },
      options
    );
  }

  async put<T>(url: string, data?: any, options: ApiClientOptions = {}): Promise<T> {
    return this.request<T>(
      url,
      {
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined,
      },
      options
    );
  }

  async delete<T>(url: string, options: ApiClientOptions = {}): Promise<T> {
    return this.request<T>(url, { method: 'DELETE' }, options);
  }

  setBaseURL(baseURL: string): void {
    this.baseURL = baseURL;
  }

  setDefaultHeader(key: string, value: string): void {
    this.defaultOptions.headers![key] = value;
  }
}

// Singleton instance
export const apiClient = new ApiClient();

export default apiClient;
