# agents.md

## 1. Genel Fotoğraf
- **Ürün amacı**: metadata.json:2 Türkiye genelinde oto çekici/kurtarma firmalarını indeksleyen OTTO rehberi.
- **Teknoloji yığını**: package.json:1 React 19, React Router 7, Vite 6, Leaflet ve TypeScript 5.8 üzerine kurulu; UI katmanı Tailwind sınıflarıyla yazılmış.
- **Yerel yapılandırma**: .env.local:5 API ana adresiyle birlikte hassas DB bilgilerinin de tutulduğu tek dosya; repo içinde `.env.example` yok.

## 2. Katman Özeti
### Router & Shell
- src/index.tsx:1 uygulamayı mount ederken env doğrulaması ve global hata yakalayıcı kuruyor.
- src/App.tsx:72 HashRouter + Layout + ErrorBoundary içeriyor; aynı rotalar src/router/AppRouter.tsx:1 dosyasında ikinci kez tanımlı.
- src/components/Layout.tsx:1 nav, footer ve ToastContext’i yönetiyor ancak context dışarıda kullanılmıyor.

### Sayfalar
- src/pages/HomePage.tsx gerçek API’den öne çıkan firmaları listeliyor ve “Konumuma göre ara” butonu ile /search’e yönlendiriyor.
- src/pages/SearchPage.tsx dinamik filtreler, grid/list/map görünümleri ve Leaflet haritası sağlıyor.
- src/pages/FirmDetailPage.tsx firma detayını, iletişim butonlarını ve haritayı çiziyor.
- src/pages/NotFoundPage.tsx basit 404 fallback veriyor.

### Servis & Data Katmanı
- src/services/apiClient.ts HTTP istekleri için timeout/retry içeren yardımcı.
- src/services/apiService.ts REST endpoint’lerini tanımlıyor fakat env’deki VITE_API_* anahtarlarını okumuyor.
- src/services/mockApiService.ts gerçek API çağrısı + opsiyonel local JSON fallback mantığını aynı dosyada saklıyor.
- src/constants.ts API sabitleri ile fallback şehir/hizmet listelerini sağlıyor.

### Hook / Yardımcılar
- src/hooks/useFetchFirms.ts ve src/hooks/useServices.ts gerçek servis hazır olduğunda ona geçmeye çalışıyor, aksi halde mock servise düşüyor.
- src/hooks/useGeoLocation.ts tarayıcı konum desteği için hazır ama hiçbir yerde çağrılmamış.

### Stil & Build
- index.html:1 Tailwind’i CDN’den, React’i importmap üzerinden yüklüyor; bu, Vite bundler ile paralel yürüyor.
- src/index.css global reset + Leaflet kaplamaları için manuel CSS sağlıyor.
- vite.config.ts @ alias’ı oluşturuyor fakat Tailwind/PostCSS entegrasyonu yok.

## 3. Eksikler ve Riskler
1. **Gerçek API servisi hook’lara bağlanmıyor (P0)**  
   - Kanıt: src/hooks/useFetchFirms.ts:56 ve src/hooks/useServices.ts:33 dinamik olarak `api` veya `default` export arıyor; src/services/apiService.ts sadece `apiService` isimli export üretiyor.  
   - Etki: Hook’lar her zaman mockApiService’e düşerek ekstra ağ çağrıları ve iki ayrı servis kodu oluşturuyor; gerçek servis güncellemeleri UI’ya yansımıyor.  
   - Yapılması gerekenler:  
     - apiService.ts’te hem `export const api = apiService` hem de `export default apiService` ekle veya hook’ları doğrudan named export kullanacak şekilde düzenle.  
     - tek bir servis nesnesi tut ve mock senaryosu için MSW/fixture yaklaşımı ekle.  

2. **Mock fallback veri seti yok (P0)**  
   - Kanıt: src/services/mockApiService.ts:126 `import("../data/anisa.json")` diyor fakat projede data klasörü bulunmuyor.  
   - Etki: Backend erişilemezse loadLocalFallback boş dönüyor ve tüm ekranlar boş liste gösteriyor.  
   - Yapılması gerekenler:  
     - src/data/anisa.json veya benzeri küçük bir seed dosyası ekle.  
     - Aynı fallback’i apiService.safeListFirms ve getCities gibi fonksiyonlarda da kullanarak tek kaynağa indir.  

3. **Arama filtreleri URL ile senkron değil (P1)**  
   - Kanıt: src/pages/SearchPage.tsx:48-65 sadece ilk yüklemede query parametrelerini state’e kopyalıyor; 264-337 arası formlar state’i güncelliyor fakat `handleFilterSubmit` hiçbir zaman `navigate` çağırmıyor.  
   - Etki: Kullanıcı filtre değiştirdiğinde URL değişmiyor; sayfa yenilenince filtreler sıfırlanıyor ve link paylaşımı mümkün olmuyor.  
   - Yapılması gerekenler:  
     - Filtre değişimlerinde URLSearchParams’i güncelleyip `useNavigate` ile push/replace et.  
     - Form submit veya debounce edilen değişikliklerde yeni parametrelerle `location.search`i güncelle ki effect tekrar tetiklensin, state-single-source olsun.  

