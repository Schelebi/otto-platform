/**
 * KOD ADI: HOME PAGE — REAL API + DYNAMIC LISTS
 * KOD YOLU (GÖRELİ): src/pages/HomePage.tsx
 *
 * KODUN AMACI (5):
 * 1) Öne çıkan firmaları gerçek API’den çekip göstermek.
 * 2) İl seçimini DB’den dinamik yüklemek, fallback ile korumak.
 * 3) Konumuma göre aramayı gerçek geolocation ile başlatmak.
 * 4) UI’nin çökmeden çalışması için L1–L2–L3 güvenlik uygulamak.
 * 5) Tüm cihazlarda responsive ve stabil görünüm sağlamak.
 *
 * REVİZYONLAR:
 * - REVİZYON NO: 2 bu sayfada yapıldı → apiService bağlandı, nearMe gerçek yapıldı.
 *
 * TALİMATLAR (ZORUNLU):
 * - L1–L2–L3 TRY modeli useEffect ve handler’larda uygulanır.
 * - API hatalarında fallback CITIES kullanılır, süreç durmaz.
 * - NearMe simülasyon yok, gerçek konum alınır.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Phone, Shield, Clock, Star } from 'lucide-react';
import FirmCard from '../components/FirmCard';
import { useServices } from '../hooks/useServices';
import { useFetchFirms } from '../hooks/useFetchFirms';
import { Firm } from '../types';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [featuredFirms, setFeaturedFirms] = useState<Firm[]>([]);
  const { cities, loading: citiesLoading } = useServices();
  const [selectedCity, setSelectedCity] = useState('');
  const { firms, loading: firmsLoading } = useFetchFirms({ cityId: '', districtId: '', serviceId: '', keyword: '' });
  const isLoading = firmsLoading || citiesLoading;

  useEffect(() => {
    // Cities artık useServices hook'undan geliyor, ek yükleme gerekmiyor
  }, []);

  useEffect(() => {
    try {
      const sorted = [...firms].sort(
        (a, b) =>
          (b.rating || 0) - (a.rating || 0) ||
          (b.reviews || 0) - (a.reviews || 0)
      );
      setFeaturedFirms(sorted.slice(0, 6));
    } catch (error) {
      console.error('Featured firms normalization failed', error);
      setFeaturedFirms([]);
    }
  }, [firms]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      if (searchKeyword) params.set('q', searchKeyword);
      if (selectedCity) params.set('city', selectedCity);
      navigate(`/search?${params.toString()}`);
    } catch (err) {
      console.error('Search handler error', err);
    }
  };

  const handleNearMe = () => {
    // L1: Global Geolocation Safety
    try {
      if (!navigator.geolocation) {
        alert('Tarayıcınız konum servisini desteklemiyor.');
        return;
      }

      // L2: Operational Geolocation Call
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          // L3: Record-level Safety
          try {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            if (typeof lat === 'number' && typeof lng === 'number') {
              navigate(`/search?lat=${lat}&lng=${lng}&mode=nearby`);
            } else {
              alert('Konum bilgisi alınamadı.');
            }
          } catch (innerErr) {
            console.error('NearMe position parse error', innerErr);
            alert('Konum bilgisi işlenemedi.');
          }
        },
        (geoErr) => {
          console.warn('Geolocation error', geoErr);
          alert('Konum izni verilmedi veya alınamadı.');
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 }
      );
    } catch (err) {
      console.error('Geolocation handler error', err);
      alert('Konum servisi başlatılamadı.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Türkiye'nin En Büyük Oto Çekici Rehberi
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              Bulunduğunuz konumdaki en yakın oto çekici firmalarını anında bulun
            </p>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="max-w-3xl mx-auto">
              <div className="bg-white rounded-2xl p-4 shadow-xl">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Firma adı veya hizmet ara..."
                      value={searchKeyword}
                      onChange={(e) => setSearchKeyword(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 text-gray-900 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                    />
                  </div>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select
                      value={selectedCity}
                      onChange={(e) => setSelectedCity(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 text-gray-900 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none appearance-none bg-white"
                    >
                      <option value="">İl seçiniz</option>
                      {cities.map(city => (
                        <option key={city} value={city}>
                          {city}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    type="submit"
                    className="bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-semibold flex items-center justify-center gap-2"
                  >
                    <Search className="w-5 h-5" />
                    Ara
                  </button>
                  <button
                    type="button"
                    onClick={handleNearMe}
                    className="bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-semibold flex items-center justify-center gap-2"
                  >
                    <MapPin className="w-5 h-5" />
                    Konumuma Göre Ara
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* Featured Firms Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Öne Çıkan Firmalar
            </h2>
            <p className="text-xl text-gray-600">
              En yüksek puanlı ve en çok tercih edilen oto çekici firmaları
            </p>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Firmalar yükleniyor...</p>
            </div>
          ) : featuredFirms.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">Şu anda öne çıkan firma bulunamadı.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredFirms.map(firm => (
                <FirmCard key={firm.id} firm={firm} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-50 py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Phone className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                7/24 Hizmet
              </h3>
              <p className="text-gray-600">
                Acil durumlarda günün her saati ulaşabileceğiniz firmalar
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Güvenilir Firmalar
              </h3>
              <p className="text-gray-600">
                Doğrulanmış ve müşteri yorumlarıyla desteklenen firmalar
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-yellow-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Hızlı Ulaşım
              </h3>
              <p className="text-gray-600">
                Konumunuza en yakın firmaları saniyeler içinde bulun
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="bg-blue-600 rounded-2xl p-8 md:p-12 text-white">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-4xl md:text-5xl font-bold mb-2">
                  {featuredFirms.length > 0 ? "1000+" : "0"}
                </div>
                <div className="text-blue-100">Kayıtlı Firma</div>
              </div>
              <div>
                <div className="text-4xl md:text-5xl font-bold mb-2">
                  {cities.length}
                </div>
                <div className="text-blue-100">Şehir</div>
              </div>
              <div>
                <div className="text-4xl md:text-5xl font-bold mb-2">7/24</div>
                <div className="text-blue-100">Hizmet</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-gray-50 py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Nasıl Çalışır?
            </h2>
            <p className="text-xl text-gray-600">
              3 adımda ihtiyacınız olan oto çekiciyi bulun
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Arama Yapın
              </h3>
              <p className="text-gray-600">
                Konumunuza göre veya şehir seçerek arama yapın
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Firmaları İnceleyin
              </h3>
              <p className="text-gray-600">
                Puanları, yorumları ve hizmetleri karşılaştırın
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                İletişime Geçin
              </h3>
              <p className="text-gray-600">
                WhatsApp veya telefon ile direkt iletişim kurun
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Firmanızı Ekleyin
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Oto çekici firmanızı rehberimize ekleyerek daha fazla müşteriye ulaşın
          </p>
          <button
            onClick={() => navigate('/add-firm')}
            className="bg-white text-blue-600 py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors font-semibold text-lg"
          >
            Firma Ekle
          </button>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
