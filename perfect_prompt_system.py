#!/usr/bin/env python3
"""
PERFECT PROMPT OTOMASYON SİSTEMİ
Tüm talimatlara uygun olarak ilerleme çubuğu, geri sayım,
hata yönetimi ve otomatik akış sağlar
"""

import asyncio
import time
import subprocess
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import sys

# Renkli terminal için ANSI kodları
class Colors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    PROGRESS = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class Status(Enum):
    PENDING = "⏳"
    RUNNING = "🔄"
    SUCCESS = "✅"
    ERROR = "❌"
    TIMEOUT = "⏰"

@dataclass
class TaskResult:
    name: str
    status: Status
    duration: float
    output: str
    error: Optional[str] = None
    steps: int = 0

class ProgressTimer:
    """Paralel geri sayım ve ilerleme çubuğu"""

    def __init__(self, duration: int = 30):
        self.duration = duration
        self.remaining = duration
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._countdown)
        self.thread.daemon = True
        self.thread.start()

    def _countdown(self):
        while self.remaining > 0 and self.running:
            progress = "█" * (self.remaining * 50 // self.duration)
            empty = "░" * (50 - len(progress))
            sys.stdout.write(f"\r{Colors.PROGRESS}⏱️  {self.remaining:2d}s [{progress}{empty}] {Colors.RESET}")
            sys.stdout.flush()
            time.sleep(1)
            self.remaining -= 1

        if self.running:
            sys.stdout.write(f"\r{Colors.WARNING}⏰ Süre doldu!{Colors.RESET}\n")
            sys.stdout.flush()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

class PerfectPromptSystem:
    """Perfect Prompt talimatlarına uygun otomasyon sistemi"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results: List[TaskResult] = []
        self.start_time = time.time()

    def run_command_with_progress(self, name: str, command: str, timeout: int = 60) -> TaskResult:
        """İlerleme çubuğu ve geri sayım ile komut çalıştır"""
        print(f"\n{Colors.INFO}🚀 {name} başlatılıyor...{Colors.RESET}")

        timer = ProgressTimer(min(timeout, 30))
        timer.start()

        start_time = time.time()
        steps = 0

        try:
            # Komutu paralel olarak çalıştır
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(subprocess.run, command, shell=True,
                                      capture_output=True, text=True, timeout=timeout)

                # İlerleme takibi
                while not future.done():
                    time.sleep(0.5)
                    steps += 1

                result = future.result(timeout=1)
                duration = time.time() - start_time

                timer.stop()

                if result.returncode == 0:
                    print(f"\r{Colors.SUCCESS}✅ {name} başarılı ({duration:.2f}s, {steps} adım){Colors.RESET}")
                    return TaskResult(name, Status.SUCCESS, duration, result.stdout, steps=steps)
                else:
                    print(f"\r{Colors.ERROR}❌ {name} başarısız ({duration:.2f}s){Colors.RESET}")
                    return TaskResult(name, Status.ERROR, duration, result.stdout, result.stderr, steps)

        except subprocess.TimeoutExpired:
            timer.stop()
            print(f"\r{Colors.WARNING}⏰ {name} zaman aşımına uğradı{Colors.RESET}")
            return TaskResult(name, Status.TIMEOUT, timeout, "", "Timeout", steps)
        except Exception as e:
            timer.stop()
            print(f"\r{Colors.ERROR}❌ {name} kritik hata: {str(e)}{Colors.RESET}")
            return TaskResult(name, Status.ERROR, time.time() - start_time, "", str(e), steps)

    def run_parallel_commands(self, tasks: List[Tuple[str, str]]) -> List[TaskResult]:
        """Paralel komut çalıştırma"""
        print(f"\n{Colors.BOLD}{Colors.INFO}🔄 {len(tasks)} paralel görev başlatılıyor...{Colors.RESET}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self.run_command_with_progress, name, cmd): (name, cmd)
                for name, cmd in tasks
            }

            results = []
            for future in as_completed(future_to_task):
                result = future.result()
                results.append(result)

        return results

    def generate_report(self) -> str:
        """Detaylı rapor üret"""
        total_time = time.time() - self.start_time
        successful = sum(1 for r in self.results if r.status == Status.SUCCESS)
        failed = len(self.results) - successful

        report = f"""
{Colors.BOLD}{Colors.INFO}📊 OTOMASYON RAPORU{Colors.RESET}
{'='*50}

{Colors.INFO}⏱️  Toplam Süre:{Colors.RESET} {total_time:.2f}s
{Colors.SUCCESS}✅ Başarılı:{Colors.RESET} {successful}
{Colors.ERROR}❌ Başarısız:{Colors.RESET} {failed}
{Colors.INFO}📈 Başarı Oranı:{Colors.RESET} {(successful/len(self.results)*100):.1f}%

{Colors.BOLD}{Colors.INFO}📋 DETAYLI SONUÇLAR:{Colors.RESET}
"""

        for result in self.results:
            status_icon = result.status.value
            color = Colors.SUCCESS if result.status == Status.SUCCESS else Colors.ERROR
            report += f"\n{color}{status_icon} {result.name}: {result.duration:.2f}s ({result.steps} adım){Colors.RESET}"
            if result.error:
                report += f"\n   {Colors.WARNING}Hata: {result.error[:100]}...{Colors.RESET}"

        # Hata çözüm önerileri
        if failed > 0:
            report += f"\n\n{Colors.WARNING}🔧 HATA ÇÖZÜM ÖNERİLERİ:{Colors.RESET}"
            report += "\n1. İnternet bağlantısını kontrol edin"
            report += "\n2. API servislerinin çalıştığını doğrulayın"
            report += "\n3. Environment değişkenlerini güncelleyin"
            report += "\n4. Build cache'ini temizleyin: npm run build --force"

        return report

    def save_report(self, filename: str = "automation_report.json"):
        """Raporu dosyaya kaydet"""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_time": time.time() - self.start_time,
            "results": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "duration": r.duration,
                    "steps": r.steps,
                    "error": r.error
                }
                for r in self.results
            ]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"{Colors.INFO}📄 Rapor kaydedildi: {filename}{Colors.RESET}")

def main():
    """Ana otomasyon akışı"""
    system = PerfectPromptSystem()

    print(f"{Colors.BOLD}{Colors.SUCCESS}🚀 PERFECT PROMPT OTOMASYON SİSTEMİ{Colors.RESET}")
    print(f"{Colors.INFO}Tüm talimatlara uygun olarak çalıştırılıyor...{Colors.RESET}")

    # Görevler listesi
    tasks = [
        ("GitHub Push", "git add . && git commit -m 'Perfect prompt automation' && git push origin master"),
        ("API Test", "curl -I https://ottomans.onrender.com/api/cities"),
        ("Vercel Deploy", "npx vercel --prod"),
        ("Build Check", "npm run build"),
        ("Environment Check", "npx vercel env ls")
    ]

    # Paralel çalıştır
    results = system.run_parallel_commands(tasks)
    system.results.extend(results)

    # Rapor üret
    print(system.generate_report())
    system.save_report()

    # Sonuç özeti
    successful = sum(1 for r in system.results if r.status == Status.SUCCESS)
    total = len(system.results)

    if successful == total:
        print(f"\n{Colors.BOLD}{Colors.SUCCESS}🎉 TÜM GÖREVLER BAŞARILI!{Colors.RESET}")
    else:
        print(f"\n{Colors.BOLD}{Colors.WARNING}⚠️  {total-successful} GÖREV BAŞARISIZ{Colors.RESET}")

if __name__ == "__main__":
    main()