4. **Home CTA 404’a gidiyor (P1)**  
   - Kanıt: src/pages/HomePage.tsx:343 `navigate('/add-firm')` çağırıyor; src/App.tsx:83-86 rotalar arasında `/add-firm` yok.  
   - Etki: “Firma Ekle” aksiyonu hatayla sonuçlanıyor, dönüşümler kaybediliyor.  
   - Yapılması gerekenler:  
     - `/add-firm` için sayfa + route ekle ya da CTA’yı mevcut iletişim kanallarına yönlendir.  

5. **Router tanımı iki yerde drift ediyor (P1)**  
   - Kanıt: Uygulama gerçekte src/App.tsx içindeki Routes yapısını kullanıyor; src/router/AppRouter.tsx:1 aynı rotaları safeLazy ile tekrar tanımlıyor ancak hiçbir yerde import edilmiyor.  
   - Etki: Yeni rota eklenirken iki dosyanın da güncellenmesi gerekiyor; biri unutulursa derleme fakat runtime belirsizliği oluşuyor.  
   - Yapılması gerekenler:  
     - Router konfigürasyonunu tek dosyada topla ve App.tsx yalnızca Layout + Router bileşenlerini sarsın.  
     - Kullanılmayan AppRouter dosyasını ya entegre et ya da sil.  

6. **Custom hook ve ToastContext kullanılmıyor (P2)**  
   - Kanıt: `rg useFetchFirms`, `useServices`, `useGeoLocation` ve `useToast` aramaları sadece tanım dosyalarını gösteriyor; tüketim yok.  
   - Etki: Aynı veri çekme ve konum mantığı Home/Search sayfalarında tekrar yazılıyor, test yükü artıyor.  
   - Yapılması gerekenler:  
     - Search/Home sayfalarını bu hook’lara taşıyıp tekrar eden kodu sil veya hook’ları repository dışına çıkar.  
     - ToastContext’i gerçek hata bildirimleriyle entegre et (ör. API catch blokları).  

7. **Environment + endpoint kullanımı tutarsız (P2)**  
   - Kanıt: .env.local:5 VITE_API_FIRMS vb. değerleri sunuyor, ayrıca DB kimlik bilgileri içeriyor; src/constants.ts:32 ve src/services/apiService.ts:20 bu env anahtarlarını hiç okumuyor.  
   - Etki: Env’de yapılan güncellemeler üretim koduna yansımıyor, ayrıca gizli DB bilgileri frontend repo’da tutuluyor.  
   - Yapılması gerekenler:  
     - constants/apiService içindeki endpointleri VITE_API_* değişkenlerine bağla.  
     - `.env.example` oluştur, gerçek database bilgilerini frontend deposundan taşı.  
     - requestJson/buildUrl fonksiyonlarını tek merkezden env okur hale getir.  

8. **Tailwind CDN + importmap, Vite bundler ile çakışıyor (P2)**  
   - Kanıt: index.html:34-79 React/Tailwind’i CDN’den yüklüyor ve importmap ile yönlendiriyor, aynı modüller paket yöneticisi ile de kurulu.  
   - Etki: Çift React kopyası yüklenme, CSP ihlali ve üretimde treeshake edilemeyen CSS riski var.  
   - Yapılması gerekenler:  
     - Tailwind’i `devDependencies`e ekleyip Vite/PostCSS pipeline’ında derle; CDN scriptlerini kaldır.  
     - importmap’i kaldırıp Vite’in yerel bundle’ına güven.  

9. **Test / lint pipeline yok (P2)**  
   - Kanıt: package.json:5 sadece `dev`, `build`, `preview` scriptleri var; lint/test tanımı yok.  
   - Etki: Tip hataları, unit/regression testleri için otomasyon bulunmuyor ve CI kurulamıyor.  
   - Yapılması gerekenler:  
     - `tsc --noEmit`, ESLint/Prettier ve en azından react-testing-library tabanlı birkaç smoke test ekle.  

## 4. Yol Haritası Önerisi
- **P0 (hemen)**: apiService exportlarını düzelt, hook’ların gerçek servise bağlandığını doğrula; `data/anisa.json` fallback’ini ekleyip offline senaryoyu kurtar.  
- **P1 (bu sprint)**: Search filtre-URL senkronizasyonunu kur, `/add-firm` rotasını tamamla, router konfigürasyonunu tek kaynağa indir.  
- **P2 (takip)**: Kullanılmayan hook/context’leri entegre et, env + Tailwind konfigürasyonunu sadeleştir, lint/test scriptlerini CI’a ekle ve hassas bilgileri `.env.example` stratejisiyle belgele.
