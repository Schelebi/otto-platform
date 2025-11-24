# README.md

## Projenin Özeti
OTTO, React 19 + Vite 6 + TypeScript ile yazılmış SPA tabanlı bir oto kurtarma rehberi uygulamasıdır. Frontend; HashRouter, lazy-loaded sayfalar (HomePage, SearchPage, FirmDetailPage) ve Tailwind tabanlı bileşenlerle inşa edilmiştir. Backend; Express.js + mysql2/promise kullanarak Google Cloud’daki `db6ctx4kvleywe` veritabanında barınan `anisa` tablosuna bağlanır. UI; şehir/ilçe/hizmet dropdown’larını gerçek verilerle doldurur, seçilen kombinasyona göre firmaları listeler ve detay sayfasında kayıtları doğrular.

## Klasör Yapısı
- `src/App.tsx`: Router + Layout + ErrorBoundary.
- `src/pages/*`: Home, Search, Detail, NotFound.
- `src/components/*`: Layout, FirmCard vb.
- `src/services/databaseService.ts`: Frontend’in kullandığı API istemcisi.
- `server.cjs`: Express API + MySQL bağlantısı.
- `src/hooks/useServices.ts`, `src/hooks/useFetchFirms.ts`: Cascade dropdown ve firma sorgu hook’ları.
- `src/types.ts`: ANISA şemasına uyumlu TypeScript tipleri.

## Çalıştırma
1. `npm install`
2. Backend: `node server.cjs` (veya package script)
3. Frontend: `npm run dev`
4. E2E/Test: Vitest + Playwright script’leri (`npm test`, `node playwright_test.js`).

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
1. Uygulama açıldığında `useServices` hook’u `/api/cities` + `/api/services` çağırılarıyla dropdown’ları doldurur.
2. İl seçildiğinde `loadDistricts(selectedCity)` çağrısı `/api/districts/<city>` endpoint’ini tetikler; ilçe dropdown sadece o ile ait değerleri gösterir.
3. `SearchPage` formu submit edildiğinde tüm filtreler URLSearchParams ile kaydedilir ve `useFetchFirms` hook’u `/api/firms/search` endpoint’ini tetikler.
4. Firma kartı seçildiğinde `/firm/:id` rotası açılır, `apiService.getFirmDetail` çağrısı ile detay verisi doğrulanır.

---

## TALİMAT + KOD PATCHLERİ (arayüz – veritabanı kablolaması)

