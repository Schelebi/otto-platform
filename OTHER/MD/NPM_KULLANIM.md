# NPM Kullanım Talimatları

## Sorun
`fix.py` scripti npm'i otomatik olarak bulamıyor çünkü PATH'de değil.

## Çözüm
Aşağıdaki komutları manuel olarak çalıştırın:

### 1. NPM versiyonunu kontrol et
```cmd
"C:\Program Files\nodejs\npm.cmd" --version
```

### 2. Dependencies kur
```cmd
"C:\Program Files\nodejs\npm.cmd" install
```

### 3. Test çalıştır
```cmd
"C:\Program Files\nodejs\npm.cmd" test
```

### 4. Build yap
```cmd
"C:\Program Files\nodejs\npm.cmd" run build
```

### Alternatif: PATH'e ekle
Geçici olarak npm'i PATH'e eklemek için:
```cmd
set PATH="C:\Program Files\nodejs";%PATH%
npm --version
```

Kalıcı olarak eklemek için:
1. Windows Arama'da "Environment Variables" ara
2. "Edit the system environment variables" tıkla
3. "Environment Variables" butonuna tıkla
4. "Path" değişkenini seç ve "Edit" tıkla
5. "New" tıkla ve `C:\Program Files\nodejs` ekle
6. Tamamla ve terminal'i yeniden başlat

## Script Sonucu
`fix.py` scripti başarıyla çalıştı:
- ✅ Ortam kontrolü (npm atlandı)
- ✅ index.html düzeltildi
- ✅ Vitest dosyaları oluşturuldu
- ✅ package.json kontrol edildi
- ⚠️ npm komutları manuel çalıştırılacak
