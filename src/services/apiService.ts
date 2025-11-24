import { requestJson, buildUrl } from './apiClient';

const API_BASE_URL = 'https://ottomans.onrender.com';

export const apiService = {
  async getCities() {
    try {
      const response = await requestJson(`${API_BASE_URL}/api/cities`);
      return response;
    } catch (error) {
      console.error('Cities API error:', error);
      throw new Error('Ýller yüklenemedi');
    }
  },

  async getServices() {
    try {
      const response = await requestJson(`${API_BASE_URL}/api/services`);
      return response;
    } catch (error) {
      console.error('Services API error:', error);
      throw new Error('Hizmetler yüklenemedi');
    }
  },

  async searchFirms(params: any) {
    try {
      const url = buildUrl(`${API_BASE_URL}/api/firms/search`, params);
      const response = await requestJson(url);
      return response;
    } catch (error) {
      console.error('Firms search API error:', error);
      throw new Error('Firmalar yüklenemedi');
    }
  },

  async getFirmById(id: string) {
    try {
      const response = await requestJson(`${API_BASE_URL}/api/firms/${id}`);
      return response;
    } catch (error) {
      console.error('Firm detail API error:', error);
      throw new Error('Firma detayý yüklenemedi');
    }
  },

  async getFirmsByCity(city: string) {
    try {
      const response = await requestJson(`${API_BASE_URL}/api/firms/by-city/${city}`);
      return response;
    } catch (error) {
      console.error('City-based firms API error:', error);
      throw new Error('Þehre göre firmalar yüklenemedi');
    }
  }
};

export default apiService;