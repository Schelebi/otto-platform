#!/usr/bin/env python3
"""
🚀 GITHUB COMMIT OTOMASYONU
Proje yapısı değişikliklerini GitHub'a gönder
"""

import subprocess
import time
import json
import sys
import os

class Colors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN_BG = '\033[42m'
    RED_BG = '\033[41g'

def run_command(cmd: str, timeout: int = 60) -> tuple[bool, str, str]:
    """Komut çalıştır ve sonucu döndür"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Ana commit işlemi"""
    print(f"{Colors.BOLD}{Colors.GREEN_BG}🚀 GITHUB COMMIT OTOMASYONU{Colors.RESET}")
    print(f"{Colors.INFO}Proje yapısı değişiklikleri gönderiliyor...{Colors.RESET}")

    # 1. Git status kontrol
    print(f"\n{Colors.INFO}🔍 Git status kontrol ediliyor...{Colors.RESET}")
    success, stdout, stderr = run_command("git status")

    if success:
        print(f"{Colors.SUCCESS}✅ Git status OK{Colors.RESET}")
        print(f"{Colors.INFO}{stdout[:200]}...{Colors.RESET}")
    else:
        print(f"{Colors.ERROR}❌ Git status HATA: {stderr}{Colors.RESET}")
        return False

    # 2. Tüm dosyaları ekle
    print(f"\n{Colors.INFO}📦 Tüm dosyalar ekleniyor...{Colors.RESET}")
    success, stdout, stderr = run_command("git add .")

    if success:
        print(f"{Colors.SUCCESS}✅ Dosyalar eklendi{Colors.RESET}")
    else:
        print(f"{Colors.ERROR}❌ Dosya ekleme HATA: {stderr}{Colors.RESET}")
        return False

    # 3. Commit oluştur
    commit_message = "Reorganize project structure - move files to appropriate folders"
    print(f"\n{Colors.INFO}📝 Commit oluşturuluyor: {commit_message}{Colors.RESET}")
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')

    if success:
        print(f"{Colors.SUCCESS}✅ Commit oluşturuldu{Colors.RESET}")
        print(f"{Colors.INFO}{stdout[:100]}...{Colors.RESET}")
    else:
        print(f"{Colors.ERROR}❌ Commit HATA: {stderr}{Colors.RESET}")
        return False

    # 4. Push to GitHub
    print(f"\n{Colors.INFO}🚀 GitHub'a push ediliyor...{Colors.RESET}")
    success, stdout, stderr = run_command("git push origin master")

    if success:
        print(f"{Colors.GREEN_BG}{Colors.BOLD}🎉 BAŞARILI! GitHub'a gönderildi{Colors.RESET}")
        print(f"{Colors.INFO}{stdout[:200]}...{Colors.RESET}")

        # URL göster
        print(f"\n{Colors.BOLD}{Colors.INFO}🔗 GitHub Repository:{Colors.RESET}")
        print(f"{Colors.INFO}https://github.com/Schelebi/otto-platform{Colors.RESET}")

        return True
    else:
        print(f"{Colors.RED_BG}{Colors.BOLD}❌ Push HATA: {stderr}{Colors.RESET}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🎉 İŞLEM BAŞARILI!{Colors.RESET}")
        else:
            print(f"\n{Colors.BOLD}{Colors.RED_BG}❌ İŞLEM BAŞARISIZ!{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  İptal edildi{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.ERROR}❌ Beklenmedik hata: {str(e)}{Colors.RESET}")
