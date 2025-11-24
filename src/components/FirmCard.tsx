/**
 * KOD ADI: FIRM CARD — ANISA REAL UI CARD
 * KOD YOLU (GÖRELİ): src/components/FirmCard.tsx
 *
 * KODUN AMACI (5):
 * 1) ANISA kaydını güvenli ve responsive kart olarak göstermek.
 * 2) WhatsApp butonunu tüm firmalarda zorunlu ve stabil tutmak.
 * 3) Telefon/phones_json’dan WhatsApp linkini doğru türetmek.
 * 4) Eksik görsel ve veri durumlarında UI kırılmasını engellemek.
 * 5) Detay sayfasına güvenli yönlendirme sağlamak.
 *
 * REVİZYONLAR:
 * - REVİZYON NO: 2 bu sayfada yapıldı → WhatsApp zorunlu, rating gizleme, fallback image güçlendirildi.
 *
 * TALİMATLAR (ZORUNLU):
 * - L1–L2–L3 TRY modeli render ve click akışlarında uygulanır.
 * - WhatsApp butonu her zaman görünür; link yoksa disable davranır.
 * - Rating/yorum sayısı boşsa badge ve metin gösterilmez.
 * - featured_image yoksa lokal fallback kullanılır.
 * - Responsive: tüm cihazlarda taşma/bozulma olmayacak şekilde tasarlanır.
 */

import React from 'react';
import { AnisaRecord } from '../types';
import { MapPin, Phone, Star, Navigation, MessageCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getWhatsAppLink } from '../services/mockApiService';

interface FirmCardProps {
  firm: AnisaRecord;
}

const FALLBACK_IMAGES: string[] = [
  'https://placehold.co/600x400?text=OTTO',
  'https://placehold.co/600x400?text=Oto+Cekici',
];

export const FirmCard: React.FC<FirmCardProps> = ({ firm }) => {
  if (!firm) return null;

  const navigate = useNavigate();

  // L1: GLOBAL COMPONENT WITH 3-LAYER PROTECTION
  try {
    // L2: OPERATIONAL DATA PROCESSING
    try {
      const waLink = getWhatsAppLink(firm?.phone || '');
      const hasRating =
        typeof firm.rating === 'number' &&
        firm.rating > 0;

      const imgSrc = firm.featured_image
        ? firm.featured_image.replace(/=s0=s0=s0$/, '').replace(/=w\d+-h\d+-k-no=s0$/, '=s0-k-no')
        : FALLBACK_IMAGES[0];

      // Debug: featured_image'i logla
      console.log('🖼️ FirmCard Debug:', {
        firmName: firm.name,
        featured_image: firm.featured_image,
        imgSrc: imgSrc,
      });

      // L3: RECORD-LEVEL NAVIGATION
      const goDetail = () => {
        try {
          if (firm?.id != null) {
            navigate(`/firm/${firm.id}`);
          } else {
            console.warn('L3: No firm ID for navigation');
          }
        } catch (navErr) {
          console.error('L3: Navigation failed:', navErr);
          // L3 Fallback: Hard redirect
          try {
            window.location.href = `/firm/${firm?.id || ''}`;
          } catch (redirectErr) {
            console.error('L3: Hard redirect failed:', redirectErr);
          }
        }
      };

    return (
      <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden border border-gray-100 flex flex-col h-full w-full min-w-0">
        {/* Image Section */}
        <div className="relative h-48 sm:h-40 bg-gray-100">
          <img
            src={imgSrc}
            alt={firm.name || 'Firma'}
            className="w-full h-full object-cover"
            onError={(e) => {
              const el = e.target as HTMLImageElement;
              el.src = FALLBACK_IMAGES[1];
            }}
          />
          {hasRating && (
            <div className="absolute top-3 right-3 bg-white/95 backdrop-blur px-2 py-1 rounded-md flex items-center gap-1 text-sm font-bold text-amber-500 shadow-sm">
              <Star size={14} fill="currentColor" />
              <span>{firm.rating}</span>
            </div>
          )}
        </div>

        {/* Content Section */}
        <div className="p-4 flex flex-col flex-grow min-w-0">
          <div className="mb-2">
            <span className="inline-block text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full uppercase tracking-wider">
              {firm.city || 'İl'} / {firm.district || 'İlçe'}
            </span>
          </div>

          <h3
            className="text-lg font-bold text-gray-900 mb-1 line-clamp-1 break-words min-w-0"
            title={firm.name}
          >
            {firm.name || 'İsimsiz Firma'}
          </h3>

          <p className="text-gray-500 text-sm mb-4 line-clamp-2 flex-grow break-words min-w-0">
            {firm.services?.join(', ') || ''}
          </p>

          {/* Rating row (only if exists) */}
          {hasRating && (
            <div className="flex items-center gap-2 text-sm text-gray-700 mb-2">
              <Star size={14} className="text-amber-500" fill="currentColor" />
              <span className="font-semibold">{firm.rating}</span>
              <span className="text-gray-500">({firm.reviews || 0} yorum)</span>
            </div>
          )}

          <div className="space-y-3 mt-auto">
            {(firm.mahalle || firm.sokak) && (
              <div className="flex items-center gap-2 text-gray-600 text-sm min-w-0">
                <MapPin size={16} className="text-gray-400 flex-shrink-0" />
                <span className="truncate">
                  {firm.mahalle ? `${firm.mahalle}, ` : ''}
                  {firm.sokak || ''}
                </span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-2 mt-4">
              {/* WhatsApp Button - ZORUNLU */}
              <a
                href={waLink || '#'}
                target="_blank"
                rel="noreferrer"
                onClick={(e) => !waLink && e.preventDefault()}
                className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-sm font-bold text-white transition hover:scale-[1.02] shadow-sm flex-1 ${
                  !waLink ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                style={{ backgroundColor: '#25D366' }}
              >
                <MessageCircle size={18} />
                WhatsApp
              </a>

              {/* Call Button */}
              {firm.phone ? (
                <a
                  href={`tel:${firm.phone}`}
                  className="flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-900 py-2 px-3 rounded-lg text-sm font-medium transition flex-1"
                >
                  <Phone size={16} />
                  Ara
                </a>
              ) : (
                <span className="flex items-center justify-center bg-slate-50 text-slate-400 py-2 px-3 rounded-lg text-sm flex-1">
                  Telefon Yok
                </span>
              )}

              {/* Detail Button */}
              <button
                onClick={goDetail}
                className="flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white py-2 px-3 rounded-lg text-sm font-medium transition flex-1"
                type="button"
              >
                <Navigation size={16} />
                Detay
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  } catch (operationalErr) {
        console.error('L2: Operational data processing failed:', operationalErr);
        // L2 Fallback: Minimal render
        try {
          return (
            <div className="p-4 border border-yellow-200 rounded text-yellow-600 bg-yellow-50">
              <div className="font-semibold">{firm?.name || 'Firma'}</div>
              <div className="text-sm">{firm?.city || 'Şehir'}</div>
            </div>
          );
        } catch (fallbackErr) {
          console.error('L2: Fallback render failed:', fallbackErr);
          throw operationalErr;
        }
      }
    } catch (globalErr) {
      console.error('L1: Global component error:', globalErr);
      return (
        <div className="p-4 border border-red-200 rounded text-red-600 bg-red-50">
          Kart yüklenemedi
        </div>
      );
    }
};

export default FirmCard;
