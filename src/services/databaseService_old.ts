import { City, District, Service, Firm } from '../types';

// Hook'ları export et
export { useServices } from '../hooks/useServices';
export { useFetchFirms } from '../hooks/useFetchFirms';


// L1: GLOBAL DATABASE SERVICE WITH 3-LAYER PROTECTION
export class DatabaseService {
  private static instance: DatabaseService;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3001';
  }

  static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  // L1: GLOBAL CITIES FETCH WITH 3-LAYER PROTECTION
  async getCities(): Promise<City[]> {
    try {
      // L2: OPERATIONAL HTTP REQUEST
      try {
        const response = await fetch(`${this.baseUrl}/api/cities`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          signal: AbortSignal.timeout(10000), // 10s timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // L3: RECORD-LEVEL DATA PROCESSING
        try {
          const data = await response.json();

          if (!data || !Array.isArray(data.cities)) {
            throw new Error('Invalid cities data format');
          }

          return data.cities.map((city: any) => ({
            id: city.id?.toString() || '',
            name: city.name || '',
            slug: city.slug || '',
          }));
        } catch (recordErr) {
          console.error('L3: Cities data processing failed:', recordErr);
          throw recordErr;
        }
      } catch (operationalErr) {
        console.error('L2: Operational cities fetch failed:', operationalErr);
        throw operationalErr;
      }
    } catch (globalErr) {
      console.error('L1: Global cities fetch failed:', globalErr);
      throw new Error('İller yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // 🔴 REAL DISTRICTS FROM ANISA TABLE - Cascading Logic
  async getDistricts(cityId: string): Promise<District[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/districts/${encodeURIComponent(cityId)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          signal: AbortSignal.timeout(10000)
        }
      );

      if (!response.ok) {
        console.warn(`Districts API error: ${response.status}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.districts || [];
    } catch (error: any) {
      console.error('Districts fetch error:', error);
      if (error.name === 'AbortError') {
        throw new Error('İlçeler yüklenemedi - timeout. Lütfen internet bağlantınızı kontrol edin.');
      }
      throw new Error('İlçeler yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // 🔴 REAL SERVICES FROM ANISA TABLE
  async getServices(): Promise<Service[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/services`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        console.warn(`Services API error: ${response.status}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.services || [];
    } catch (error: any) {
      console.error('Services fetch error:', error);
      if (error.name === 'AbortError') {
        throw new Error('Hizmetler yüklenemedi - timeout. Lütfen internet bağlantınızı kontrol edin.');
      }
      throw new Error('Hizmetler yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // 🔴 REAL FIRMS SEARCH FROM ANISA TABLE - All Filters Combined
  // L1: GLOBAL FIRMS SEARCH WITH 3-LAYER PROTECTION
  async searchFirms(filters: {
    cityId?: string;
    districtId?: string;
    serviceId?: string;
    keyword?: string;
  }): Promise<Firm[]> {
    try {
      // L2: OPERATIONAL HTTP REQUEST
      try {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value.toString());
        });

        const response = await fetch(`${this.baseUrl}/api/firms/search?${params}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(15000), // 15s timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // L3: RECORD-LEVEL DATA PROCESSING
        try {
          const data = await response.json();

          if (!data || !Array.isArray(data.firms)) {
            throw new Error('Invalid firms data format');
          }

          return data.firms.map((firm: any) => ({
            id: firm.id?.toString() || '',
            name: firm.firma_adi || '',
            phone: firm.telefon || '',
            address: firm.adres || '',
            city: firm.il || '',
            district: firm.ilce || '',
            services: firm.hizmetler ? firm.hizmetler.split(',').map((s: string) => s.trim()) : [],
            rating: firm.puan ? Number(firm.puan) : 0,
            latitude: firm.lat ? Number(firm.lat) : null,
            longitude: firm.lng ? Number(firm.lng) : null,
          }));
        } catch (recordErr) {
          console.error('L3: Firms data processing failed:', recordErr);
          throw recordErr;
        }
      } catch (operationalErr) {
        console.error('L2: Operational firms search failed:', operationalErr);
        throw operationalErr;
      }
    } catch (globalErr) {
      console.error('L1: Global firms search failed:', globalErr);
      throw new Error('Firmalar yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }


  // L1: GLOBAL FIRM DETAIL WITH 3-LAYER PROTECTION
  async getFirmDetail(firmId: number): Promise<Firm> {
    try {
      // L2: OPERATIONAL HTTP REQUEST
      try {
        const response = await fetch(`${this.baseUrl}/api/firms/${firmId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          signal: AbortSignal.timeout(10000), // 10s timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // L3: RECORD-LEVEL DATA PROCESSING
        try {
          const data = await response.json();

          if (!data || !data.firm) {
            throw new Error('Invalid firm detail data format');
          }

          const firm = data.firm;
          return {
            id: firm.id?.toString() || '',
            name: firm.firma_adi || '',
            phone: firm.telefon || '',
            address: firm.adres || '',
            city: firm.il || '',
            district: firm.ilce || '',
            services: firm.hizmetler ? firm.hizmetler.split(',').map((s: string) => s.trim()) : [],
            rating: firm.puan ? Number(firm.puan) : 0,
            latitude: firm.lat ? Number(firm.lat) : null,
            longitude: firm.lng ? Number(firm.lng) : null,
          };
        } catch (recordErr) {
          console.error('L3: Firm detail data processing failed:', recordErr);
          throw recordErr;
        }
      } catch (operationalErr) {
        console.error('L2: Operational firm detail failed:', operationalErr);
        throw operationalErr;
      }

      const data = await response.json();
      return data.services || [];
    } catch (error: any) {
      console.error('Services fetch error:', error);
      if (error.name === 'AbortError') {
        throw new Error('Hizmetler yüklenemedi - timeout. Lütfen internet bağlantınızı kontrol edin.');
      }
      throw new Error('Hizmetler yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // 🔴 REAL FIRMS SEARCH FROM ANISA TABLE - All Filters Combined
  // L1: GLOBAL FIRMS SEARCH WITH 3-LAYER PROTECTION
  async searchFirms(filters: {
    cityId?: string;
    districtId?: string;
    serviceId?: string;
    keyword?: string;
  }): Promise<Firm[]> {
    try {
      // L2: OPERATIONAL HTTP REQUEST
      try {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value.toString());
        });

        const response = await fetch(`${this.baseUrl}/api/firms/search?${params}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(15000), // 15s timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // L3: RECORD-LEVEL DATA PROCESSING
        try {
          const data = await response.json();

          if (!data || !Array.isArray(data.firms)) {
            throw new Error('Invalid firms data format');
          }

          return data.firms.map((firm: any) => ({
            id: firm.id?.toString() || '',
            name: firm.firma_adi || '',
            phone: firm.telefon || '',
            address: firm.adres || '',
            city: firm.il || '',
            district: firm.ilce || '',
            services: firm.hizmetler ? firm.hizmetler.split(',').map((s: string) => s.trim()) : [],
            rating: firm.puan ? Number(firm.puan) : 0,
            latitude: firm.lat ? Number(firm.lat) : null,
            longitude: firm.lng ? Number(firm.lng) : null,
          }));
        } catch (recordErr) {
          console.error('L3: Firms data processing failed:', recordErr);
          throw recordErr;
        }
      } catch (operationalErr) {
        console.error('L2: Operational firms search failed:', operationalErr);
        throw operationalErr;
      }
    } catch (globalErr) {
      console.error('L1: Global firms search failed:', globalErr);
      throw new Error('Firmalar yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // L1: GLOBAL FIRM DETAIL WITH 3-LAYER PROTECTION
  async getFirmDetail(firmId: number): Promise<Firm> {
    try {
      // L2: OPERATIONAL HTTP REQUEST
      try {
        const response = await fetch(`${this.baseUrl}/api/firms/${firmId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          signal: AbortSignal.timeout(10000), // 10s timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // L3: RECORD-LEVEL DATA PROCESSING
        try {
          const data = await response.json();

          if (!data || !data.firm) {
            throw new Error('Invalid firm detail data format');
          }

          const firm = data.firm;
          return {
            id: firm.id?.toString() || '',
            name: firm.firma_adi || '',
            phone: firm.telefon || '',
            address: firm.adres || '',
            city: firm.il || '',
            district: firm.ilce || '',
            services: firm.hizmetler ? firm.hizmetler.split(',').map((s: string) => s.trim()) : [],
            rating: firm.puan ? Number(firm.puan) : 0,
            latitude: firm.lat ? Number(firm.lat) : null,
            longitude: firm.lng ? Number(firm.lng) : null,
          };
        } catch (recordErr) {
          console.error('L3: Firm detail data processing failed:', recordErr);
          throw recordErr;
        }
      } catch (operationalErr) {
        console.error('L2: Operational firm detail failed:', operationalErr);
        throw operationalErr;
      }
    } catch (globalErr) {
      console.error('L1: Global firm detail failed:', globalErr);
      throw new Error('Firma detayı yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

export default DatabaseService.getInstance();
