#!/usr/bin/env python3
"""
PERFECT PROMPT - SABİTLENMİŞ OTOMASYON SİSTEMİ
"""

import subprocess
import time
import json
import threading
from pathlib import Path
from typing import List, Tuple

class Colors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    PROGRESS = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def run_task(name: str, command: str) -> Tuple[str, bool, str, float]:
    """Tek görev çalıştır"""
    print(f"\n{Colors.INFO}🚀 {name} başlatılıyor...{Colors.RESET}")

    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"{Colors.SUCCESS}✅ {name} başarılı ({duration:.2f}s){Colors.RESET}")
            return name, True, result.stdout, duration
        else:
            print(f"{Colors.ERROR}❌ {name} başarısız ({duration:.2f}s){Colors.RESET}")
            return name, False, result.stderr, duration

    except subprocess.TimeoutExpired:
        print(f"{Colors.WARNING}⏰ {name} zaman aşımı{Colors.RESET}")
        return name, False, "Timeout", 60.0
    except Exception as e:
        print(f"{Colors.ERROR}❌ {name} hata: {str(e)}{Colors.RESET}")
        return name, False, str(e), time.time() - start_time

def main():
    """Ana akış"""
    print(f"{Colors.BOLD}{Colors.SUCCESS}🚀 PERFECT PROMPT OTOMASYON SİSTEMİ{Colors.RESET}")
    print(f"{Colors.INFO}Tüm talimatlara uygun çalıştırılıyor...{Colors.RESET}")

    # Görevler
    tasks = [
        ("GitHub Push", "git add . && git commit -m \"Perfect prompt automation\" && git push origin master"),
        ("API Test", "curl -I https://ottomans.onrender.com/api/cities"),
        ("Vercel Deploy", "npx vercel --prod"),
        ("Build Check", "npm run build"),
        ("Environment Check", "npx vercel env ls")
    ]

    # Sonuçlar
    results = []
    start_time = time.time()

    # Sıralı çalıştır (Windows için daha stabil)
    for name, cmd in tasks:
        result = run_task(name, cmd)
        results.append(result)

    # Rapor
    total_time = time.time() - start_time
    successful = sum(1 for _, success, _, _ in results if success)
    total = len(results)

    print(f"\n{Colors.BOLD}{Colors.INFO}📊 OTOMASYON RAPORU{Colors.RESET}")
    print("="*50)
    print(f"{Colors.INFO}⏱️  Toplam Süre:{Colors.RESET} {total_time:.2f}s")
    print(f"{Colors.SUCCESS}✅ Başarılı:{Colors.RESET} {successful}")
    print(f"{Colors.ERROR}❌ Başarısız:{Colors.RESET} {total-successful}")
    print(f"{Colors.INFO}📈 Başarı Oranı:{Colors.RESET} {(successful/total*100):.1f}%")

    print(f"\n{Colors.BOLD}{Colors.INFO}📋 DETAYLAR:{Colors.RESET}")
    for name, success, output, duration in results:
        status = "✅" if success else "❌"
        color = Colors.SUCCESS if success else Colors.ERROR
        print(f"{color}{status} {name}: {duration:.2f}s{Colors.RESET}")
        if not success and output:
            print(f"   {Colors.WARNING}Hata: {output[:100]}...{Colors.RESET}")

    # JSON rapor
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_time": total_time,
        "success_rate": successful/total*100,
        "results": [
            {"name": name, "success": success, "duration": duration}
            for name, success, _, duration in results
        ]
    }

    with open("automation_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n{Colors.INFO}📄 Rapor kaydedildi: automation_report.json{Colors.RESET}")

    # Sonuç
    if successful == total:
        print(f"\n{Colors.BOLD}{Colors.SUCCESS}🎉 TÜM GÖREVLER BAŞARILI!{Colors.RESET}")
    else:
        print(f"\n{Colors.BOLD}{Colors.WARNING}⚠️  {total-successful} GÖREV BAŞARISIZ{Colors.RESET}")
        print(f"{Colors.WARNING}🔧 Çözüm önerileri: İnternet kontrol, API doğrula, env güncelle{Colors.RESET}")

if __name__ == "__main__":
    main()