### 1) `server.cjs` – Şehir/İlçe/Hizmet + Arama API’larını DB’ye bağla
```js
const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');

const app = express();
const PORT = process.env.API_PORT || 3001;

const dbConfig = {
  host: process.env.DB_HOST || '35.214.224.135',
  user: process.env.DB_USER || 'uwcw1gm1sor8u',
  password: process.env.DB_PASSWORD || 'g05jkizfzjdp',
  database: process.env.DB_NAME || 'db6ctx4kvleywe',
  charset: 'utf8mb4',
  waitForConnections: true
};

const slugify = (value = '') =>
  value.toString().trim().toLowerCase()
    .replace(/ı/g, 'i').replace(/ğ/g, 'g').replace(/ü/g, 'u')
    .replace(/ş/g, 's').replace(/ö/g, 'o').replace(/ç/g, 'c')
    .replace(/[^a-z0-9-\s]/g, '')
    .replace(/\s+/g, '-');

let db;

async function initializeDatabase() {
  db = await mysql.createConnection(dbConfig);
  console.log('✅ MySQL bağlantısı hazır');
}

app.use(cors());
app.use(express.json());

app.get('/api/cities', async (req, res) => {
  try {
    const [rows] = await db.execute(
      'SELECT il AS name, MIN(il_id) AS il_id FROM anisa WHERE il_id <> 0 AND il IS NOT NULL GROUP BY il ORDER BY il'
    );
    const cities = rows.map(row => ({
      id: String(row.il_id ?? row.name),
      name: row.name,
      slug: slugify(row.name)
    }));
    res.json({ cities });
  } catch (error) {
    console.error('Cities API error:', error);
    res.status(500).json({ error: 'İller yüklenemedi' });
  }
});

app.get('/api/districts/:city', async (req, res) => {
  try {
    const cityName = decodeURIComponent(req.params.city);
    const [rows] = await db.execute(
      'SELECT DISTINCT ilce_id, ilce FROM anisa WHERE il = ? AND ilce_id <> 0 AND ilce IS NOT NULL ORDER BY ilce',
      [cityName]
    );
    const districts = rows.map(row => ({
      id: String(row.ilce_id ?? row.ilce),
      name: row.ilce,
      slug: slugify(row.ilce),
      city_id: cityName
    }));
    res.json({ districts });
  } catch (error) {
    console.error('Districts API error:', error);
    res.status(500).json({ error: 'İlçeler yüklenemedi' });
  }
});

app.get('/api/services', async (req, res) => {
  try {
    const [rows] = await db.execute(
      'SELECT DISTINCT hizmetler FROM anisa WHERE hizmetler IS NOT NULL AND hizmetler <> "" ORDER BY hizmetler'
    );
    const services = rows.map(row => ({
      id: slugify(row.hizmetler),
      name: row.hizmetler,
      slug: slugify(row.hizmetler),
      description: row.hizmetler
    }));
    res.json({ services });
  } catch (error) {
    console.error('Services API error:', error);
    res.status(500).json({ error: 'Hizmetler yüklenemedi' });
  }
});

app.get('/api/firms/search', async (req, res) => {
  try {
    const { cityId, districtId, serviceId, keyword } = req.query;
    let query = 'SELECT * FROM anisa WHERE aktif = 1';
    const params = [];

    if (serviceId) { query += ' AND hizmetler = ?'; params.push(serviceId); }
    if (cityId)    { query += ' AND il = ?'; params.push(cityId); }
    if (districtId){ query += ' AND ilce = ?'; params.push(districtId); }
    if (keyword) {
      query += ' AND (firma_adi LIKE ? OR all_hepsi LIKE ?)';
      params.push(`%${keyword}%`, `%${keyword}%`);
    }

    query += ' ORDER BY id DESC LIMIT 50';
    const [rows] = await db.execute(query, params);

    const firms = rows.map(row => ({
      id: row.id,
      name: row.firma_adi || 'İsimsiz Firma',
      phone: row.telefon || '',
      whatsapp: row.whatsapp || '',
      email: row.email || '',
      address: row.adres_full || row.adres || '',
      city: row.il || '',
      district: row.ilce || '',
      hizmetler: row.hizmetler || '',
      latitude: row.lat != null ? Number(row.lat) : null,
      longitude: row.lng != null ? Number(row.lng) : null,
      rating: row.puan != null ? Number(row.puan) : 0,
      reviews: row.yorum_sayisi != null ? Number(row.yorum_sayisi) : 0,
      verified: !!row.aktif,
      featured_image: row.featured_image || ''
    }));
    res.json({ firms });
  } catch (error) {
    console.error('Firms search API error:', error);
    res.status(500).json({ error: 'Firmalar yüklenemedi' });
  }
});

app.get('/api/firms/:id', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM anisa WHERE id = ?', [req.params.id]);
    if (!rows.length) {
      return res.status(404).json({ error: 'Firma bulunamadı' });
    }
    const row = rows[0];
    res.json({
      firm: {
        id: row.id,
        name: row.firma_adi,
        phone: row.telefon,
        whatsapp: row.whatsapp,
        email: row.email,
        address: row.adres_full || row.adres || '',
        city: row.il,
        district: row.ilce,
        hizmetler: row.hizmetler,
        latitude: row.lat != null ? Number(row.lat) : null,
        longitude: row.lng != null ? Number(row.lng) : null,
        rating: row.puan != null ? Number(row.puan) : 0,
        reviews: row.yorum_sayisi != null ? Number(row.yorum_sayisi) : 0,
        verified: !!row.aktif
      }
    });
  } catch (error) {
    console.error('Firm detail API error:', error);
    res.status(500).json({ error: 'Firma detayı yüklenemedi' });
  }
});

initializeDatabase().then(() => {
  app.listen(PORT, () => console.log(`🚀 API ${PORT} portunda`));
});
```

### 2) `src/services/databaseService.ts` – Frontend API istemcisi güncelle
```ts
export class DatabaseService {
  private static instance: DatabaseService;
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';
  }

  static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  async getCities(): Promise<City[]> {
    const response = await fetch(`${this.baseUrl}/api/cities`);
    if (!response.ok) throw new Error('İller yüklenemedi');
    return (await response.json()).cities || [];
  }

  async getDistricts(city: string): Promise<District[]> {
    if (!city) return [];
    const response = await fetch(
      `${this.baseUrl}/api/districts/${encodeURIComponent(city)}`
    );
    if (!response.ok) throw new Error('İlçeler yüklenemedi');
    return (await response.json()).districts || [];
  }

  async getServices(): Promise<Service[]> {
    const response = await fetch(`${this.baseUrl}/api/services`);
    if (!response.ok) throw new Error('Hizmetler yüklenemedi');
    return (await response.json()).services || [];
  }

  async searchFirms(filters: SearchFilters): Promise<Firm[]> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value.toString());
    });
    const response = await fetch(`${this.baseUrl}/api/firms/search?${params}`);
    if (!response.ok) throw new Error('Firmalar yüklenemedi');
    return (await response.json()).firms || [];
  }

  async getFirmDetail(id: number): Promise<Firm> {
    const response = await fetch(`${this.baseUrl}/api/firms/${id}`);
    if (!response.ok) throw new Error('Firma detayı yüklenemedi');
    return (await response.json()).firm;
  }
}
```

