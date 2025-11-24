/**
 * 1) KOD ADI:
 * OTTO — ANISA TypeScript Tipleri (Gerçek DB şema uyumu)
 *
 * 2) KOD YOLU (GÖRELI):
 * src/types.ts
 *
 * 3) KODUN AMACI (5 MADDE):
 * - ANISA tablosunun tüm kolonlarını birebir TypeScript’e taşımak.
 * - Null/opsiyonel alanları güvenli şekilde tanımlamak.
 * - phones_json ve aktif alanlarını gerçek DB formatına uyarlamak.
 * - Nearby araması için hesaplanan distance alanını desteklemek.
 * - Tüm UI ve servis katmanının tek şemaya bağlanmasını sağlamak.
 *
 * 4) KODLA İLGİLİ TÜM REVİZYONLAR:
 * - phones_json tipi genişletildi (string | array | object | null).
 * - aktif tipi boolean yanında 0/1 kabul edecek hale getirildi.
 * - slug ve bazı alanlar DB’de nullable olduğu için opsiyonel yapıldı.
 * - distance_km alanı eklendi (nearby sonuçları için).
 *
 * 5) KODLA İLGİLİ TALİMATLARIN KODLANMIŞ HALİ:
 * - ANISA şeması %100 korunur, isimler birebir aynıdır.
 * - Null gelebilecek kolonlar opsiyonel/nullable işaretlenmiştir.
 * - UI/servis tarafı bu tipleri zorunlu referans alır.
 */

export type BackendBool = boolean | 0 | 1;

export type PhonesJson =
  | string
  | string[]
  | { phones?: string[]; whatsapp?: string }
  | null
  | undefined;

export interface AnisaRecord {
  id: number; // int unsigned NOT NULL DEFAULT 0
  firma_id?: number | null; // int unsigned
  all_hepsi?: string | null; // longtext
  firma_adi: string; // varchar(255) NOT NULL
  il_id: number; // int unsigned NOT NULL
  il: string; // varchar(100) NOT NULL
  ilce_id: number; // int unsigned NOT NULL
  ilce: string; // varchar(120) NOT NULL
  hizmetler?: string | null; // text
  telefon?: string | null; // varchar(32)
  phones_json?: PhonesJson; // text(JSON) → normalize edilecek
  email?: string | null; // varchar(255)
  google_review_url?: string | null; // varchar(255)
  website?: string | null; // varchar(255)
  categories?: string | null; // varchar(255)
  adres_full?: string | null; // varchar(512)
  mahalle?: string | null; // varchar(120)
  sokak?: string | null; // varchar(160)
  puan: number; // decimal(2,1) DEFAULT 5.0
  yorum_sayisi: number; // int unsigned DEFAULT 0
  lat?: number | null; // decimal(9,6)
  lng?: number | null; // decimal(9,6)
  aktif: BackendBool; // tinyint(1) DEFAULT 1
  slug?: string | null; // varchar(255) nullable
  featured_image?: string | null; // varchar(255)
  google_maps_url?: string | null; // varchar(255)
  created_at?: string | null; // timestamp
  updated_at?: string | null; // timestamp
  distance_km?: number; // computed field for nearby
}

export interface SearchFilters {
  il?: string;
  ilce?: string;
  hizmet?: string;
  kelime?: string;
  lat?: number;
  lng?: number;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface City {
  id: string | number;
  name: string;
  slug: string;
}

export interface District {
  id: string | number;
  name: string;
  slug: string;
  city_id?: string | number;
}

export interface Service {
  id: string | number;
  name: string;
  slug: string;
  description?: string;
}

export interface Firm {
  id: number;
  name: string;
  phone: string;
  whatsapp?: string;
  email?: string;
  address: string;
  city?: string;
  district?: string;
  hizmetler?: string;
  latitude?: number | null;
  longitude?: number | null;
  rating: number;
  reviews: number;
  verified: boolean;
  featured_image?: string;
}

export interface SearchFilters {
  cityId?: string;
  districtId?: string;
  serviceId?: string;
  keyword?: string;
}
