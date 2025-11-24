import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useServices } from '../hooks/useServices';
import { useFetchFirms } from '../hooks/useFetchFirms';
import { useFirmsByCity } from '../hooks/useFirmsByCity';
import { Search, MapPin, List, Grid, Image } from 'lucide-react';
import FirmCard from '../components/FirmCard';
import { Firm, SearchFilters } from '../types';

const SearchPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { cities, services, loading, error } = useServices();
  // talimat 2g İlçe Dropdown Güncelleme düzeltildi - districts state'i kullanılıyor
  const [filters, setFilters] = useState<SearchFilters>({
    cityId: '',
    serviceId: '',
    keyword: ''
  });

  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'map'>('grid');
  const [showOnlyWithImages, setShowOnlyWithImages] = useState(false);
  const { firms, loading: firmsLoading } = useFetchFirms(filters);

  // İl bazlı firma araması için
  const { firms: cityFirms, loading: cityFirmsLoading, error: cityFirmsError } = useFirmsByCity(filters.cityId || null);

  // İlgili firmaları belirle: eğer il seçiliyse il bazlı firmaları kullan, değilse normal aramayı kullan
  const displayFirms = filters.cityId ? cityFirms : firms;
  const displayLoading = filters.cityId ? cityFirmsLoading : firmsLoading;
  const displayError = filters.cityId ? cityFirmsError : error;

  // Resimli firmaları filtrele
  const filteredFirms = showOnlyWithImages
    ? displayFirms.filter(firm => firm.featured_image && firm.featured_image.trim() !== '')
    : displayFirms;

  useEffect(() => {
    try {
      const params = new URLSearchParams(location.search);
      setFilters({
        cityId: params.get('cityId') || '',
        serviceId: params.get('serviceId') || '',
        keyword: params.get('keyword') || ''
      });
    } catch (error) {
      console.error('URL parse error:', error);
    }
  }, [location.search]);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value as string);
    });
    navigate(`${location.pathname}?${params.toString()}`);
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters({ ...filters, [key]: value });

    // URL parametrelerini anında güncelle
    const params = new URLSearchParams();
    Object.entries({ ...filters, [key]: value }).forEach(([k, v]) => {
      if (v) params.set(k, v as string);
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
            {/* LOADING VE ERROR STATE */}
            {loading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-gray-600">Veriler yükleniyor...</span>
              </div>
            )}

            {error && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  İl
                </label>
                <select
                  value={filters.cityId}
                  onChange={(e) => handleFilterChange('cityId', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                >
                  <option value="">Tüm İller</option>
                  {cities.map((city) => (
                    <option key={city.id} value={city.name}>
                      {city.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hizmet
                </label>
                <select
                  value={filters.serviceId}
                  onChange={(e) => handleFilterChange('serviceId', e.target.value)}
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Anahtar Kelime
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Firma adı..."
                    value={filters.keyword}
                    onChange={(e) => handleFilterChange('keyword', e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </form>

          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-gray-600">
              {firmsLoading ? 'Aranıyor...' : `${firms.length} firma bulundu`}
            </div>
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white shadow-sm text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="Liste Görünümü"
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-white shadow-sm text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="Grid Görünümü"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'map'
                    ? 'bg-white shadow-sm text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="Harita Görünümü"
              >
                <MapPin className="w-4 h-4" />
              </button>
              <div className="border-l border-gray-200 mx-2"></div>
              <button
                onClick={() => setShowOnlyWithImages(!showOnlyWithImages)}
                className={`p-2 rounded-md transition-colors flex items-center gap-1 ${
                  showOnlyWithImages
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="Sadece Resimli Firmalar"
              >
                <Image className="w-4 h-4" />
                <span className="text-xs font-medium">Resimli</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {displayLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">
              {filters.cityId ? `${filters.cityId} şehrindeki firmalar aranıyor...` : 'Firmalar aranıyor...'}
            </p>
          </div>
        ) : displayError ? (
          <div className="text-center py-12">
            <p className="text-red-600">{displayError}</p>
          </div>
        ) : filteredFirms.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">
              {showOnlyWithImages
                ? 'Resimli firma bulunamadı.'
                : filters.cityId
                  ? `${filters.cityId} şehrinde firma bulunamadı.`
                  : 'Firma bulunamadı.'
              }
            </p>
          </div>
        ) : (
          <div className={`grid gap-6 ${
            viewMode === 'list' ? 'grid-cols-1' :
            viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' :
            'grid-cols-1'
          }`}>
            {filteredFirms.map((firm) => (
              <FirmCard key={firm.id} firm={firm} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
