/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_CITIES: string;
  readonly VITE_API_SERVICES: string;
  readonly VITE_API_SEARCH: string;
  readonly VITE_API_DISTRICTS: string;
  readonly VITE_API_NEARBY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
