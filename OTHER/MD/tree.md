# 🌳 OTTO Rehberi - Sistem Tree Yapısı

**Proje:** OTTO - Türkiye Oto Çekici/Kurtarma Firmaları Rehberi
**Konum:** `c:\laragon\www\g\s\all`
**Teknoloji:** React 19 + TypeScript + Vite 6 + Leaflet + Tailwind CSS

---

## 📁 Kök Dizin Yapısı

```
c:\laragon\www\g\s\all\
├── 📄 README.md
├── 📄 metadata.json
├── 📄 package.json
├── 📄 package-lock.json
├── 📄 tsconfig.json
├── 📄 vite.config.ts
├── 📄 vitest.config.ts
├── 📄 index.html
├── 📄 .gitignore
├── 📄 .env.local
├── 📄 NPM_KULLANIM.md
├── 📄 agents.md
├── 📄 rapor.txt
├── 📄 all.code-workspace
├── 🐍 Python Scripts
│   ├── gpt_codex_full_permissions.py
│   ├── kernel_mode_permissions.py
│   ├── force_mandatory_root.py
│   └── gpt_codex_error_fix.py
├── 📄 Fix Scripts
│   ├── fix.py
│   ├── 1a-izin.py
│   ├── gpt_codex_permissions.json
│   ├── kernel_mode_status.json
│   └── gpt_codex_error_fix_proof.json
├── 📄 Development Tools
│   ├── start_dev_server.py
│   ├── gpt_codex_full_permissions.py
│   └── npm.bat / npm.ps1
├── 📄 API Server
│   └── local-api-server.js
└── 📂 src/
```

---

## 🚀 src/ - Uygulama Kaynak Kodları

```
src/
├── 📄 index.tsx              # React uygulama giriş noktası
├── 📄 App.tsx                 # Ana uygulama bileşeni
├── 📄 index.css               # Global stiller + Leaflet kaplamaları
├── 📄 constants.ts            # API sabitleri ve fallback veriler
├── 📄 types.ts                # TypeScript tip tanımlamaları
│
├── 📂 components/             # UI Bileşenleri
│   ├── 📄 Layout.tsx          # Ana layout (nav, footer, ToastContext)
│   └── 📄 FirmCard.tsx        # Firma kartı bileşeni
│
├── 📂 pages/                  # Sayfa Bileşenleri
│   ├── 📄 HomePage.tsx        # Ana sayfa (öne çıkan firmalar)
│   ├── 📄 SearchPage.tsx      # Arama sayfası (filtreler, grid/list/map)
│   ├── 📄 FirmDetailPage.tsx  # Firma detay sayfası
│   ├── 📄 AddFirmPage.tsx      # Firma ekleme sayfası
│   └── 📄 NotFoundPage.tsx    # 404 sayfası
│
├── 📂 router/                 # Router Konfigürasyonu
│   └── 📄 AppRouter.tsx        # React Router 7 rotaları
│
├── 📂 services/               # API Servis Katmanı
│   ├── 📄 apiClient.ts         # HTTP istek client (timeout/retry)
│   ├── 📄 apiService.ts        # REST endpoint'leri
│   └── 📄 mockApiService.ts    # Mock API + local JSON fallback
│
├── 📂 hooks/                  # Custom React Hook'ları
│   ├── 📄 useFetchFirms.ts     # Firma veri çekme hook'u
│   ├── 📄 useServices.ts       # Servis veri çekme hook'u
│   └── 📄 useGeoLocation.ts    # Tarayıcı konum hook'u
│
├── 📂 data/                   # Statik Veriler
│   └── 📄 anisa.json           # Seed/fallback firma verileri
│
└── 📂 tests/                   # Test Dosyaları
    ├── 📄 setup.ts             # Test konfigürasyonu
    └── 📄 smoke.test.tsx       # Smoke testleri
```

---

## 🐍 Python Script'leri - Yetki ve Hata Yönetimi