### 3) `src/hooks/useServices.ts` – Cascade mantığı için hook
```ts
import { useState, useCallback, useEffect } from 'react';
import { City, District, Service } from '../types';
import { DatabaseService } from '../services/databaseService';

export const useServices = () => {
  const [cities, setCities] = useState<City[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadInitial = useCallback(async () => {
    try {
      setLoading(true);
      const db = DatabaseService.getInstance();
      const [citiesData, servicesData] = await Promise.all([
        db.getCities(),
        db.getServices()
      ]);
      setCities(citiesData);
      setServices(servicesData);
      setError(null);
    } catch (err) {
      console.error('Initial load error:', err);
      setError('API bağlantısı yok – demo veriler kullanılabilir');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDistricts = useCallback(async (cityId?: string) => {
    try {
      if (!cityId) {
        setDistricts([]);
        return [];
      }
      const db = DatabaseService.getInstance();
      const districtsData = await db.getDistricts(cityId);
      setDistricts(districtsData);
      return districtsData;
    } catch (err) {
      console.error('District load error:', err);
      setDistricts([]);
      setError('İlçeler yüklenemedi');
      return [];
    }
  }, []);

  useEffect(() => {
    loadInitial();
  }, [loadInitial]);

  return {
    cities,
    districts,
    services,
    loading,
    error,
    loadDistricts,
    reload: loadInitial
  };
};
```

### 4) `src/pages/SearchPage.tsx` – İl/İlçe UI akışı
```tsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useServices } from '../hooks/useServices';
import { useFetchFirms } from '../hooks/useFetchFirms';
import { Search, MapPin, List, Grid } from 'lucide-react';

const SearchPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { cities, districts, services, loading, error, loadDistricts } = useServices();

  const [filters, setFilters] = useState({
    cityId: '',
    districtId: '',
    serviceId: '',
    keyword: ''
  });

  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'map'>('grid');
  const { firms, loading: firmsLoading } = useFetchFirms(filters);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setFilters({
      cityId: params.get('cityId') || '',
      districtId: params.get('districtId') || '',
      serviceId: params.get('serviceId') || '',
      keyword: params.get('keyword') || ''
    });
  }, [location.search]);

  useEffect(() => {
    if (filters.cityId) {
      loadDistricts(filters.cityId);
    } else {
      loadDistricts('');
    }
  }, [filters.cityId, loadDistricts]);

  const handleFilterChange = (key: string, value: string) => {
    if (key === 'cityId') {
      setFilters(prev => ({ ...prev, cityId: value, districtId: '' }));
      loadDistricts(value);
      return;
    }
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    navigate(`${location.pathname}?${params.toString()}`);
  };

  // ... JSX içinde district dropdown -> districts state
};
```

### 5) `src/hooks/useFetchFirms.ts` – Filtreli sorgu hook’u
```ts
import { useState, useEffect } from 'react';
import { Firm } from '../types';
import { DatabaseService } from '../services/databaseService';

export function useFetchFirms(filters: {
  cityId?: string;
  districtId?: string;
  serviceId?: string;
  keyword?: string;
}) {
  const [firms, setFirms] = useState<Firm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const db = DatabaseService.getInstance();
        const data = await db.searchFirms(filters);
        if (!alive) return;
        setFirms(data);
        setError(null);
      } catch (err) {
        console.error('Firms fetch error:', err);
        if (alive) {
          setFirms([]);
          setError('Firmalar yüklenemedi.');
        }
      } finally {
        alive && setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [filters.cityId, filters.districtId, filters.serviceId, filters.keyword]);

  return { firms, loading, error };
}
```

Bu talimat ve kod blokları uygulandığında:
- İl dropdown, DB’den gelen gerçek il_id’leri kullanır.
- İlçe dropdown, seçilen il’e göre anında güncellenir.
- Hizmet filtresi aynı tablo üzerinden slug’lanır.
- Arama/Detay çağrıları tek tabloda tüm filtreleri uygulayarak doğru kayıtları döndürür.
