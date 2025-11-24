# 🔴 MANUEL TEST TALİMATLARI - EKRAN KAYDI OLMADAN

## 📱 TEST ADIMLARI:
1. **Browser aç:** http://localhost:3000/search
2. **İl dropdown'u kontrol et:** Gerçek şehirler (Adana, Adıyaman, Afyonkarahisar...)
3. **Şehir seç:** Adana veya İstanbul seç
4. **İlçe dropdown'unu bekle:** 1-2 saniye içinde ilçeler yüklenmeli
5. **İlçe seç:** Merkez veya başka ilçe seç
6. **Hizmet seç:** Oto Çekici seç
7. **Ara butonuna tıkla:** Sonuçlar gelmeli

## ✅ BEKLENEN SONUÇLAR:
- **Mock data yok:** İstanbul, Ankara, İzmir gibi sahte şehirler olmamalı
- **Gerçek şehirler:** Adana, Adıyaman, Afyonkarahisar... MySQL'den gelmeli
- **Kaskad çalışmalı:** Şehir seçince ilçeler otomatik yüklenmeli
- **API hatası yok:** "İlçeler yüklenemedi" uyarısı olmamalı

## 🔍 KONTROL EDİLECEKLER:
1. **Backend API:** http://localhost:3001/api/cities → JSON şehir listesi
2. **Frontend state:** Browser devtools → Application → Local Storage
3. **Network tab:** API çağrıları başarılı mı?
4. **Console log:** Hata mesajları var mı?

## 📊 TEST SONUCU RAPORU:
- ✅ Sayfa yüklendi
- ❌ İl dropdown bulunamadı (mock data'dan kalma olabilir)
- 🔍 Manuel kontrol gerekli
