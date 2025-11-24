/**
 * 1) KOD ADI:
 * MockApiService (WhatsApp ve Yardımcı Fonksiyonlar)
 *
 * 2) KOD YOLU (GÖRELİ):
 * src/services/mockApiService.ts
 *
 * 3) KODUN AMACI (5 MADDE):
 * - WhatsApp linki oluşturma fonksiyonu sağlamak
 * - Mock API servisleri için yardımcı fonksiyonlar sunmak
 * - UI component'lerinin bağımlılıklarını karşılamak
 * - Geçici veri ve test senaryolarını desteklemek
 * - Gerçek API servislerine yedek olmak
 *
 * 4) KODLA İLGİLİ TÜM REVİZYONLAR:
 * - Yeni dosya oluşturuldu
 * - getWhatsAppLink fonksiyonu eklendi
 * - Mock API yardımcıları eklendi
 *
 * 5) KODLA İLGİLİ TALİMATLARIN TÜMÜ KODLANDI:
 * - TypeScript tip güvenliği sağlandı
 * - Error handling eklendi
 * - Export yapılandırıldı
 */

/**
 * WhatsApp linki oluşturur
 * @param phone - Telefon numarası (ülke kodu ile)
 * @param message - Gönderilecek mesaj
 * @returns WhatsApp chat linki
 */
export const getWhatsAppLink = (phone: string | undefined | null, message?: string): string => {
  try {
    // L1: GLOBAL INPUT VALIDATION
    if (!phone || typeof phone !== 'string') {
      console.warn('L1: Invalid phone input:', typeof phone, phone);
      return 'https://wa.me/'; // Fallback
    }

    // L2: OPERATIONAL PHONE CLEANING
    try {
      const cleanPhone = phone.replace(/[^0-9+]/g, '');

      // L3: RECORD-LEVEL PHONE VALIDATION
      try {
        if (!cleanPhone || cleanPhone.length < 10) {
          console.warn('L3: Invalid cleaned phone:', cleanPhone);
          return 'https://wa.me/'; // Fallback
        }

        // Mesajı encode et
        const encodedMessage = message ? encodeURIComponent(message) : '';

        // WhatsApp linki oluştur
        return `https://wa.me/${cleanPhone}${encodedMessage ? `?text=${encodedMessage}` : ''}`;
      } catch (recordErr) {
        console.error('L3: Record-level phone processing failed:', recordErr);
        return 'https://wa.me/'; // Fallback
      }
    } catch (operationalErr) {
      console.error('L2: Operational phone cleaning failed:', operationalErr);
      return 'https://wa.me/'; // Fallback
    }
  } catch (globalErr) {
    console.error('L1: Global WhatsApp link creation failed:', globalErr);
    return 'https://wa.me/'; // Fallback
  }
};

/**
 * Mock API yanıtları için yardımcı fonksiyonlar
 */
export const mockApiService = {
  /**
   * Gecikmeli yanıt simüle etme
   */
  delay: (ms: number = 1000): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  /**
   * Mock firma verisi oluştur
   */
  createMockFirm: (id: number, name: string) => ({
    id,
    name,
    phone: `+90555${id.toString().padStart(6, '0')}`,
    address: `${name} adresi`,
    city: 'İstanbul',
    district: 'Kadıköy',
    rating: 4.5,
    services: ['Oto Çekici', 'Yol Yardımı']
  }),

  /**
   * Mock şehir verileri
   */
  cities: [
    { id: 'Istanbul', name: 'İstanbul', slug: 'istanbul' },
    { id: 'Ankara', name: 'Ankara', slug: 'ankara' },
    { id: 'Izmir', name: 'İzmir', slug: 'izmir' },
    { id: 'Bursa', name: 'Bursa', slug: 'bursa' },
    { id: 'Antalya', name: 'Antalya', slug: 'antalya' }
  ],

  /**
   * Mock hizmet verileri
   */
  services: [
    { id: '1', name: 'Oto Çekici' },
    { id: '2', name: 'Yol Yardımı' },
    { id: '3', name: 'Akü Takviyesi' },
    { id: '4', name: 'Lastik Değişimi' },
    { id: '5', name: 'Yakıt Temini' }
  ]
};

/**
 * Export edilen fonksiyonlar
 */
export default mockApiService;
