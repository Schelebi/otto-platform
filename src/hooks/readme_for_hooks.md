# Hooks Kılavuzu

## useServices
- Amaç: İlleri, ilçeleri ve hizmetleri gerçek API’den çekip bileşenlere sunmak.
- Akış: İlk render’da `/api/cities` ve `/api/services` çağrılır; seçilen ile göre `loadDistricts(il)` tetiklenir.
- Durumlar: `cities`, `districts`, `services`, `loading`, `error` state’leri tüketen bileşenlere döner.

## useFetchFirms
- Amaç: Hizmet + il + ilçe + anahtar kelime filtrelerini backend’e gönderip firma listesini almak.
- Akış: `filters` bağımlılıkları değiştiğinde `/api/firms/search` çağrılır; sonuçlar FirmCard’larda kullanılır.
- Hata Yönetimi: API başarısız olursa fallback mesajı ve boş liste döner.

## Genişletme Notları
- Yeni hook eklerken TypeScript tiplerini `src/types.ts` dosyasından referans alın.
- API’ye yeni parametre ekleyecekseniz hem hook hem de backend sorgularını güncelleyin.
