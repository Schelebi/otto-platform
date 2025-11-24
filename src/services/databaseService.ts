import { City, District, Service, Firm, SearchFilters } from '../types';

export class DatabaseService {
  private static instance: DatabaseService;
  private baseUrl: string;

  private constructor() {
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

  async getFirmsByCity(city: string): Promise<Firm[]> {
    const response = await fetch(`${this.baseUrl}/api/firms/by-city/${encodeURIComponent(city)}`);
    if (!response.ok) throw new Error('Şehre göre firmalar yüklenemedi');
    return (await response.json()).firms || [];
  }

  async getFirmDetail(id: number): Promise<Firm> {
    const response = await fetch(`${this.baseUrl}/api/firms/${id}`);
    if (!response.ok) throw new Error('Firma detayı yüklenemedi');
    return (await response.json()).firm;
  }
}
