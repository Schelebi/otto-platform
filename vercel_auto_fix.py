#!/usr/bin/env python3
"""
Vercel Otomatik Yapılandırma ve API Bağlantı Fix Script
Otomatik olarak environment değişkenlerini düzeltir ve deploy yapar
"""

import subprocess
import json
import time
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Komut çalıştır ve sonucu döndür"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_vercel_login():
    """Vercel login kontrol"""
    success, stdout, stderr = run_command("npx vercel whoami")
    if success and "salihchelebii" in stdout:
        return True
    return False

def remove_env_var(var_name):
    """Environment değişkenini kaldır"""
    print(f"🗑️ {var_name} kaldırılıyor...")
    cmd = f"echo yes | npx vercel env rm {var_name} production"
    success, stdout, stderr = run_command(cmd)
    if success:
        print(f"✅ {var_name} kaldırıldı")
        return True
    else:
        print(f"⚠️ {var_name} kaldırılamadı (zaten yok olabilir)")
        return True

def add_env_var(var_name, value):
    """Environment değişkeni ekle"""
    print(f"➕ {var_name} ekleniyor: {value}")
    cmd = f'echo "{value}" | npx vercel env add {var_name} production'
    success, stdout, stderr = run_command(cmd)
    if success:
        print(f"✅ {var_name} eklendi")
        return True
    else:
        print(f"❌ {var_name} eklenemedi: {stderr}")
        return False

def update_local_env():
    """Local .env dosyasını güncelle"""
    env_file = Path(".env")
    env_content = """VITE_API_BASE_URL=https://ottomans.onrender.com
DB_HOST=35.214.224.135
DB_USER=uwcw1gm1sor8u
DB_PASSWORD=g05jkizfzjdp
DB_NAME=db6ctx4kvleywe
NODE_ENV=production"""

    try:
        # Dosya izinlerini kontrol et
        if env_file.exists():
            os.chmod(env_file, 0o666)

        with open(env_file, 'w') as f:
            f.write(env_content)

        print("✅ .env dosyası güncellendi")
        return True
    except Exception as e:
        print(f"❌ .env güncellenemedi: {e}")
        return False

def deploy_to_vercel():
    """Vercel'e deploy"""
    print("🚀 Vercel deploy başlatılıyor...")
    success, stdout, stderr = run_command("npx vercel --prod")
    if success:
        print("✅ Deploy başarılı")
        # URL'yi çıkar
        lines = stdout.split('\n')
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                url = line.strip()
                print(f"🌐 Frontend URL: {url}")
                return url
    else:
        print(f"❌ Deploy başarısız: {stderr}")
    return None

def test_api_connection(api_url):
    """API bağlantısını test et"""
    print(f"🔍 API test ediliyor: {api_url}")
    try:
        import requests
        response = requests.get(f"{api_url}/api/cities", timeout=10)
        if response.status_code == 200:
            print("✅ API çalışıyor")
            return True
        else:
            print(f"⚠️ API yanıt veriyor ama hata var: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API erişilemiyor: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("🔧 VERCEL OTOMATİK YAPILANDIRMA")
    print("=" * 40)

    # 1. Vercel login kontrol
    if not check_vercel_login():
        print("❌ Vercel'e giriş yapın: npx vercel login")
        return

    # 2. Environment değişkenlerini temizle
    print("\n🗑️ Environment değişkenleri temizleniyor...")
    remove_env_var("VITE_API_BASE_URL")

    # 3. Yeni environment değişkeni ekle
    print("\n➕ Yeni environment değişkenleri ekleniyor...")
    api_url = "https://ottomans.onrender.com"
    add_env_var("VITE_API_BASE_URL", api_url)

    # 4. Local .env güncelle
    print("\n📝 Local .env güncelleniyor...")
    update_local_env()

    # 5. API test
    print("\n🔍 API bağlantısı test ediliyor...")
    test_api_connection(api_url)

    # 6. Deploy
    print("\n🚀 Deploy başlatılıyor...")
    frontend_url = deploy_to_vercel()

    if frontend_url:
        print(f"\n🎉 TAMAMLANDI!")
        print(f"🌐 Frontend: {frontend_url}")
        print(f"🔧 Backend API: {api_url}")
        print(f"\n📋 Test et: {frontend_url}#/search")

        # Sonuçları kaydet
        result = {
            "frontend_url": frontend_url,
            "backend_url": api_url,
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        with open("deployment_result.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print("📊 Sonuçlar kaydedildi: deployment_result.json")
    else:
        print("❌ Deploy başarısız")

if __name__ == "__main__":
    main()
