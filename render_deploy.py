#!/usr/bin/env python3
"""
OTTO Backend Render Deployment Otomasyonu
Otomatik olarak backend'i Render'a deploy eder
"""

import subprocess
import json
import time
import requests
from pathlib import Path

def run_command(cmd, cwd=None):
    """Komut çalıştır ve sonucu döndür"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_render_yaml():
    """render.yaml dosyasını kontrol et"""
    yaml_path = Path("render.yaml")
    if not yaml_path.exists():
        print("❌ render.yaml dosyası bulunamadı")
        return False

    print("✅ render.yaml dosyası mevcut")
    with open(yaml_path, 'r') as f:
        content = f.read()
        print(f"📄 İçerik:\n{content}")
    return True

def update_render_yaml():
    """render.yaml dosyasını güncelle"""
    yaml_content = """services:
  - type: web
    name: otto-api
    runtime: node
    plan: free
    autoDeploy: true
    buildCommand: "npm install"
    startCommand: "node server.cjs"
    envVars:
      - key: NODE_ENV
        value: production
      - key: API_PORT
        value: 3001
      - key: DB_HOST
        value: 35.214.224.135
      - key: DB_USER
        value: uwcw1gm1sor8u
      - key: DB_PASSWORD
        value: g05jkizfzjdp
      - key: DB_NAME
        value: db6ctx4kvleywe"""

    with open("render.yaml", 'w') as f:
        f.write(yaml_content)
    print("✅ render.yaml güncellendi")

def check_github_repo():
    """GitHub reposunu kontrol et"""
    success, stdout, stderr = run_command("git remote -v")
    if success and "github.com" in stdout:
        print("✅ GitHub reposu mevcut")
        return True
    print("❌ GitHub reposu bulunamadı")
    return False

def push_to_github():
    """Değişiklikleri GitHub'a push et"""
    print("📤 GitHub'a push yapılıyor...")

    commands = [
        "git add .",
        "git commit -m 'Auto deploy - Backend ready for Render'",
        "git push origin master"
    ]

    for cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"❌ Hata: {cmd} - {stderr}")
            return False
        print(f"✅ {cmd}")

    return True

def create_render_deployment():
    """Render deployment bilgileri oluştur"""
    deploy_info = {
        "repo_url": "https://github.com/Schelebi/otto-platform",
        "service_name": "otto-api",
        "expected_url": "https://otto-api.onrender.com",
        "instructions": """
1. https://render.com'a git
2. GitHub ile giriş yap
3. "New Web Service" seç
4. GitHub reposunu bağla: Schelebi/otto-platform
5. render.yaml dosyasını otomatik algıla
6. Deploy butonuna tıkla
7. Deploy tamamlandığında URL'yi kopyala
        """
    }

    with open("deploy_info.json", 'w') as f:
        json.dump(deploy_info, f, indent=2)

    print("📋 Deploy bilgileri oluşturuldu")
    print(f"🌐 Beklenen URL: {deploy_info['expected_url']}")
    print(f"📄 Detaylı bilgi: deploy_info.json")

def check_api_health(url):
    """API sağlık kontrolü yap"""
    try:
        response = requests.get(f"{url}/api/cities", timeout=10)
        if response.status_code == 200:
            print(f"✅ API çalışıyor: {url}")
            return True
        else:
            print(f"⚠️ API yanıt veriyor ama hata var: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API erişilemiyor: {url} - {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("🚀 OTTO Backend Render Deployment Otomasyonu")
    print("=" * 50)

    # 1. render.yaml kontrol
    if not check_render_yaml():
        update_render_yaml()

    # 2. GitHub kontrol
    if not check_github_repo():
        print("❌ GitHub reposu gerekli")
        return

    # 3. GitHub'a push
    if not push_to_github():
        print("❌ GitHub push başarısız")
        return

    # 4. Deploy bilgileri
    create_render_deployment()

    # 5. Manuel deploy talimatları
    print("\n🎯 SONRAKİ ADIMLAR:")
    print("1. https://render.com'a git")
    print("2. 'New Web Service' → GitHub'dan Schelebi/otto-platform seç")
    print("3. Deploy et")
    print("4. Deploy sonrası URL'yi al")

    # 6. API kontrol (beklenen URL)
    print("\n🔍 API Kontrol:")
    check_api_health("https://otto-api.onrender.com")

    print("\n✅ Otomasyon tamamlandı!")

if __name__ == "__main__":
    main()
