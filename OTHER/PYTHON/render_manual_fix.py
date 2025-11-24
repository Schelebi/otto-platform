#!/usr/bin/env python3
"""
🔧 RENDER MANUEL MÜDAHALE KILAVUZU
Backend 502 hatası için manuel çözüm adımları
"""

import subprocess
import time
import json
import webbrowser
from pathlib import Path

class Colors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN_BG = '\033[42m'
    RED_BG = '\033[41m'

def main():
    print(f"{Colors.BOLD}{Colors.RED_BG}🔧 RENDER MANUEL MÜDAHALE KILAVUZU{Colors.RESET}")
    print(f"{Colors.INFO}Backend 502 hatası için adım adım çözüm{Colors.RESET}")

    steps = [
        {
            "title": "1️⃣ Render Dashboard'a Giriş",
            "description": "https://dashboard.render.com/login adresine gidin",
            "action": "BROWSER_OPEN",
            "url": "https://dashboard.render.com/login"
        },
        {
            "title": "2️⃣ Servisi Bul",
            "description": "ottomans servisini bulun ve tıklayın",
            "action": "MANUAL"
        },
        {
            "title": "3️⃣ Manual Restart",
            "description": "Restart butonuna tıklayarak servisi yeniden başlatın",
            "action": "MANUAL"
        },
        {
            "title": "4️⃣ Logları Kontrol Et",
            "description": "Logs sekmesinde hata mesajlarını kontrol edin",
            "action": "MANUAL"
        },
        {
            "title": "5️⃣ Environment Değişkenleri",
            "description": "Environment sekmesinde DB ayarlarını kontrol edin",
            "action": "MANUAL"
        },
        {
            "title": "6️⃣ Health Check Test",
            "description": "Servis başladıktan sonra API test edin",
            "action": "API_TEST"
        }
    ]

    current_step = 0

    while current_step < len(steps):
        step = steps[current_step]

        print(f"\n{Colors.BOLD}{Colors.INFO}📍 {step['title']}{Colors.RESET}")
        print(f"{Colors.WARNING}{step['description']}{Colors.RESET}")

        if step['action'] == 'BROWSER_OPEN':
            print(f"{Colors.INFO}🌐 Tarayıcı açılıyor...{Colors.RESET}")
            webbrowser.open(step['url'])
            input(f"{Colors.INFO}Devam etmek için Enter tuşuna basın...{Colors.RESET}")

        elif step['action'] == 'API_TEST':
            print(f"{Colors.INFO}🔄 API test ediliyor...{Colors.RESET}")

            for i in range(5):
                success, stdout, stderr = run_command("curl -I https://ottomans.onrender.com/api/cities", timeout=10)

                if success and "200" in stdout:
                    print(f"{Colors.GREEN_BG}{Colors.BOLD}🎉 BAŞARILI! Backend çalışıyor{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.WARNING}⏱️  Tekrar deneniyor ({i+1}/5){Colors.RESET}")
                    time.sleep(10)

            print(f"{Colors.ERROR}❌ Backend hala çalışmıyor{Colors.RESET}")

        else:  # MANUAL
            input(f"{Colors.INFO}Tamamlandığında Enter tuşuna basın...{Colors.RESET}")

        current_step += 1

    # Son kontrol
    print(f"\n{Colors.BOLD}{Colors.INFO}🔍 SON KONTROL{Colors.RESET}")
    success, stdout, stderr = run_command("curl -I https://ottomans.onrender.com/api/cities", timeout=30)

    if success and "200" in stdout:
        print(f"{Colors.GREEN_BG}{Colors.BOLD}🎉 TÜM SORUNLAR ÇÖZÜLDÜ!{Colors.RESET}")

        # Frontend test
        print(f"{Colors.INFO}🔄 Frontend test ediliyor...{Colors.RESET}")
        frontend_success, _, _ = run_command("curl -I https://otto-qqg9onomf-ottos-projects-52f5219c.vercel.app", timeout=10)

        if frontend_success:
            print(f"{Colors.SUCCESS}✅ Frontend de çalışıyor{Colors.RESET}")
            print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🎉 SİSTEM TAMEN ÇALIŞIYOR!{Colors.RESET}")
            print(f"{Colors.INFO}🌐 Frontend: https://otto-qqg9onomf-ottos-projects-52f5219c.vercel.app{Colors.RESET}")
            print(f"{Colors.INFO}🔧 Backend: https://ottomans.onrender.com{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}⚠️  Frontend test edilemedi{Colors.RESET}")

        return True
    else:
        print(f"{Colors.RED_BG}{Colors.BOLD}❌ SORUN DEVAM EDİYOR{Colors.RESET}")
        print(f"{Colors.WARNING}🔧 Destek için Render loglarını kontrol edin{Colors.RESET}")
        return False

def run_command(cmd: str, timeout: int = 30):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

if __name__ == "__main__":
    main()
