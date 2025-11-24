#!/usr/bin/env python3
"""
Windows için Güvenli Perfect Prompt Otomasyon
"""

import subprocess
import time
import json
import os

class Colors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def run_safe_command(cmd):
    """Windows için güvenli komut çalıştır"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print(f"{Colors.BOLD}{Colors.SUCCESS}🚀 WINDOWS SAFE AUTOMATION{Colors.RESET}")

    tasks = [
        ("Git Status", "git status"),
        ("Git Add", "git add ."),
        ("Git Commit", 'git commit -m "Windows safe automation"'),
        ("Git Push", "git push origin master"),
        ("API Test", "curl -I https://ottomans.onrender.com/api/cities"),
        ("Vercel Deploy", "npx vercel --prod")
    ]

    results = []
    start_time = time.time()

    for name, cmd in tasks:
        print(f"\n{Colors.INFO}🔄 {name}{Colors.RESET}")

        success, stdout, stderr = run_safe_command(cmd)
        duration = time.time() - start_time

        if success:
            print(f"{Colors.SUCCESS}✅ {name} başarılı{Colors.RESET}")
            results.append((name, True, stdout, duration))
        else:
            print(f"{Colors.ERROR}❌ {name} başarısız{Colors.RESET}")
            if stderr:
                print(f"   {Colors.WARNING}Hata: {stderr[:100]}{Colors.RESET}")
            results.append((name, False, stderr, duration))

    # Rapor
    total_time = time.time() - start_time
    successful = sum(1 for _, success, _, _ in results if success)
    total = len(results)

    print(f"\n{Colors.BOLD}{Colors.INFO}📊 RAPOR{Colors.RESET}")
    print(f"⏱️ Süre: {total_time:.2f}s")
    print(f"✅ Başarılı: {successful}/{total}")
    print(f"📈 Oran: {(successful/total*100):.1f}%")

    # JSON kayıt
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_time": total_time,
        "success_rate": successful/total*100,
        "results": [{"name": name, "success": success} for name, success, _, _ in results]
    }

    with open("windows_automation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"{Colors.INFO}📄 Rapor kaydedildi{Colors.RESET}")

if __name__ == "__main__":
    main()
