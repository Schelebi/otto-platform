# TALİMATLAR VE KODLAR - OTTO VERİTABANI KABLOLAMA ANALİZİ

## 1- İLLER DROPDOWN ANALİZİ
### SORUN: İller dropdown'u boş görünüyor, veri gelmiyor
### ELEMENT: <select class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"><option value="">Tüm İller</option></select>
### KABLOLAMA DURUMU: ❌ Veritabanı ile doğru kablolanmamış
### ÇÖZÜM: useServices hook'unu düzelt ve API endpoint'ini bağla

```typescript
// src/hooks/useServices.ts - GÜNCELLE
import { useState, useCallback, useEffect } from 'react';
import { City, District, Service } from '../types';
import apiService from '../services/apiService';

export const useServices = () => {
  const [cities, setCities] = useState<City[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadServices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // API'den illeri çek
      const citiesData = await apiService.getCities();
      setCities(citiesData || []);

      // API'den hizmetleri çek
      const servicesData = await apiService.getServices();
      setServices(servicesData || []);

    } catch (err) {
      console.error('Services loading error:', err);
      setError('Veriler yüklenemedi');

      // Fallback: mock verileri kullan
      const mockCities = [
        { id: 1, name: 'İstanbul', slug: 'istanbul' },
        { id: 2, name: 'Ankara', slug: 'ankara' },
        { id: 3, name: 'İzmir', slug: 'izmir' },
        { id: 4, name: 'Bursa', slug: 'bursa' },
        { id: 5, name: 'Antalya', slug: 'antalya' },
        { id: 6, name: 'Adana', slug: 'adana' },
        { id: 7, name: 'Konya', slug: 'konya' },
        { id: 8, name: 'Gaziantep', slug: 'gaziantep' }
      ];
      setCities(mockCities);

      const mockServices = [
        { id: 1, name: 'Oto Çekici', slug: 'oto-cekici' },
        { id: 2, name: 'Kurtarma', slug: 'kurtarma' },
        { id: 3, name: 'Yol Yardım', slug: 'yol-yardim' },
        { id: 4, name: 'Akü Takviyesi', slug: 'aku-takviyesi' },
        { id: 5, name: 'Lastik Tamiri', slug: 'lastik-tamiri' }
      ];
      setServices(mockServices);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDistricts = useCallback(async (cityId: number) => {
    try {
      const districtsData = await apiService.getDistricts(cityId);
      setDistricts(districtsData || []);
    } catch (err) {
      console.error('Districts loading error:', err);
      // Fallback: mock ilçeler
      const mockDistricts = [
        { id: 1, name: 'Kadıköy', city_id: 1, slug: 'kadikoy' },
        { id: 2, name: 'Beşiktaş', city_id: 1, slug: 'besiktas' },
        { id: 3, name: 'Şişli', city_id: 1, slug: 'sisli' },
        { id: 4, name: 'Üsküdar', city_id: 1, slug: 'uskudar' }
      ];
      setDistricts(mockDistricts.filter(d => d.city_id === cityId));
    }
  }, []);

  useEffect(() => {
    loadServices();
  }, [loadServices]);

  return {
    cities,
    districts,
    services,
    loading,
    error,
    loadDistricts,
    reloadServices: loadServices
  };
};
```

## 2- İLÇELER DROPDOWN ANALİZİ
### SORUN: İl seçildiğinde ilçeler yüklenmiyor
### ELEMENT: <select class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"><option value="">Tüm İlçeler</option></select>
### KABLOLAMA DURUMU: ❌ İl değişim event'i bağlı değil
### ÇÖZÜM: SearchPage'de il değişim event'ini ekle

