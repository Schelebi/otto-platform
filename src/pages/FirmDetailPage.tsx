/**
 * KOD ADI: FIRM DETAIL PAGE — REAL API DETAIL + WHATSAPP ALWAYS
 * KOD YOLU (GÖRELİ): src/pages/FirmDetailPage.tsx
 *
 * KODUN AMACI (5):
 * 1) Firma detayını gerçek API’den almak.
 * 2) WhatsApp butonunu her durumda görünür tutmak.
 * 3) İletişim alanlarını “varsa göster” kuralına göre render etmek.
 * 4) Leaflet haritayı güvenli kurup cleanup yapmak.
 * 5) UI çökmeden L1–L2–L3 TRY ile devam etmek.
 *
 * REVİZYONLAR:
 * - REVİZYON NO: 2 bu sayfada yapıldı → apiService bağlandı, conditional contact eklendi.
 *
 * TALİMATLAR (ZORUNLU):
 * - L1–L2–L3 TRY modeli fetch ve mapte zorunlu.
 * - İletişim başlıkları veri yoksa asla görünmez.
 * - WhatsApp butonu görünür, numara yoksa disable kalır.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  ArrowLeft,
  MapPin,
  Phone,
  MessageCircle,
  Star,
  Clock,
  Globe,
  Mail,
  ExternalLink
} from 'lucide-react';
import { getWhatsAppLink } from '../services/mockApiService';
import { apiService } from '../services/apiService';
import { AnisaRecord } from '../types';

const FirmDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [firm, setFirm] = useState<AnisaRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    let alive = true;

    const loadFirm = async () => {
      // L1: Global Fetch Safety
      try {
        if (!id) return;

        setLoading(true);
        setError(false);

        // L2: Operational API Call
        const data = await apiService.getFirmDetail(parseInt(id, 10));

        // L3: Record-level State Update
        if (!alive) return;
        if (data) {
          setFirm(data);
        } else {
          setError(true);
        }
      } catch (err) {
        console.error("Detail fetch error", err);
        if (!alive) return;
        setError(true);
      } finally {
        if (alive) setLoading(false);
      }
    };

    loadFirm();
    return () => { alive = false; };
  }, [id]);

// Initialize Map
  useEffect(() => {
    try {
      if (!loading && firm && firm.lat && firm.lng && mapContainerRef.current) {
        // Fix Leaflet Icons
        const iconDefault = L.icon({
          iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
          iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
          shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        });
        L.Marker.prototype.options.icon = iconDefault;

        // Reset old map if any
        if (mapInstanceRef.current) {
          try { mapInstanceRef.current.remove(); } catch {}
          mapInstanceRef.current = null;
        }

        const map = L.map(mapContainerRef.current).setView([firm.lat, firm.lng], 14);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        L.marker([firm.lat, firm.lng])
          .addTo(map)
          .bindPopup(`<b>${firm.firma_adi}</b>`)
          .openPopup();

        mapInstanceRef.current = map;
      }
    } catch (mapError) {
      console.error("Leaflet map initialization failed on detail page", mapError);
    }

    return () => {
      try {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.remove();
          mapInstanceRef.current = null;
        }
      } catch (e) {
        console.warn("Leaflet map cleanup failed on detail page", e);
      }
    };
  }, [loading, firm]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Firma detayları yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error || !firm) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Firma Bulunamadı
          </h2>
          <p className="text-gray-600 mb-6">
            Aradığınız firma bulunamadı veya bir hata oluştu.
          </p>
          <button
            onClick={() => navigate(-1)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Geri Dön
          </button>
        </div>
      </div>
    );
  }

  const waLink = getWhatsAppLink(firm);
  const hasContactInfo = Boolean(
    firm?.adres_full || firm?.telefon || firm?.phones_json || firm?.email || firm?.website || firm?.google_maps_url
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Geri
          </button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2">
            {/* Firm Header */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <div className="flex flex-col md:flex-row gap-6">
                {/* Firm Image */}
                <div className="w-full md:w-48 h-48 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                  {firm.featured_image ? (
                    <img
                      src={firm.featured_image}
                      alt={firm.firma_adi}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <MapPin className="w-12 h-12" />
                    </div>
                  )}
                </div>

                {/* Firm Info */}
                <div className="flex-1">
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
                    {firm.firma_adi}
                  </h1>

                  <div className="flex items-center gap-4 mb-4">
                    <div className="flex items-center gap-1">
                      <Star className="w-5 h-5 text-yellow-400 fill-current" />
                      <span className="font-semibold text-gray-900">
                        {firm.puan}
                      </span>
                      <span className="text-gray-600">
                        ({firm.yorum_sayisi} yorum)
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-green-600">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm font-medium">7/24 Açık</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-gray-600 mb-4">
                    <MapPin className="w-4 h-4" />
                    <span>{firm.il}, {firm.ilce}</span>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row gap-3">
                    {firm.telefon && (
                      <a
                        href={`tel:${firm.telefon}`}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold flex items-center justify-center gap-2"
                      >
                        <Phone className="w-5 h-5" />
                        Ara
                      </a>
                    )}

                    {/* WhatsApp must always be visible */}
                    <a
                      href={waLink || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={(e) => !waLink && e.preventDefault()}
                    >
                      <MessageCircle className="w-5 h-5" />
                      WhatsApp
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Services */}
            {firm.hizmetler && (
              <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Hizmetler
                </h2>
                <div className="flex flex-wrap gap-2">
                  {firm.hizmetler.split(',').map((serviceName, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {serviceName.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Map */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Konum
              </h2>
              {firm.lat && firm.lng ? (
                <div
                  ref={mapContainerRef}
                  className="h-80 w-full rounded-lg overflow-hidden"
                ></div>
              ) : (
                <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
                  <MapPin className="w-8 h-8 mr-2" />
                  Konum bilgisi yok
                </div>
              )}
            </div>

            {/* Additional Info */}
            {(firm.adres_full || firm.email || firm.website) && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Ek Bilgiler
                </h2>

                <div className="space-y-3">
                  {firm.adres_full && (
                    <div className="flex items-start gap-3">
                      <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <div className="font-medium text-gray-900">Adres</div>
                        <div className="text-gray-600">{firm.adres_full}</div>
                      </div>
                    </div>
                  )}

                  {firm.email && (
                    <div className="flex items-center gap-3">
                      <Mail className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="font-medium text-gray-900">Email</div>
                        <a
                          href={`mailto:${firm.email}`}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          {firm.email}
                        </a>
                      </div>
                    </div>
                  )}

                  {firm.website && (
                    <div className="flex items-center gap-3">
                      <Globe className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="font-medium text-gray-900">Website</div>
                        <a
                          href={firm.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700 flex items-center gap-1"
                        >
                          {firm.website}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Contact Info */}
            {hasContactInfo && (
                <div>
                   <h3 className="text-lg font-bold text-gray-900 mb-4">İletişim Bilgileri</h3>
                   <ul className="space-y-3">
                     {firm.telefon && (
                       <li className="flex items-center gap-3">
                         <Phone className="w-5 h-5 text-blue-600" />
                         <a href={`tel:${firm.telefon}`} className="text-gray-900 hover:text-blue-600 transition-colors">
                           {firm.telefon}
                         </a>
                       </li>
                     )}

                     {firm.email && (
                       <li className="flex items-center gap-3">
                         <Mail className="w-5 h-5 text-blue-600" />
                         <a href={`mailto:${firm.email}`} className="text-gray-900 hover:text-blue-600 transition-colors">
                           {firm.email}
                         </a>
                       </li>
                     )}

                     {firm.website && (
                       <li className="flex items-center gap-3">
                         <Globe className="w-5 h-5 text-blue-600" />
                         <a href={firm.website} target="_blank" rel="noopener noreferrer" className="text-gray-900 hover:text-blue-600 transition-colors">
                           Website
                         </a>
                       </li>
                     )}

                     {firm.google_maps_url && (
                       <li className="flex items-center gap-3">
                         <MapPin className="w-5 h-5 text-blue-600" />
                         <a href={firm.google_maps_url} target="_blank" rel="noopener noreferrer" className="text-gray-900 hover:text-blue-600 transition-colors">
                           Google Maps
                         </a>
                       </li>
                     )}
                   </ul>
                 </div>
                )}

            {/* Rating Info */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Puan & Yorumlar
              </h3>
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">
                  {firm.puan}
                </div>
                <div className="flex justify-center mb-2">
                  {[1, 2, 3, 4, 5].map(star => (
                    <Star
                      key={star}
                      className={`w-5 h-5 ${
                        star <= firm.puan ? 'text-yellow-400 fill-current' : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <div className="text-gray-600">
                  {firm.yorum_sayisi} değerlendirme
                </div>

                {firm.google_review_url && (
                  <a
                    href={firm.google_review_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-3 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Google Yorumlarını Gör
                  </a>
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Hızlı İşlemler
              </h3>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/search')}
                  className="w-full bg-gray-100 text-gray-900 py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Diğer Firmaları Gör
                </button>

                {firm.google_maps_url && (
                  <a
                    href={firm.google_maps_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full bg-blue-100 text-blue-900 py-3 px-4 rounded-lg hover:bg-blue-200 transition-colors font-medium text-center"
                  >
                    Yol Tarifi Al
                  </a>
                )}
              </div>
            </div>

            {/* Safety Notice */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-yellow-800 mb-2">
                Güvenlik Uyarısı
              </h3>
              <p className="text-yellow-700 text-sm">
                Hizmet almadan önce firmayla fiyat ve hizmet detaylarını netleştirin.
                Acil durumlarda 112'yi arayın.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FirmDetailPage;
