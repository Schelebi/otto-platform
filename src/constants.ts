/**
 * 1) KOD ADI:
 * OTTO — Constants + Real API Endpoints (Fallbacks güvenli)
 *
 * 2) KOD YOLU (GÖRELI):
 * src/constants.ts
 *
 * 3) KODUN AMACI (5 MADDE):
 * - Gerçek API base URL ve endpoint yollarını tek yerden yönetmek.
 * - Hardcode verileri yalnızca fallback olarak tutmak.
 * - Mock’a özel sabitleri üretim akışından ayırmak.
 * - UI’nin güvenle çalışması için boş/undefined riskini sıfırlamak.
 * - Harita ve görsel varsayılanlarını tüm cihazlarda stabil tutmak.
 *
 * 4) KODLA İLGİLİ TÜM REVİZYONLAR:
 * - API_BASE_URL ve API_ENDPOINTS eklendi.
 * - CITIES / DISTRICTS / SERVICES artık FALLBACK olarak etiketlendi.
 * - MOCK_IMAGES adı FALLBACK_IMAGES olarak revize edildi, alias korundu.
 *
 * 5) KODLA İLGİLİ TALİMATLARIN KODLANMIŞ HALİ:
 * - Gerçek veri önceliklidir, fallback sadece API çökünce kullanılır.
 * - Hardcode listeler üretim akışını belirlemez.
 * - Env okuma try ile korunur, sistem çökmez.
 */

// L1: Env güvenli okuma
const safeEnv = <T = string>(key: string, fallback: T): T => {
  try {
    return ((import.meta as any)?.env?.[key] as T) ?? fallback;
  } catch {
    return fallback;
  }
};

// Real API base + endpoints (env üzerinden override edilir)
export const API_BASE_URL = safeEnv<string>("VITE_API_BASE_URL", "");

const envPath = (key: string, fallback: string) => safeEnv<string>(key, fallback);

const buildDetailPath = (template: string, id: number | string) => {
  if (template.includes(":id")) {
    return template.replace(":id", String(id));
  }
  const normalized = template.endsWith("/") ? template.slice(0, -1) : template;
  return `${normalized}/${id}`;
};

const FIRM_DETAIL_TEMPLATE = envPath("VITE_API_FIRM_DETAIL", "/api/firm/:id");

export const API_ENDPOINTS = {
  firms: envPath("VITE_API_FIRMS", "/api/firms"),
  search: envPath("VITE_API_SEARCH", "/api/search"),
  nearby: envPath("VITE_API_NEARBY", "/api/nearby"),
  cities: envPath("VITE_API_CITIES", "/api/cities"),
  districts: envPath("VITE_API_DISTRICTS", "/api/districts"),
  services: envPath("VITE_API_SERVICES", "/api/services"),
  firmDetail: (id: number | string) => buildDetailPath(FIRM_DETAIL_TEMPLATE, id),
};

// ---- FALLBACK DATA (API başarısız olursa minimum UI için) ----

// Cities data for dropdowns (fallback)
export const FALLBACK_CITIES = [
  "İstanbul",
  "Ankara",
  "İzmir",
  "Bursa",
  "Antalya",
  "Adana",
  "Konya",
  "Gaziantep",
];

// District mapping (fallback)
export const FALLBACK_CITIES_DISTRICTS: Record<string, string[]> = {
  İstanbul: ["Kadıköy", "Beşiktaş", "Ümraniye", "Şişli", "Kartal", "Maltepe", "Pendik", "Üsküdar"],
  Ankara: ["Çankaya", "Keçiören", "Yenimahalle", "Mamak", "Etimesgut", "Sincan"],
  İzmir: ["Konak", "Karşıyaka", "Bornova", "Buca", "Çiğli", "Gaziemir"],
  Bursa: ["Nilüfer", "Osmangazi", "Yıldırım", "İnegöl"],
  Antalya: ["Muratpaşa", "Kepez", "Konyaaltı", "Alanya", "Manavgat"],
  Adana: ["Seyhan", "Çukurova", "Yüreğir", "Sarıçam"],
  Konya: ["Selçuklu", "Meram", "Karatay"],
  Gaziantep: ["Şahinbey", "Şehitkamil"],
};

// Services (fallback)
export const FALLBACK_SERVICES = [
  "Oto Çekici",
  "Yol Yardım",
  "Akü Takviye",
  "Lastik Değişimi",
  "Vinç Hizmeti",
  "Motosiklet Taşıma",
  "Ağır Ticari Çekici",
];

// Images (fallback)
export const FALLBACK_IMAGES = [
  "https://picsum.photos/800/600?random=1",
  "https://picsum.photos/800/600?random=2",
  "https://picsum.photos/800/600?random=3",
  "https://picsum.photos/800/600?random=4",
];

// ---- Backward-compatible aliases (mevcut importlar kırılmasın) ----
export const CITIES = FALLBACK_CITIES;
export const CITIES_DISTRICTS = FALLBACK_CITIES_DISTRICTS;
export const SERVICES = FALLBACK_SERVICES;
export const MOCK_IMAGES = FALLBACK_IMAGES;
