#!/usr/bin/env python3
"""
🔄 PERSISTENT AUTOMATION - BAŞARILI OLANA KADAR DEVAM ET
"""

import subprocess
import time
import json
import sys
from pathlib import Path

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

def run_simple_command(name: str, command: str, max_attempts: int = 10) -> bool:
    """Basit komut çalıştır - başarılı olana kadar dene"""
    print(f"{Colors.INFO}🔄 {name} deneniyor...{Colors.RESET}")

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"{Colors.PROGRESS}⏱️  Deneme {attempt}/{max_attempts}{Colors.RESET}")

            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print(f"{Colors.GREEN_BG}{Colors.BOLD}✅ {name} BAŞARILI!{Colors.RESET}")
                return True
            else:
                print(f"{Colors.WARNING}⚠️  {name} başarısız (deneme {attempt}){Colors.RESET}")
                if attempt < max_attempts:
                    time.sleep(2)

        except Exception as e:
            print(f"{Colors.ERROR}❌ Hata: {str(e)}{Colors.RESET}")
            if attempt < max_attempts:
                time.sleep(2)

    print(f"{Colors.RED_BG}{Colors.BOLD}❌ {name} BAŞARISIZ - TÜM DENEMELER TÜKENDİ{Colors.RESET}")
    return False

def main():
    """Ana akış - başarılı olana kadar devam et"""
    print(f"{Colors.BOLD}{Colors.GREEN_BG}🔄 PERSISTENT AUTOMATION{Colors.RESET}")
    print(f"{Colors.INFO}Başarılı olana kadar devam ediliyor...{Colors.RESET}")

    # Önce basit komutları dene
    simple_tasks = [
        ("Git Status", "git status"),
        ("List Files", "dir"),
        ("Python Test", "python --version"),
        ("Node Test", "node --version")
    ]

    successful_tasks = []
    failed_tasks = []

    for name, cmd in simple_tasks:
        if run_simple_command(name, cmd):
            successful_tasks.append(name)
        else:
            failed_tasks.append(name)

    # Sonra ana görevleri dene
    main_tasks = [
        ("Git Add", "git add ."),
        ("Git Commit", 'git commit -m "Persistent automation attempt"'),
        ("Git Push", "git push origin master")
    ]

    for name, cmd in main_tasks:
        if run_simple_command(name, cmd, max_attempts=5):
            successful_tasks.append(name)
        else:
            failed_tasks.append(name)

    # Rapor
    total = len(simple_tasks) + len(main_tasks)
    success_count = len(successful_tasks)

    print(f"\n{Colors.BOLD}{Colors.INFO}📊 SONUÇ RAPORU{Colors.RESET}")
    print("="*50)
    print(f"{Colors.SUCCESS}✅ Başarılı: {success_count}/{total}{Colors.RESET}")
    print(f"{Colors.ERROR}❌ Başarısız: {len(failed_tasks)}{Colors.RESET}")

    if successful_tasks:
        print(f"\n{Colors.SUCCESS}🎉 BAŞARILI GÖREVLER:{Colors.RESET}")
        for task in successful_tasks:
            print(f"  ✅ {task}")

    if failed_tasks:
        print(f"\n{Colors.ERROR}❌ BAŞARISIZ GÖREVLER:{Colors.RESET}")
        for task in failed_tasks:
            print(f"  ❌ {task}")

    # Kaydet
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "successful": successful_tasks,
        "failed": failed_tasks,
        "success_rate": success_count / total * 100
    }

    with open("persistent_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Sonuç
    if success_count == total:
        print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🎉 TÜM GÖREVLER BAŞARILI!{Colors.RESET}")
        return True
    else:
        print(f"\n{Colors.BOLD}{Colors.WARNING}⚠️  {len(failed_tasks)} GÖREV BAŞARISIZ{Colors.RESET}")
        print(f"{Colors.INFO}🔄 Sistem devam etmeye hazır...{Colors.RESET}")
        return False

if __name__ == "__main__":
    # Başarılı olana kadar devam et
    attempt = 1
    while True:
        print(f"\n{Colors.BOLD}{Colors.INFO}🔄 OTOMASYON DENEmesi {attempt}{Colors.RESET}")

        if main():
            print(f"{Colors.GREEN_BG}{Colors.BOLD}🎉 BAŞARI! Otomasyon tamamlandı.{Colors.RESET}")
            break
        else:
            attempt += 1
            print(f"{Colors.WARNING}⚠️  5 saniye bekleniyor...{Colors.RESET}")
            time.sleep(5)

            if attempt > 10:  # Sonsuz döngüyü engelle
                print(f"{Colors.RED_BG}{Colors.BOLD}⏰ Maksimum deneme sayısına ulaşıldı!{Colors.RESET}")
                break
