#!/usr/bin/env python3

api_service_content = '''import { apiClient } from './apiClient';

const API_BASE_URL = 'https://ottomans.onrender.com';

export const apiService = {
  async getCities() {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/api/cities`);
      return response;
    } catch (error) {
      console.error('Cities API error:', error);
      throw new Error('İller yüklenemedi');
    }
  },

  async getServices() {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/api/services`);
      return response;
    } catch (error) {
      console.error('Services API error:', error);
      throw new Error('Hizmetler yüklenemedi');
    }
  },

  async searchFirms(params: any) {
    try {
      const url = new URL(`${API_BASE_URL}/api/firms/search`);
      Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.append(key, String(value));
      });
      const response = await apiClient.get(url.pathname + url.search);
      return response;
    } catch (error) {
      console.error('Firms search API error:', error);
      throw new Error('Firmalar yüklenemedi');
    }
  },

  async getFirmById(id: string) {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/api/firms/${id}`);
      return response;
    } catch (error) {
      console.error('Firm detail API error:', error);
      throw new Error('Firma detayı yüklenemedi');
    }
  },

  async getFirmsByCity(city: string) {
    try {
      const response = await apiClient.get(`${API_BASE_URL}/api/firms/by-city/${city}`);
      return response;
    } catch (error) {
      console.error('City-based firms API error:', error);
      throw new Error('Şehre göre firmalar yüklenemedi');
    }
  }
};

export default apiService;'''

with open("src/services/apiService.ts", "w", encoding="utf-8") as f:
    f.write(api_service_content)

print("✅ apiService.ts düzeltildi")