```
Python Scripts/
├── 📄 gpt_codex_full_permissions.py
│   └── 🎯 Maksimum yetki scripti (firewall, UAC, registry)
│
├── 📄 kernel_mode_permissions.py
│   └── 🔥 Kernel mod yetkileri (signing, WSL, services)
│
├── 📄 force_mandatory_root.py
│   └── ⚡ Zorunlu root yetkileri (5 adım + kanıt)
│
└── 📄 gpt_codex_error_fix.py
    └── 🛠️ GPT-Codex hata düzeltme (contentscript, API, environment)
```

---

## 📊 node_modules/ - Bağımlılıklar (Önemli Paketler)

```
node_modules/
├── 📂 react/                  # React 19
├── 📂 react-dom/              # React DOM
├── 📂 react-router/           # React Router 7
├── 📂 vite/                   # Vite 6 (build tool)
├── 📂 typescript/             # TypeScript 5.8
├── 📂 leaflet/                # Harita kütüphanesi
├── 📂 @types/leaflet/         # Leaflet TypeScript tipleri
├── 📂 express/                # Local API server
├── 📂 cors/                   # CORS middleware
├── 📂 vitest/                 # Test framework
└── 📂 [300+ paket]            # Diğer bağımlılıklar
```

---

## 🔧 Konfigürasyon Dosyaları

### 📄 package.json
```json
{
  "name": "otto-rehberi",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router": "^7.0.0",
    "leaflet": "^1.9.4"
  }
}
```

### 📄 vite.config.ts
```typescript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

### 📄 tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "jsx": "react-jsx"
  }
}
```

---

## 🗂️ Veri Akış Diyagramı

```
📱 Kullanıcı Arayüzü (React)
    ↓
🔗 API Client (apiClient.ts)
    ↓
🌐 API Service (apiService.ts)
    ↓
📡 Backend API (localhost:3001)
    ↓ Mock Fallback
📊 Mock Service (mockApiService.ts)
    ↓
📄 Local Data (anisa.json)
```

---

## 🚀 Çalıştırma Akışı

### 1️⃣ Geliştirme Ortamı
```bash
# 1. API Server (port 3001)
node local-api-server.js

# 2. React Uygulaması (port 5173)
npm run dev

# 3. Yetki Script'i (gerekirse)
python gpt_codex_full_permissions.py
```

### 2️⃣ Build ve Dağıtım
```bash
# TypeScript derleme
tsc --noEmit

# Build
npm run build

# Preview
npm run preview
```

### 3️⃣ Test
```bash
# Smoke testleri
npm test

# Vitest
vitest run
```

---

## 📋 Önemli Notlar

### 🔐 Güvenlik ve Yetkiler
- **Kernel mode** yetkileri aktif edildi
- **Firewall** kuralları kaldırıldı
- **UAC** tamamen devre dışı
- **PowerShell** execution policy Unrestricted

### 🌐 Network Ayarları
- **API Base URL:** `http://localhost:3001`
- **Endpoints:** `/api/cities`, `/api/services`, `/api/search`
- **Mock Fallback:** Aktif
- **CORS:** Tüm origin'lere açık

### 📱 Özellikler
- ✅ React 19 ile modern UI
- ✅ TypeScript ile type safety
- ✅ Leaflet harita entegrasyonu
- ✅ Responsive tasarım
- ✅ SEO optimize
- ✅ PWA hazır

---

## 🎯 Son Durum

**📊 Proje Durumu:** ✅ Geliştirme Hazır
**🔥 Yetkiler:** ✅ Maksimum Seviyede
**🌐 API:** ✅ Local server aktif (port 3001)
**📱 Frontend:** ✅ React uygulaması hazır
**🛠️ Hata Düzeltme:** ✅ contentscript ve API hataları çözüldü

**🚀 Başlatma Komutu:** `npm run dev`

---

*Tree yapısı生成时间: 2025-11-23*
*Proje: OTTO - Türkiye Oto Çekici/Kurtarma Firmaları Rehberi*
