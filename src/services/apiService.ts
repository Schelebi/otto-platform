import { apiClient } from "./apiClient"; // #DELIL 4
import { mockApiService } from "./mockApiService";
import type { AnisaRecord } from "../types";

const EP = {
  cities: import.meta.env.VITE_API_CITIES || "/iller.php",
  districts: import.meta.env.VITE_API_DISTRICTS || "/iller_ilceler.php",
  services: import.meta.env.VITE_API_SERVICES || "/hizmetler.php",
  search: import.meta.env.VITE_API_SEARCH || "/arama.php",
  nearby: import.meta.env.VITE_API_NEARBY || "/en_yakin.php",
  firmDetail: import.meta.env.VITE_API_FIRM_DETAIL || "/firma_detay.php",
};

function toStringList(x: any): string[] {
  if (!x) return [];
  if (Array.isArray(x)) {
    return x
      .map((i) => (typeof i === "string" ? i : i?.il || i?.hizmet_adi || i?.name || i?.slug))
      .filter(Boolean);
  }
  if (Array.isArray(x.data)) return toStringList(x.data);
  return [];
}

export const apiService = {
  async getCities(): Promise<string[]> {
    try {
      const res = await apiClient.get<any>(EP.cities);
      const list = toStringList(res);
      if (list.length) return list;
      return toStringList(res?.iller);
    } catch (e) {
      console.warn("[apiService][fallback] getCities", e);
      return mockApiService.getCities();
    }
  },

  async getDistricts(city: string): Promise<string[]> {
    try {
      const res = await apiClient.get<any>(EP.districts, { il: city, city });
      const list = toStringList(res);
      if (list.length) return list;
      return toStringList(res?.ilceler);
    } catch (e) {
      console.warn("[apiService][fallback] getDistricts", e);
      return mockApiService.getDistricts(city);
    }
  },

  async getServices(): Promise<string[]> {
    try {
      const res = await apiClient.get<any>(EP.services);
      const list = toStringList(res);
      if (list.length) return list;
      return toStringList(res?.hizmetler);
    } catch (e) {
      console.warn("[apiService][fallback] getServices", e);
      return mockApiService.getServices();
    }
  },

  async search(filters: { city?: string; district?: string; service?: string; keyword?: string; }): Promise<AnisaRecord[]> {
    try {
      const params = {
        il: filters.city || "",
        ilce: filters.district || "",
        hizmet: filters.service || "",
        q: filters.keyword || "",
        city: filters.city || "",
        district: filters.district || "",
        service: filters.service || "",
        keyword: filters.keyword || "",
      };
      const res = await apiClient.get<any>(EP.search, params);
      const rows = res?.data || res?.firmalar || res || [];
      return Array.isArray(rows) ? rows : [];
    } catch (e) {
      console.warn("[apiService][fallback] search", e);
      return mockApiService.search(filters);
    }
  },

  async getNearby(lat: number, lng: number): Promise<AnisaRecord[]> {
    try {
      const res = await apiClient.get<any>(EP.nearby, { lat, lng });
      const rows = res?.data || res?.firmalar || res || [];
      return Array.isArray(rows) ? rows : [];
    } catch (e) {
      console.warn("[apiService][fallback] getNearby", e);
      return mockApiService.getNearby(lat, lng);
    }
  },

  async getFirmDetail(id: number): Promise<AnisaRecord | null> {
    try {
      const res = await apiClient.get<any>(EP.firmDetail, { id, firma_id: id });
      const row = res?.data || res?.firma || res;
      return row || null;
    } catch (e) {
      console.warn("[apiService][fallback] getFirmDetail", e);
      return mockApiService.getFirmDetail(id);
    }
  },
};
