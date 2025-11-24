#!/usr/bin/env python3
"""
API Bağlantı Sorunu Otomatik Çözüm Script
"""

import subprocess
import json
import time

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("🔧 API BAĞLANTI SORUNU ÇÖZÜLÜYOR")
    print("=" * 40)

    # 1. Vercel environment değişkenlerini kontrol et
    print("1. Environment değişkenleri kontrol ediliyor...")
    success, stdout, stderr = run_cmd("npx vercel env ls")
    print(f"Env list: {stdout}")

    # 2. Eski değişkeni kaldır
    print("2. Eski VITE_API_BASE_URL kaldırılıyor...")
    run_cmd('echo yes | npx vercel env rm VITE_API_BASE_URL production')

    # 3. Yeni değişken ekle
    print("3. Yeni VITE_API_BASE_URL ekleniyor...")
    api_url = "https://ottomans.onrender.com"
    run_cmd(f'echo "{api_url}" | npx vercel env add VITE_API_BASE_URL production')

    # 4. Frontend kodunda direkt URL güncelle
    print("4. Frontend kodunda direkt URL güncelleniyor...")

    # src/services/apiService.ts dosyasını güncelle
    api_service_content = '''import { requestJson, buildUrl } from './apiClient';

const API_BASE_URL = 'https://ottomans.onrender.com';

export const apiService = {
  async getCities() {
    try {
      const response = await requestJson(`${API_BASE_URL}/api/cities`);
      return response;
    } catch (error) {
      console.error('Cities API error:', error);
      throw new Error('İller yüklenemedi');
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
      throw new Error('Firma detayı yüklenemedi');
    }
  },

  async getFirmsByCity(city: string) {
    try {
      const response = await requestJson(`${API_BASE_URL}/api/firms/by-city/${city}`);
      return response;
    } catch (error) {
      console.error('City-based firms API error:', error);
      throw new Error('Şehre göre firmalar yüklenemedi');
    }
  }
};

export default apiService;'''

    try:
        with open("src/services/apiService.ts", "w") as f:
            f.write(api_service_content)
        print("✅ apiService.ts güncellendi")
    except Exception as e:
        print(f"❌ apiService.ts güncellenemedi: {e}")

    # 5. GitHub'a push
    print("5. Değişiklikler GitHub'a pushlanıyor...")
    run_cmd("git add .")
    run_cmd('git commit -m "Fix: Direct API URL to ottomans.onrender.com"')
    run_cmd("git push origin master")

    # 6. Yeniden deploy
    print("6. Vercel yeniden deploy...")
    success, stdout, stderr = run_cmd("npx vercel --prod")

    if success:
        print("✅ Deploy başarılı!")
        for line in stdout.split('\n'):
            if 'https://' in line and 'vercel.app' in line:
                print(f"🌐 Yeni URL: {line.strip()}")
                print(f"🔗 Test et: {line.strip()}#/search")
    else:
        print(f"❌ Deploy başarısız: {stderr}")

    # 7. API test
    print("7. Backend API test...")
    try:
        import requests
        response = requests.get(f"{api_url}/api/cities", timeout=10)
        if response.status_code == 200:
            print("✅ Backend API çalışıyor")
        else:
            print(f"⚠️ Backend API hata: {response.status_code}")
    except:
        print("❌ Backend API erişilemiyor")

    print("\n🎉 ÇÖZÜM TAMAMLANDI!")

if __name__ == "__main__":
    main()
