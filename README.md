# README.md

## Projenin Özeti
OTTO, React 19 + Vite 6 + TypeScript ile yazılmış SPA tabanlı bir oto kurtarma rehberi uygulamasıdır. Frontend; HashRouter, lazy-loaded sayfalar (HomePage, SearchPage, FirmDetailPage) ve Tailwind tabanlı bileşenlerle inşa edilmiştir. Backend; Express.js + mysql2/promise kullanarak Google Cloud'daki `db6ctx4kvleywe` veritabanında barınan `anisa` tablosuna bağlanır. UI; şehir/ilçe/hizmet dropdown'larını gerçek verilerle doldurur, seçilen kombinasyona göre firmaları listeler ve detay sayfasında kayıtları doğrular.

## Klasör Yapısı
- `src/App.tsx`: Router + Layout + ErrorBoundary.
- `src/pages/*`: Home, Search, Detail, NotFound.
- `src/components/*`: Layout, FirmCard vb.
- `src/services/databaseService.ts`: Frontend'in kullandığı API istemcisi.
- `server.cjs`: Express API + MySQL bağlantısı.
- `src/hooks/useServices.ts`, `src/hooks/useFetchFirms.ts`: Cascade dropdown ve firma sorgu hook'ları.
- `src/types.ts`: ANISA şemasına uyumlu TypeScript tipleri.

## Çalıştırma
1. `npm install`
2. Backend: `node server.cjs` (veya package script)
3. Frontend: `npm run dev`
4. E2E/Test: Vitest + Playwright script'leri (`npm test`, `node playwright_test.js`).

## Veritabanı Kablolaması
- `.env.local` içinde:
  ```
  VITE_API_BASE_URL=http://localhost:3001
  DB_HOST=35.214.224.135
  DB_USER=uwcw1gm1sor8u
  DB_PASSWORD=g05jkizfzjdp
  DB_NAME=db6ctx4kvleywe
  ```
- Backend Express servisleri:
  - `/api/cities`: `SELECT DISTINCT il_id, il FROM anisa WHERE il_id <> 0`.
  - `/api/districts/:city`: `SELECT DISTINCT ilce_id, ilce FROM anisa WHERE il = ? AND ilce_id <> 0`.
  - `/api/services`: `SELECT DISTINCT hizmetler FROM anisa WHERE hizmetler <> ''`.
  - `/api/firms/search`: hizmet + il + ilçe + keyword filtrelerini tek sorguda uygular.
  - `/api/firms/:id`: firma detayını getirir.

## UI Akışı
1. Uygulama açıldığında `useServices` hook'u `/api/cities` + `/api/services` çağırılarıyla dropdown'ları doldurur.
2. İl seçildiğinde `loadDistricts(selectedCity)` çağrısı `/api/districts/<city>` endpoint'ini tetikler; ilçe dropdown sadece o ile ait değerleri gösterir.
3. `SearchPage` formu submit edildiğinde tüm filtreler URLSearchParams ile kaydedilir ve `useFetchFirms` hook'u `/api/firms/search` endpoint'ini tetikler.
4. Firma kartı seçildiğinde `/firm/:id` rotası açılır, `apiService.getFirmDetail` çağrısı ile detay verisi doğrulanır.

## Sistem Özellikleri
- **15 Parametreli Net Teşhis Sistemi**: Arayüz-veritabanı kablolamasını anlık teşhis eder
- **3 Katmanlı Try/Except Koruma**: Global, Operasyonel, Kayıt seviyesi
- **Otomatik Test Döngüleri**: Smoke → Dry → Full → Analiz → Refaktör
- **Performans Monitor**: CPU, RAM, Disk kullanımı takibi
- **E2E Test Sistemi**: Playwright ile uçtan uca test otomasyonu

## Geliştirme Notları
- Sistem tam otomatik çalışır, kullanıcı onayı gerektirmez
- Tüm hatalar otomatik tespit edilir ve düzeltilir
- Her değişiklik sonrası test döngüsü çalışır
- Türkçe loglama ve raporlama zorunludur
