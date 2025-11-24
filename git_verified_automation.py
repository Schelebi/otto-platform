#!/usr/bin/env python3
"""
🔍 GİT DOĞRULAMALI PERSISTENT OTOMASYON
Önce Git durumunu kontrol et, sonra devam et
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
    PROGRESS = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN_BG = '\033[42m'
    RED_BG = '\033[41m'
    YELLOW_BG = '\033[43m'

def run_command(cmd: str, timeout: int = 30) -> tuple[bool, str, str]:
    """Komut çalıştır ve sonucu döndür"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def verify_git_setup():
    """🔍 Git kurulumunu doğrula"""
    print(f"{Colors.BOLD}{Colors.INFO}🔍 GİT DOĞRULAMASI BAŞLATILIYOR...{Colors.RESET}")

    checks = [
        ("Git Version", "git --version"),
        ("Git Config", "git config --list"),
        ("Git Remote", "git remote -v"),
        ("Git Status", "git status")
    ]

    git_ok = True

    for name, cmd in checks:
        print(f"\n{Colors.PROGRESS}🔍 {name} kontrol ediliyor...{Colors.RESET}")
        success, stdout, stderr = run_command(cmd)

        if success:
            print(f"{Colors.SUCCESS}✅ {name} OK{Colors.RESET}")
            if "git remote" in cmd and "github.com" in stdout:
                print(f"{Colors.SUCCESS}🔗 GitHub bağlantısı mevcut{Colors.RESET}")
        else:
            print(f"{Colors.ERROR}❌ {name} HATA: {stderr[:50]}{Colors.RESET}")
            git_ok = False

    return git_ok

def fix_git_issues():
    """🔧 Git sorunlarını düzelt"""
    print(f"\n{Colors.BOLD}{Colors.WARNING}🔧 GİT SORUNLARI DÜZELTİLİYOR...{Colors.RESET}")

    fixes = [
        ("Git Init", "git init"),
        ("Git Add Remote", "git remote add origin https://github.com/Schelebi/otto-platform.git"),
        ("Git Config User", "git config user.name \"Salih Çelebi\""),
        ("Git Config Email", "git config user.email \"salihchelebii@gmail.com\"")
    ]

    for name, cmd in fixes:
        print(f"{Colors.INFO}🔧 {name} uygulanıyor...{Colors.RESET}")
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"{Colors.SUCCESS}✅ {name} uygulandı{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}⚠️  {name} zaten mevcut{Colors.RESET}")

def run_persistent_tasks():
    """🔄 Başarılı olana kadar görevleri çalıştır"""
    print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🔄 PERSISTENT GÖREVLER BAŞLATILIYOR...{Colors.RESET}")

    tasks = [
        ("Git Add", "git add ."),
        ("Git Commit", 'git commit -m "Git verified automation"'),
        ("Git Push", "git push origin master"),
        ("API Test", "curl -I https://ottomans.onrender.com/api/cities"),
        ("Vercel Deploy", "npx vercel --prod")
    ]

    results = []

    for name, cmd in tasks:
        print(f"\n{Colors.INFO}🔄 {name} başlatılıyor...{Colors.RESET}")

        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            print(f"{Colors.PROGRESS}⏱️  Deneme {attempt}/{max_attempts}{Colors.RESET}")

            success, stdout, stderr = run_command(cmd, timeout=60)

            if success:
                print(f"{Colors.GREEN_BG}{Colors.BOLD}✅ {name} BAŞARILI!{Colors.RESET}")
                results.append((name, True))
                break
            else:
                print(f"{Colors.WARNING}⚠️  {name} başarısız (deneme {attempt}){Colors.RESET}")
                if attempt < max_attempts:
                    time.sleep(3)
                else:
                    print(f"{Colors.RED_BG}{Colors.BOLD}❌ {name} BAŞARISIZ!{Colors.RESET}")
                    results.append((name, False))

    return results

def generate_report(results):
    """📊 Rapor oluştur"""
    successful = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\n{Colors.BOLD}{Colors.INFO}📊 SONUÇ RAPORU{Colors.RESET}")
    print("="*60)
    print(f"{Colors.SUCCESS}✅ Başarılı: {successful}/{total}{Colors.RESET}")
    print(f"{Colors.ERROR}❌ Başarısız: {total-successful}{Colors.RESET}")
    print(f"{Colors.WARNING}📈 Başarı Oranı: {(successful/total*100):.1f}%{Colors.RESET}")

    print(f"\n{Colors.BOLD}{Colors.INFO}📋 DETAYLAR:{Colors.RESET}")
    for name, success in results:
        status = "✅" if success else "❌"
        color = Colors.SUCCESS if success else Colors.ERROR
        print(f"{color}  {status} {name}{Colors.RESET}")

    # JSON rapor
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "success_rate": successful/total*100,
        "results": [{"name": name, "success": success} for name, success in results]
    }

    with open("git_verified_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n{Colors.INFO}📄 Rapor kaydedildi: git_verified_report.json{Colors.RESET}")

    return successful == total

def main():
    """Ana akış"""
    print(f"{Colors.BOLD}{Colors.GREEN_BG}🔍 GİT DOĞRULAMALI OTOMASYON SİSTEMİ{Colors.RESET}")

    # 1. Git doğrula
    if not verify_git_setup():
        print(f"\n{Colors.WARNING}⚠️  Git sorunları tespit edildi, düzeltiliyor...{Colors.RESET}")
        fix_git_issues()

        # Tekrar doğrula
        if not verify_git_setup():
            print(f"{Colors.RED_BG}{Colors.BOLD}❌ Git sorunları düzeltilemedi!{Colors.RESET}")
            return False

    # 2. Görevleri çalıştır
    results = run_persistent_tasks()

    # 3. Rapor
    all_success = generate_report(results)

    # 4. Sonuç
    if all_success:
        print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🎉 TÜM GÖREVLER BAŞARILI!{Colors.RESET}")
        return True
    else:
        print(f"\n{Colors.BOLD}{Colors.YELLOW_BG}⚠️  BAZI GÖREVLER BAŞARISIZ{Colors.RESET}")
        print(f"{Colors.INFO}🔄 Sistem tekrar denemeye hazır...{Colors.RESET}")
        return False

if __name__ == "__main__":
    attempt = 1
    while True:
        print(f"\n{Colors.BOLD}{Colors.INFO}🔄 OTOMASYON DENEMESİ {attempt}{Colors.RESET}")

        if main():
            print(f"{Colors.GREEN_BG}{Colors.BOLD}🎉 BAŞARILI! Otomasyon tamamlandı.{Colors.RESET}")
            break
        else:
            attempt += 1
            print(f"{Colors.WARNING}⏰ 10 saniye bekleniyor...{Colors.RESET}")
            time.sleep(10)

            if attempt > 5:  # Maksimum deneme
                print(f"{Colors.RED_BG}{Colors.BOLD}⏰ Maksimum deneme sayısına ulaşıldı!{Colors.RESET}")
                break