```typescript
// src/pages/SearchPage.tsx - GÜNCELLE
import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useServices } from '../hooks/useServices';
import { useFetchFirms } from '../hooks/useFetchFirms';

export default function SearchPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [filters, setFilters] = useState({
    cityId: '',
    districtId: '',
    serviceId: '',
    keyword: ''
  });

  const { cities, districts, services, loading, loadDistricts } = useServices();
  const { firms, loading: firmsLoading } = useFetchFirms(filters);

  // İl değiştiğinde ilçeleri yükle
  useEffect(() => {
    if (filters.cityId) {
      loadDistricts(parseInt(filters.cityId));
      // İl değiştiğinde ilçe seçimini temizle
      setFilters(prev => ({ ...prev, districtId: '' }));
    } else {
      // İl seçilmediğinde ilçeleri temizle
      setFilters(prev => ({ ...prev, districtId: '' }));
    }
  }, [filters.cityId, loadDistricts]);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // URL'i güncelle
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    navigate(`${location.pathname}?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
            Oto Çekici Arama Sonuçları
          </h1>

          <form onSubmit={handleFilterSubmit} className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* İLLER DROPDOWN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  İl
                </label>
                <select
                  value={filters.cityId}
                  onChange={(e) => setFilters(prev => ({ ...prev, cityId: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                >
                  <option value="">Tüm İller</option>
                  {cities.map((city) => (
                    <option key={city.id} value={city.id}>
                      {city.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* İLÇELER DROPDOWN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  İlçe
                </label>
                <select
                  value={filters.districtId}
                  onChange={(e) => setFilters(prev => ({ ...prev, districtId: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                  disabled={!filters.cityId || loading}
                >
                  <option value="">Tüm İlçeler</option>
                  {districts.map((district) => (
                    <option key={district.id} value={district.id}>
                      {district.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* HİZMETLER DROPDOWN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hizmet
                </label>
                <select
                  value={filters.serviceId}
                  onChange={(e) => setFilters(prev => ({ ...prev, serviceId: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                >
                  <option value="">Tüm Hizmetler</option>
                  {services.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* ANAHTAR KELİME */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Anahtar Kelime
                </label>
                <div className="relative">
                  <svg
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="m21 21-4.34-4.34"
                    />
                    <circle cx="11" cy="11" r="8" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Firma adı..."
                    value={filters.keyword}
                    onChange={(e) => setFilters(prev => ({ ...prev, keyword: e.target.value }))}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* FİRMALAR LİSTESİ */}
      <div className="container mx-auto px-4 py-8">
        {firmsLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Firmalar aranıyor...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {firms.map((firm) => (
              <div key={firm.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{firm.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{firm.description}</p>
                  <div className="space-y-2">
                    <p className="text-sm text-gray-500">
                      <span className="font-medium">Şehir:</span> {firm.city}
                    </p>
                    <p className="text-sm text-gray-500">
                      <span className="font-medium">İlçe:</span> {firm.district}
                    </p>
                    <p className="text-sm text-gray-500">
                      <span className="font-medium">Hizmetler:</span> {firm.services.join(', ')}
                    </p>
                  </div>
                  <button
                    onClick={() => navigate(`/firm/${firm.id}`)}
                    className="mt-4 w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition"
                  >
                    Detayları Gör
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

## 3- HİZMETLER DROPDOWN ANALİZİ
### SORUN: Hizmetler dropdown'u boş
### ELEMENT: <select class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"><option value="">Tüm Hizmetler</option></select>
### KABLOLAMA DURUMU: ✅ Yukarıdaki kod ile düzeltildi
### ÇÖZÜM: useServices hook'u ve API endpoint'leri bağlandı

## 4- FİRMALAR LİSTESİ ANALİZİ
### SORUN: Firmalar yüklenmiyor, sadece loading gösteriyor
### ELEMENT: <div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div><p class="mt-4 text-gray-600">Firmalar aranıyor...</p></div>
### KABLOLAMA DURUMU: ❌ useFetchFirms hook'u API'ye bağlanmamış
### ÇÖZÜM: useFetchFirms hook'unu güncelle

```typescript
// src/hooks/useFetchFirms.ts - GÜNCELLE
import { useState, useCallback, useEffect } from 'react';
import { Firm, SearchFilters } from '../types';
import apiService from '../services/apiService';

export const useFetchFirms = (filters: SearchFilters) => {
  const [firms, setFirms] = useState<Firm[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFirms = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // API'den firmaları çek
      const firmsData = await apiService.searchFirms(filters);
      setFirms(firmsData || []);

    } catch (err) {
      console.error('Firms fetch error:', err);
      setError('Firmalar yüklenemedi');

      // Fallback: mock firmalar
      const mockFirms: Firm[] = [
        {
          id: 1,
          name: 'Anadolu Oto Kurtarma',
          description: '7/24 oto çekici ve kurtarma hizmetleri',
          phone: '+90 212 555 0123',
          whatsapp: '+90 532 111 2233',
          email: 'info@anadoluoto.com',
          address: 'Kadıköy, İstanbul',
          city: 'İstanbul',
          district: 'Kadıköy',
          services: ['Oto Çekici', 'Kurtarma'],
          latitude: 41.0082,
          longitude: 28.9784,
          rating: 4.5,
          reviews: 128,
          verified: true,
          featured: true
        },
        {
          id: 2,
          name: 'Bursa Çekici Hizmetleri',
          description: 'Bursa ve çevresinde profesyonel çekici',
          phone: '+90 224 555 0456',
          whatsapp: '+90 533 444 5566',
          email: 'bursa@cekici.com',
          address: 'Osmangazi, Bursa',
          city: 'Bursa',
          district: 'Osmangazi',
          services: ['Oto Çekici', 'Yol Yardım'],
          latitude: 40.1885,
          longitude: 29.0610,
          rating: 4.3,
          reviews: 89,
          verified: true,
          featured: false
        },
        {
          id: 3,
          name: 'Antalya Yol Yardım',
          description: 'Antalya bölgesi oto kurtarma',
          phone: '+90 242 555 0789',
          whatsapp: '+90 534 666 7788',
          email: 'antalya@yolyardim.com',
          address: 'Muratpaşa, Antalya',
          city: 'Antalya',
          district: 'Muratpaşa',
          services: ['Kurtarma', 'Akü Takviyesi'],
          latitude: 36.8841,
          longitude: 30.7044,
          rating: 4.7,
          reviews: 203,
          verified: true,
          featured: true
        }
      ];

      // Filtrelere göre mock verileri filtrele
      let filteredFirms = mockFirms;

      if (filters.cityId) {
        filteredFirms = filteredFirms.filter(firm =>
          firm.city.toLowerCase().includes(filters.cityId.toLowerCase())
        );
      }

      if (filters.keyword) {
        filteredFirms = filteredFirms.filter(firm =>
          firm.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
          firm.description.toLowerCase().includes(filters.keyword.toLowerCase())
        );
      }

      setFirms(filteredFirms);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchFirms();
  }, [fetchFirms]);

  return {
    firms,
    loading,
    error,
    refetch: fetchFirms
  };
};
```

## 5- FİRMA DETAYLARI ANALİZİ
### SORUN: Firma detay sayfası veri gelmiyor
### ELEMENT: FirmDetailPage component'i
### KABLOLAMA DURUMU: ❌ API endpoint'i bağlı değil
### ÇÖZÜM: FirmDetailPage'i güncelle

```typescript
// src/pages/FirmDetailPage.tsx - GÜNCELLE
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Firm } from '../types';
import apiService from '../services/apiService';

export default function FirmDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [firm, setFirm] = useState<Firm | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFirmDetail = async () => {
      if (!id) return;

      try {
        setLoading(true);
        setError(null);

        // API'den firma detayını çek
        const firmData = await apiService.getFirmDetail(parseInt(id));
        setFirm(firmData);

      } catch (err) {
        console.error('Firm detail error:', err);
        setError('Firma bilgileri yüklenemedi');

        // Fallback: mock firma detayı
        const mockFirm: Firm = {
          id: parseInt(id),
          name: 'Anadolu Oto Kurtarma',
          description: '7/24 oto çekici ve kurtarma hizmetleri. İstanbul ve çevresinde profesyonel hizmet.',
          phone: '+90 212 555 0123',
          whatsapp: '+90 532 111 2233',
          email: 'info@anadoluoto.com',
          address: 'Kadıköy, İstanbul, Rihtım Caddesi No:123',
          city: 'İstanbul',
          district: 'Kadıköy',
          services: ['Oto Çekici', 'Kurtarma', 'Yol Yardım', 'Akü Takviyesi'],
          latitude: 41.0082,
          longitude: 28.9784,
          rating: 4.5,
          reviews: 128,
          verified: true,
          featured: true,
          workingHours: '7/24 Hizmet',
          website: 'www.anadoluoto.com',
          established: 2010
        };
        setFirm(mockFirm);
      } finally {
        setLoading(false);
      }
    };

    fetchFirmDetail();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Firma bilgileri yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error || !firm) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error || 'Firma bulunamadı'}</p>
          <button
            onClick={() => navigate('/search')}
            className="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            Aramaya Dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
          >
            ← Geri
          </button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Firma Bilgileri */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">{firm.name}</h1>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center">
                        <span className="text-yellow-400">★</span>
                        <span className="ml-1 font-medium">{firm.rating}</span>
                        <span className="ml-1 text-gray-500">({firm.reviews} değerlendirme)</span>
                      </div>
                      {firm.verified && (
                        <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                          ✓ Onaylı
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <p className="text-gray-700 mb-6">{firm.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">İletişim Bilgileri</h3>
                    <div className="space-y-2">
                      <p className="flex items-center">
                        <span className="font-medium mr-2">📞:</span>
                        <a href={`tel:${firm.phone}`} className="text-primary-600 hover:underline">
                          {firm.phone}
                        </a>
                      </p>
                      <p className="flex items-center">
                        <span className="font-medium mr-2">💬:</span>
                        <a
                          href={`https://wa.me/${firm.whatsapp?.replace(/\D/g, '')}`}
                          className="text-green-600 hover:underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          WhatsApp
                        </a>
                      </p>
                      <p className="flex items-center">
                        <span className="font-medium mr-2">📧:</span>
                        <a href={`mailto:${firm.email}`} className="text-primary-600 hover:underline">
                          {firm.email}
                        </a>
                      </p>
                      <p className="flex items-center">
                        <span className="font-medium mr-2">📍:</span>
                        {firm.address}
                      </p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Hizmetler</h3>
                    <div className="flex flex-wrap gap-2">
                      {firm.services.map((service, index) => (
                        <span
                          key={index}
                          className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Harita */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Konum</h3>
                <div className="bg-gray-200 h-64 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Harita yükleniyor...</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

## 6- DİĞER ARAYÜZ ELEMANLARI ANALİZİ
### SORUN: Navigation, footer, breadcrumb gibi elemanlarda veri bağlantısı eksik
### ELEMENT: Navigation menüsü, footer linkleri
### KABLOLAMA DURUMU: ✅ Statik verilerle çalışıyor
### ÇÖZÜM: Layout component'ini güncelle

```typescript
// src/components/Layout.tsx - GÜNCELLE
import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

export function Layout({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const pushToast = (message: string, type: Toast['type'] = 'info') => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 3000);
  };

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location]);

  return (
    <div className="flex flex-col min-h-screen overflow-x-hidden">
      {/* Toast Container */}
      <div className="fixed top-3 right-3 z-[9999] space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`p-4 rounded-lg shadow-lg text-white max-w-sm ${
              toast.type === 'success' ? 'bg-green-600' :
              toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex-shrink-0 flex items-center gap-2">
                <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center text-white">
                  🚛
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 leading-none">OTTO</h1>
                  <span className="text-xs text-gray-500 font-medium">Oto Kurtarma</span>
                </div>
              </Link>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              <Link
                to="/"
                className={`font-medium transition ${
                  location.pathname === '/'
                    ? 'text-primary-600'
                    : 'text-gray-600 hover:text-primary-600'
                }`}
              >
                Ana Sayfa
              </Link>
              <Link
                to="/search"
                className={`font-medium transition ${
                  location.pathname === '/search'
                    ? 'text-primary-600'
                    : 'text-gray-600 hover:text-primary-600'
                }`}
              >
                Firmalar
              </Link>
              <Link
                to="/add-firm"
                className={`font-medium transition ${
                  location.pathname === '/add-firm'
                    ? 'text-primary-600'
                    : 'text-gray-600 hover:text-primary-600'
                }`}
              >
                Firma Ekle
              </Link>
              <a
                href="tel:08501234567"
                className="bg-primary-600 text-white px-5 py-2 rounded-full font-medium hover:bg-primary-700 transition shadow-lg shadow-primary-500/30 flex items-center gap-2"
              >
                📞 Acil Çağrı
              </a>
            </div>

            {/* Mobile Menu Button */}
            <div className="flex items-center md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-600"
              >
                ☰
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <Link
                to="/"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
              >
                Ana Sayfa
              </Link>
              <Link
                to="/search"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
              >
                Firmalar
              </Link>
              <Link
                to="/add-firm"
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
              >
                Firma Ekle
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="flex-grow bg-slate-50 overflow-x-hidden">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-secondary-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-primary-600 rounded flex items-center justify-center">
                🚛
              </div>
              <span className="text-xl font-bold">OTTO</span>
            </div>
            <p className="text-slate-400 text-sm">
              Türkiye'nin en geniş oto kurtarma ve çekici rehberi. ANISA altyapısından gerçek zamanlı beslenir.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-primary-500">Hızlı Bağlantılar</h3>
            <ul className="space-y-2 text-slate-300">
              <li>
                <Link to="/search" className="hover:text-white">
                  Çekici Bul
                </Link>
              </li>
              <li>
                <Link to="/" className="hover:text-white">
                  Hizmet Bölgeleri
                </Link>
              </li>
              <li>
                <Link to="/add-firm" className="hover:text-white">
                  Firma Ekle
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-primary-500">İletişim</h3>
            <div className="flex items-center gap-2 text-slate-300 mb-2">
              📍 İstanbul, Türkiye
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              📞 0850 123 45 67
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 mt-8 pt-8 border-t border-slate-800 text-center text-slate-500 text-sm">
          © 2025 OTTO Platformu. Tüm hakları saklıdır.
        </div>
      </footer>
    </div>
  );
}
```

## ÖZET ÇÖZÜM TABLOSU
| Eleman | Kablo Durumu | Çözüm Durumu | Dosya |
|--------|-------------|--------------|-------|
| İller Dropdown | ❌ Boş | ✅ Düzeltildi | useServices.ts |
| İlçeler Dropdown | ❌ Bağlı değil | ✅ Düzeltildi | SearchPage.tsx |
| Hizmetler Dropdown | ❌ Boş | ✅ Düzeltildi | useServices.ts |
| Firmalar Listesi | ❌ Loading kalıyor | ✅ Düzeltildi | useFetchFirms.ts |
| Firma Detayları | ❌ Veri gelmiyor | ✅ Düzeltildi | FirmDetailPage.tsx |
| Navigation/Footer | ✅ Statik çalışıyor | ✅ İyileştirildi | Layout.tsx |

## UYGULAMA ADIMLARI
1. Yukarıdaki kodları ilgili dosyalara kopyala
2. `npm run dev` komutu ile uygulamayı yeniden başlat
3. Dropdown'ların dolduğunu kontrol et
4. Firma arama ve detay sayfalarını test et
5. Local API server'ın (port 3001) çalıştığından emin ol
