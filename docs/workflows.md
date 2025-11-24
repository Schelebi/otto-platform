# 🔴 OTTO PROJE İŞ AKIŞLARI

## 📋 LOKASYON MANTIĞINI KONTROL ET

### Görev Adı: Kaskad Menü Entegrasyon Testi
### Öncelik: Yüksek
### Süre: ~15 dakika

---

### 🔴 ADIM 1: VERİTABANI BAĞLANTISINI KONTROL ET
**Komut:** `mysql -h 35.214.224.135 -u uwcw1gm1sor8u -p db6ctx4kvleywe`
**Beklenti:** Bağlantı başarılı, anisa tablosu erişilebilir
**Test:** `SHOW TABLES;` ve `DESCRIBE anisa;`
**Sonuç:** ✅ Bağlantı kuruldu / ❌ Hata mesajı

---

### 🔴 ADIM 2: İL LİSTESİNİ ÇEK
**Endpoint:** `GET /api/cities`
**Backend Logic:** `SELECT DISTINCT il FROM anisa ORDER BY il`
**Frontend Component:** `useServices()` hook'u
**Beklenti:** Benzersiz şehir listesi (örn: Adana, Ankara, İstanbul...)
**Test:** SearchPage açıldığında "İl" dropdown'ı dolu mu?
**Sonuç:** ✅ Şehirler yüklendi / ❌ Boş veya hata

---

### 🔴 ADIM 3: İLÇE BAĞLILIĞINI (CASCADING) DOĞRULA
**Test Senaryosu:** Adana örneği
1. Kullanıcı "Adana" il'ini seçer
2. Frontend `loadDistricts(cityId)` fonksiyonunu çağırır
3. Backend: `SELECT DISTINCT ilce FROM anisa WHERE il = 'Adana'`
4. Dropdown güncellenir: Seyhan, Çukurova, Yüreğir...
**Beklenti:** Sadece Adana'ya ait ilçeler görünür
**Kontrol:** Diğer şehirlerin ilçeleri karışıyor mu?
**Sonuç:** ✅ Doğru ilçeler / ❌ Yanlış veya boş

---

### 🔴 ADIM 4: KULLANICI AKIŞINI TEST ET
**Tam Akış:**
1. Arama sayfasını aç (`/search`)
2. "İl" dropdown'ından "Adana" seç
3. "İlçe" dropdown'ından "Seyhan" seç
4. "Hizmet" dropdown'ından "Oto Çekici" seç
5. "Filtrele" butonuna bas
6. Sonuçları kontrol et
**Beklenti:** `SELECT * FROM anisa WHERE il = 'Adana' AND ilce = 'Seyhan' AND hizmet LIKE '%Oto Çekici%'`
**Sonuç:** ✅ Doğru firmalar / ❌ Boş veya yanlış

---

### 🔴 ADIM 5: HATA DURUMLARINI TEST ET
**Senaryo A:** İl seçilmeden ilçe dropdown'ı
- **Beklenti:** Pasif durumda, "Önce İl Seçin" mesajı
- **Sonuç:** ✅ Pasif / ❌ Aktif (hata)

**Senaryo B:** API timeout
- **Beklenti:** Fallback veriler yüklenir
- **Sonuç:** ✅ Demo veriler / ❌ Boş sayfa

**Senaryo C:** Network error
- **Beklenti:** Error banner ve kullanıcı bilgilendirme
- **Sonuç:** ✅ Error gösteriliyor / ❌ Sessiz hata

---

### 🔴 ADIM 6: PERFORMANS TESTİ
**Metrikler:**
- İller yükleme süresi: <3 saniye
- İlçeler yükleme süresi: <2 saniye
- Firma arama süresi: <5 saniye
- UI responsiveness: Lock-free

**Test Araçları:**
- Browser Network tab
- Console logları
- React DevTools Profiler

---

### 🔴 ADIM 7: MOBİL UYUMLULUK TESTİ
**Cihazlar:**
- Mobile (320px+)
- Tablet (768px+)
- Desktop (1024px+)

**Kontroller:**
- Dropdown'lar kullanılabilir mi?
- Touch interaction çalışıyor mu?
- Layout bozuluyor mu?

---

## 🎯 BAŞARI KRİTERLERİ

### ✅ BAŞARILI SAYILIR:
- [ ] Veritabanı bağlantısı kuruldu
- [ ] İller listesi doğru yüklendi
- [ ] İlçe bağımlılığı çalışıyor (Adana → Seyhan, Çukurova...)
- [ ] Tam arama akışı çalışıyor
- [ ] Hata durumları yönetiliyor
- [ ] Performans kabul edilebilir
- [ ] Mobil uyumlu

### ❌ BAŞARISIZ SAYILIR:
- [ ] Veritabanı bağlantı hatası
- [ ] İller boş geliyor
- [ ] İlçe bağımsız yükleniyor
- [ ] Arama sonucu boş veya yanlış
- [ ] UI lock-up veya crash
- [ ] Kritik hatalar yönetilmiyor

---

## 🔄 OTOMATİK TEST KOMUTLARI

```bash
# Frontend build test
npm run build

# Development server test
npm run dev

# Database connection test
python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='35.214.224.135',
    user='uwcw1gm1sor8u',
    password='g05jkizfzjdp',
    database='db6ctx4kvleywe'
)
print('✅ DB Connection OK')
conn.close()
"
```

---

## 📊 TEST RAPORU ŞABLONU

```
Tarih: ____________
Tester: ____________

🔴 VERİTABANI BAĞLANTISI: ✅ / ❌
🔴 İLLER LİSTESİ: ✅ / ❌
🔴 İLÇE BAĞLILIĞI: ✅ / ❌
🔴 ARAMA AKIŞI: ✅ / ❌
🔴 HATA YÖNETİMİ: ✅ / ❌
🔴 PERFORMANS: ✅ / ❌
🔴 MOBİL UYUM: ✅ / ❌

GENEL DEĞERLENDİRME: BAŞARILI / BAŞARISIZ
NOTLAR: _____________________________
```

---

## 🚨 KRİTİK NOTLAR

1. **Hiçbir zaman ilçe verisini bağımsız çekme**
2. **Parent-child ilişki mutlaka korunmalı**
3. **SELECT DISTINCT kullanımı zorunlu**
4. **Real database connection, placeholder yok**
5. **Error handling ile kullanıcı deneyimi**
6. **Loading states ile UI feedback**
7. **Mobile-first design prensibi**

---

**Bu iş akışı OTTO projesinin kaskad menü mantığının doğru çalıştığını garanti altına almak için tasarlanmıştır.**
