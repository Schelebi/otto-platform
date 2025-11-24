#!/usr/bin/env python3
"""
🚨 PUKOR DÖNGÜSÜ - KÜRESEL HATA YÖNETİM SİSTEMİ
P = PLANLA, U = UYGULA, K = KONTROL ET, O = ÖNLEM AL, R = RAPORLA
"""

import subprocess
import time
import json
import sys
import threading
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

# 🎨 RENK SİSTEMİ
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

# 🚨 KÜRESEL HATA SINIFLARI (ENUM)
class ErrorClass(Enum):
    NETWORK = "NETWORK"           # Ağ bağlantı sorunları
    SERVICE = "SERVICE"           # Servis çalışmıyor
    CONFIG = "CONFIG"             # Konfigürasyon hataları
    DEPLOYMENT = "DEPLOYMENT"     # Deployment sorunları
    TIMEOUT = "TIMEOUT"           # Zaman aşımı
    AUTH = "AUTH"                 # Yetkilendirme hataları
    SYSTEM = "SYSTEM"             # Sistem seviye hatalar

@dataclass
class ErrorAnalysis:
    error_class: ErrorClass
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    solution_path: str
    estimated_time: int  # saniye

class PUKOREngine:
    """PUKOR Döngüsü Motoru"""

    def __init__(self):
        self.start_time = time.time()
        self.results: List[Dict] = []
        self.max_timeout = 120  # 2 dakika maksimum

    # 🔍 OTOMATİK BİRLEŞİK HATA ANALİZ FONKSİYONU
    def analyze_error(self, error_code: int, error_message: str, url: str) -> ErrorAnalysis:
        """Hata sınıflaması ve çözüm yolu belirleme"""

        # 502 Bad Gateway - SERVICE sınıfı
        if error_code == 502:
            return ErrorAnalysis(
                error_class=ErrorClass.SERVICE,
                severity="HIGH",
                description="Backend servisi çalışmıyor veya yanıt vermiyor",
                solution_path="RESTART_SERVICE",
                estimated_time=60
            )

        # 404 Not Found - CONFIG sınıfı
        elif error_code == 404:
            return ErrorAnalysis(
                error_class=ErrorClass.CONFIG,
                severity="MEDIUM",
                description="API endpoint bulunamadı",
                solution_path="CHECK_ENDPOINTS",
                estimated_time=30
            )

        # 500 Internal Server Error - SYSTEM sınıfı
        elif error_code == 500:
            return ErrorAnalysis(
                error_class=ErrorClass.SYSTEM,
                severity="CRITICAL",
                description="Sunucu iç hatası",
                solution_path="CHECK_LOGS",
                estimated_time=90
            )

        # Network timeout - NETWORK sınıfı
        elif "timeout" in error_message.lower():
            return ErrorAnalysis(
                error_class=ErrorClass.NETWORK,
                severity="MEDIUM",
                description="Ağ zaman aşımı",
                solution_path="CHECK_CONNECTIVITY",
                estimated_time=45
            )

        # Varsayılan - SYSTEM sınıfı
        else:
            return ErrorAnalysis(
                error_class=ErrorClass.SYSTEM,
                severity="HIGH",
                description=f"Bilinmeyen hata: {error_code}",
                solution_path="INVESTIGATE",
                estimated_time=120
            )

    # 1️⃣ P — PLANLA (MANDATORY)
    def plan_solution(self, analysis: ErrorAnalysis) -> Dict[str, Any]:
        """AI tabanlı tahmini süre ile çözüm planla"""
        print(f"\n{Colors.BOLD}{Colors.INFO}📋 P — PLANLA{Colors.RESET}")
        print(f"🔍 Hata Sınıfı: {analysis.error_class.value}")
        print(f"⚠️  Şiddet: {analysis.severity}")
        print(f"📝 Açıklama: {analysis.description}")
        print(f"🛠️  Çözüm Yolu: {analysis.solution_path}")
        print(f"⏱️  Tahmini Süre: {analysis.estimated_time}s")

        plan = {
            "error_class": analysis.error_class,
            "solution_path": analysis.solution_path,
            "estimated_time": analysis.estimated_time,
            "timeout": min(analysis.estimated_time * 2, self.max_timeout)
        }

        print(f"{Colors.PROGRESS}✅ Plan hazır: {plan['timeout']}s timeout{Colors.RESET}")
        return plan

    # 2️⃣ U — UYGULA (MANDATORY)
    def apply_solution(self, plan: Dict[str, Any]) -> bool:
        """Planlanan çözümü uygula"""
        print(f"\n{Colors.BOLD}{Colors.WARNING}🔧 U — UYGULA{Colors.RESET}")

        solution_path = plan["solution_path"]
        start_time = time.time()

        try:
            if solution_path == "RESTART_SERVICE":
                return self._restart_backend_service(plan["timeout"])
            elif solution_path == "CHECK_ENDPOINTS":
                return self._check_endpoints(plan["timeout"])
            elif solution_path == "CHECK_LOGS":
                return self._check_backend_logs(plan["timeout"])
            elif solution_path == "CHECK_CONNECTIVITY":
                return self._check_connectivity(plan["timeout"])
            else:
                return self._investigate_issue(plan["timeout"])

        except Exception as e:
            print(f"{Colors.ERROR}❌ Uygulama hatası: {str(e)}{Colors.RESET}")
            return False

    def _restart_backend_service(self, timeout: int) -> bool:
        """Backend servisini yeniden başlat"""
        print(f"{Colors.INFO}🔄 Backend servisi yeniden başlatılıyor...{Colors.RESET}")

        # Render dashboard üzerinden manuel restart gerekli
        # Alternatif: API health check döngüsü
        for i in range(10):
            print(f"{Colors.PROGRESS}⏱️  Health check {i+1}/10{Colors.RESET}")

            success, stdout, stderr = self._run_command(f"curl -I https://ottomans.onrender.com/api/cities", timeout=10)

            if success and "200" in stdout:
                print(f"{Colors.SUCCESS}✅ Backend servisi çalışıyor!{Colors.RESET}")
                return True

            time.sleep(6)  # 60 saniye toplam

        return False

    def _check_endpoints(self, timeout: int) -> bool:
        """Endpoint'leri kontrol et"""
        endpoints = [
            "https://ottomans.onrender.com/api/cities",
            "https://ottomans.onrender.com/api/services",
            "https://ottomans.onrender.com/api/firms/search"
        ]

        for endpoint in endpoints:
            print(f"{Colors.INFO}🔍 {endpoint} kontrol ediliyor...{Colors.RESET}")
            success, stdout, stderr = self._run_command(f"curl -I {endpoint}", timeout=10)

            if not success:
                print(f"{Colors.ERROR}❌ {endpoint} başarısız{Colors.RESET}")
                return False

        return True

    def _check_backend_logs(self, timeout: int) -> bool:
        """Backend loglarını kontrol et"""
        # Render dashboard üzerinden manuel kontrol gerekli
        print(f"{Colors.WARNING}⚠️  Backend logları Render dashboard üzerinden kontrol edilmeli{Colors.RESET}")
        return False

    def _check_connectivity(self, timeout: int) -> bool:
        """Ağ bağlantısını kontrol et"""
        print(f"{Colors.INFO}🌐 Ağ bağlantısı kontrol ediliyor...{Colors.RESET}")

        # Google DNS test
        success, _, _ = self._run_command("ping -n 1 8.8.8.8", timeout=10)
        if success:
            print(f"{Colors.SUCCESS}✅ İnternet bağlantısı OK{Colors.RESET}")
            return True

        return False

    def _investigate_issue(self, timeout: int) -> bool:
        """Sorunu araştır"""
        print(f"{Colors.INFO}🔍 Sorun araştırılıyor...{Colors.RESET}")

        # Frontend çalışıyor mu?
        frontend_url = "https://otto-qqg9onomf-ottos-projects-52f5219c.vercel.app"
        success, stdout, stderr = self._run_command(f"curl -I {frontend_url}", timeout=10)

        if success:
            print(f"{Colors.SUCCESS}✅ Frontend çalışıyor{Colors.RESET}")
            print(f"{Colors.WARNING}⚠️  Sadece backend sorunlu{Colors.RESET}")
            return True

        return False

    # 3️⃣ K — KONTROL ET (MANDATORY)
    def verify_solution(self, original_analysis: ErrorAnalysis) -> bool:
        """Çözüm başarılı mı kontrol et"""
        print(f"\n{Colors.BOLD}{Colors.PROGRESS}✅ K — KONTROL ET{Colors.RESET}")

        # Orijinal sorunu tekrar test et
        success, stdout, stderr = self._run_command("curl -I https://ottomans.onrender.com/api/cities", timeout=30)

        if success and "200" in stdout:
            print(f"{Colors.SUCCESS}✅ Sorun çözüldü!{Colors.RESET}")
            return True
        else:
            print(f"{Colors.ERROR}❌ Sorun devam ediyor{Colors.RESET}")
            return False

    # 4️⃣ O — ÖNLEM AL + R — RAPORLA (MANDATORY)
    def take_precautions_and_report(self, analysis: ErrorAnalysis, success: bool) -> Dict:
        """Önlemler al ve raporla"""
        print(f"\n{Colors.BOLD}{Colors.INFO}🛡️  O — ÖNLEM AL + R — RAPORLA{Colors.RESET}")

        # Önlemler
        precautions = []

        if analysis.error_class == ErrorClass.SERVICE:
            precautions.append("Render auto-restart ayarları kontrol edilmeli")
            precautions.append("Health check endpoint'i eklenmeli")

        if analysis.error_class == ErrorClass.NETWORK:
            precautions.append("CDN ayarları gözden geçirilmeli")
            precautions.append("Load balancer kontrol edilmeli")

        # Rapor
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error_analysis": {
                "class": analysis.error_class.value,
                "severity": analysis.severity,
                "description": analysis.description,
                "solution_path": analysis.solution_path
            },
            "success": success,
            "precautions": precautions,
            "total_time": time.time() - self.start_time
        }

        # Çift formatlı rapor
        self._save_json_report(report)
        self._save_txt_report(report)

        return report

    def _save_json_report(self, report: Dict):
        """JSON formatında rapor kaydet"""
        with open("pukor_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"{Colors.INFO}📄 JSON rapor kaydedildi: pukor_report.json{Colors.RESET}")

    def _save_txt_report(self, report: Dict):
        """TXT formatında okunabilir rapor kaydet"""
        txt_content = f"""
🚨 PUKOR DÖNGÜSÜ RAPORU
{'='*50}

TARİH: {report['timestamp']}
HATA SINIFI: {report['error_analysis']['class']}
ŞİDDET: {report['error_analysis']['severity']}
AÇIKLAMA: {report['error_analysis']['description']}
ÇÖZÜM YOLU: {report['error_analysis']['solution_path']}

SONUÇ: {'✅ BAŞARILI' if report['success'] else '❌ BAŞARISIZ'}
SÜRE: {report['total_time']:.2f}s

ÖNLEMLER:
{chr(10).join(f'• {p}' for p in report['precautions'])}

{'='*50}
"""

        with open("pukor_report.txt", "w", encoding="utf-8") as f:
            f.write(txt_content)
        print(f"{Colors.INFO}📄 TXT rapor kaydedildi: pukor_report.txt{Colors.RESET}")

    def _run_command(self, cmd: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Komut çalıştır"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    # 🔄 PUKOR DÖNGÜSÜ
    def run_pukor_cycle(self, error_code: int, error_message: str, url: str) -> bool:
        """Tam PUKOR döngüsü çalıştır"""
        print(f"{Colors.BOLD}{Colors.RED_BG}🚨 PUKOR DÖNGÜSÜ BAŞLATILIYOR 🚨{Colors.RESET}")

        cycle_count = 0
        max_cycles = 3  # Maksimum 3 döngü

        while cycle_count < max_cycles:
            cycle_count += 1
            print(f"\n{Colors.BOLD}{Colors.WARNING}🔄 DÖNGÜ {cycle_count}/{max_cycles}{Colors.RESET}")

            # P — PLANLA
            analysis = self.analyze_error(error_code, error_message, url)
            plan = self.plan_solution(analysis)

            # U — UYGULA
            success = self.apply_solution(plan)

            # K — KONTROL ET
            if success:
                success = self.verify_solution(analysis)

            # O — ÖNLEM AL + R — RAPORLA
            report = self.take_precautions_and_report(analysis, success)
            self.results.append(report)

            if success:
                print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🎉 SORUN ÇÖZÜLDÜ!{Colors.RESET}")
                return True
            else:
                print(f"\n{Colors.WARNING}⚠️  Döngü devam ediyor...{Colors.RESET}")
                time.sleep(5)

        print(f"\n{Colors.BOLD}{Colors.RED_BG}❌ MAKSİMUM DÖNGÜ SAYISINA ULAŞILDI{Colors.RESET}")
        return False

def main():
    """Ana fonksiyon"""
    print(f"{Colors.BOLD}{Colors.RED_BG}🚨 PUKOR KÜRESEL HATA YÖNETİM SİSTEMİ{Colors.RESET}")

    # Backend 502 hatası tespit edildi
    engine = PUKOREngine()

    # PUKOR döngüsünü başlat
    success = engine.run_pukor_cycle(
        error_code=502,
        error_message="Bad Gateway",
        url="https://ottomans.onrender.com/api/cities"
    )

    if success:
        print(f"\n{Colors.BOLD}{Colors.GREEN_BG}🎉 TÜM SORUNLAR ÇÖZÜLDÜ!{Colors.RESET}")
    else:
        print(f"\n{Colors.BOLD}{Colors.RED_BG}❌ SORUNLAR DEVAM EDİYOR{Colors.RESET}")
        print(f"{Colors.WARNING}🔧 Manuel müdahale gerekebilir{Colors.RESET}")

if __name__ == "__main__":
    main()
