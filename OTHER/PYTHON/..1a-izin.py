# KOD ADI: ANISA.REACT.VITE.ENV.PREFLIGHT.RUNNER
# KOD YOLU (GÖRELİ): fix_env_and_run.py
# KODUN AMACI (5 MADDE):
# 1) Proje kökünde yazma izni ve temel dosya/klasör varlığını doğrular.
# 2) Ağ erişimini (npm registry) test ederek bağımlılık kurulumuna uygunluğu ölçer.
# 3) Node/NPM erişimini kontrol eder; eksikse net raporlar.
# 4) Tek seferlik npm install + npm test/build çalıştırır, sonsuz döngüye girmez.
# 5) Başarılı/başarısız tüm adımları rapor.txt'ye yazar ve terminale loglar.
# REVİZYONLAR:
# - REV-1: Paralel preflight kontrolleri eklendi (ThreadPoolExecutor).
# - REV-2: Rapor formatı "başarılılar sonra başarısızlar" olarak zorunlu hale getirildi.
# - REV-3: NPM komutları tek deneme + timeout ile güvenceye alındı.
# TALİMATLARIN KODLANMIŞ HALİ:
# - Üç katmanlı hata yönetimi (GLOBAL/OPERATIONAL/RECORD) uygulanır.
# - Her adım loglanır, hata sınıflandırılır, süreç durmadan raporlanır.
# - Reconnect/sonsuz retry yok: Her kritik komut 1 kez denenir.
# - Gereksiz dosya üretimi yok; sadece rapor.txt ve kısa geçici test dosyası.

from __future__ import annotations
import os
import sys
import json
import time
import shutil
import socket
import traceback
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# -----------------------------
# GLOBAL CONFIG
# -----------------------------
ROOT_DEFAULT = os.getcwd()
REPORT_PATH = os.path.join(ROOT_DEFAULT, "rapor.txt")
NETWORK_TEST_URL = "https://registry.npmjs.org/"
NPM_TIMEOUT_SEC = 600  # 10 dk hard timeout
PRINT_PREFIX = "🔥[ANISA-FIX]"

# -----------------------------
# LOGGING + RESULT MODELS
# -----------------------------
@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str = ""
    error: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Report:
    successes: List[StepResult] = field(default_factory=list)
    failures: List[StepResult] = field(default_factory=list)

    def add(self, result: StepResult):
        (self.successes if result.ok else self.failures).append(result)

    def to_text(self) -> str:
        lines: List[str] = []
        lines.append("=== RAPOR / BAŞARILI İŞLEMLER ===")
        if not self.successes:
            lines.append("- [OK] Başarılı adım yok.")
        else:
            for r in self.successes:
                lines.append(f"- [OK] {r.name}: {r.detail}")
        lines.append("")
        lines.append("=== RAPOR / BAŞARISIZ İŞLEMLER ===")
        if not self.failures:
            lines.append("- [X] Başarısız adım yok.")
        else:
            for r in self.failures:
                lines.append(f"- [X] {r.name}: {r.detail}")
                if r.error:
                    lines.append(f"  NEDEN: {r.error}")
        return "\n".join(lines)

def p(msg: str):
    print(f"{PRINT_PREFIX} {msg}")

def safe_write_report(rep: Report):
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(rep.to_text())
        p(f"✅ rapor.txt yazıldı → {REPORT_PATH}")
    except Exception as e:
        p(f"❌ rapor.txt yazılamadı: {e}")

# -----------------------------
# TRY LAYERS UTILITIES
# -----------------------------
def try_global(fn, step_name: str) -> StepResult:
    try:
        return fn()
    except Exception as e:
        return StepResult(
            name=step_name,
            ok=False,
            detail="GLOBAL try katmanında hata yakalandı.",
            error=f"{type(e).__name__}: {e}",
            extra={"traceback": traceback.format_exc()},
        )

def try_operational(fn, step_name: str) -> StepResult:
    try:
        return fn()
    except (OSError, URLError, HTTPError, subprocess.SubprocessError) as e:
        return StepResult(
            name=step_name,
            ok=False,
            detail="OPERATIONAL try katmanında kritik operasyon hatası.",
            error=f"{type(e).__name__}: {e}",
            extra={"traceback": traceback.format_exc()},
        )
    except Exception as e:
        return StepResult(
            name=step_name,
            ok=False,
            detail="OPERATIONAL try katmanında beklenmeyen hata.",
            error=f"{type(e).__name__}: {e}",
            extra={"traceback": traceback.format_exc()},
        )

def try_record(fn, step_name: str) -> StepResult:
    try:
        return fn()
    except Exception as e:
        return StepResult(
            name=step_name,
            ok=False,
            detail="RECORD try katmanında satır/öğe hatası.",
            error=f"{type(e).__name__}: {e}",
            extra={"traceback": traceback.format_exc()},
        )

# -----------------------------
# PREFLIGHT CHECKS
# -----------------------------
def check_root_structure(root: str) -> StepResult:
    def _impl():
        required = [
            "package.json",
            "tsconfig.json",
            "vite.config.ts",
            "index.html",
            "src",
            "src/index.tsx",
            "src/App.tsx",
            "src/services/apiService.ts",
            "src/services/apiClient.ts",
            "src/services/mockApiService.ts",
        ]
        missing = [r for r in required if not os.path.exists(os.path.join(root, r))]
        if missing:
            return StepResult(
                name="CHUNK-0/STRUCTURE",
                ok=False,
                detail=f"Eksik zorunlu yollar: {', '.join(missing)}",
                error="Proje yapısı eksik veya farklı konumda.",
            )
        return StepResult(
            name="CHUNK-0/STRUCTURE",
            ok=True,
            detail="Zorunlu dosya/klasörler mevcut.",
        )
    return try_operational(_impl, "CHUNK-0/STRUCTURE")

def check_write_access(root: str) -> StepResult:
    def _impl():
        test_file = os.path.join(root, ".write_test.tmp")
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test_file)
            return StepResult(
                name="CHUNK-0/WRITE_ACCESS",
                ok=True,
                detail="Yazma izni var.",
            )
        except Exception as e:
            return StepResult(
                name="CHUNK-0/WRITE_ACCESS",
                ok=False,
                detail="Yazma izni yok.",
                error=str(e),
            )
    return try_operational(_impl, "CHUNK-0/WRITE_ACCESS")

def check_node_npm() -> StepResult:
    def _impl():
        node = shutil.which("node")
        npm = shutil.which("npm")
        if not node or not npm:
            return StepResult(
                name="CHUNK-0/NODE_NPM",
                ok=False,
                detail=f"node={node}, npm={npm}",
                error="Node veya NPM bulunamadı; PATH kontrol et.",
            )
        return StepResult(
            name="CHUNK-0/NODE_NPM",
            ok=True,
            detail=f"node={node}, npm={npm}",
        )
    return try_operational(_impl, "CHUNK-0/NODE_NPM")

def check_network() -> StepResult:
    def _impl():
        req = Request(NETWORK_TEST_URL, headers={"User-Agent": "ANISA-FIX/1.0"})
        try:
            with urlopen(req, timeout=8) as resp:
                if resp.status >= 200 and resp.status < 400:
                    return StepResult(
                        name="CHUNK-0/NETWORK",
                        ok=True,
                        detail=f"npm registry erişimi OK (status={resp.status}).",
                    )
        except Exception as e:
            return StepResult(
                name="CHUNK-0/NETWORK",
                ok=False,
                detail="npm registry erişimi başarısız.",
                error=str(e),
            )
        return StepResult(
            name="CHUNK-0/NETWORK",
            ok=False,
            detail="npm registry erişimi başarısız.",
            error="Bilinmeyen ağ hatası.",
        )
    return try_operational(_impl, "CHUNK-0/NETWORK")

# -----------------------------
# COMMAND RUNNER (ONE SHOT)
# -----------------------------
def run_cmd(cmd: List[str], cwd: str, timeout: int, step_name: str) -> StepResult:
    def _impl():
        p(f"▶️ {step_name} çalıştırılıyor: {' '.join(cmd)}")
        start = time.time()
        try:
            out = subprocess.run(
                cmd,
                cwd=cwd,
                timeout=timeout,
                text=True,
                capture_output=True,
                shell=False,
            )
            dur = time.time() - start
            if out.returncode == 0:
                return StepResult(
                    name=step_name,
                    ok=True,
                    detail=f"OK ({dur:.1f}s)",
                    extra={"stdout": out.stdout[-2000:], "stderr": out.stderr[-2000:]},
                )
            return StepResult(
                name=step_name,
                ok=False,
                detail=f"Komut hata kodu döndürdü ({out.returncode})",
                error=out.stderr[-2000:] or out.stdout[-2000:] or "stderr/stdout boş",
                extra={"stdout": out.stdout[-2000:], "stderr": out.stderr[-2000:]},
            )
        except subprocess.TimeoutExpired as e:
            return StepResult(
                name=step_name,
                ok=False,
                detail=f"Timeout ({timeout}s) — tek deneme bitti.",
                error=str(e),
            )
    return try_operational(_impl, step_name)

def ensure_node_modules(root: str) -> StepResult:
    def _impl():
        nm = os.path.join(root, "node_modules")
        if os.path.isdir(nm):
            return StepResult(
                name="CHUNK-0/NODE_MODULES",
                ok=True,
                detail="node_modules zaten var.",
            )
        # one-shot npm install
        res = run_cmd(["npm", "install"], cwd=root, timeout=NPM_TIMEOUT_SEC, step_name="CHUNK-0/NPM_INSTALL")
        if not res.ok:
            return res
        if os.path.isdir(nm):
            return StepResult(
                name="CHUNK-0/NODE_MODULES",
                ok=True,
                detail="node_modules oluşturuldu.",
            )
        return StepResult(
            name="CHUNK-0/NODE_MODULES",
            ok=False,
            detail="npm install sonrası node_modules yok.",
            error="Kurulum tamamlanmadı veya farklı klasöre yazıldı.",
        )
    return try_global(_impl, "CHUNK-0/NODE_MODULES")

def run_tests_build(root: str) -> List[StepResult]:
    results: List[StepResult] = []
    # test
    results.append(run_cmd(["npm", "test"], cwd=root, timeout=NPM_TIMEOUT_SEC, step_name="CHUNK-6/NPM_TEST"))
    # build (dev server açmaz; blocking risk yok)
    results.append(run_cmd(["npm", "run", "build"], cwd=root, timeout=NPM_TIMEOUT_SEC, step_name="CHUNK-6/NPM_BUILD"))
    return results

# -----------------------------
# MAIN FLOW
# -----------------------------
def main():
    p("=== OTOMATİK ORTAM DÜZELTME + ÇALIŞTIRMA BAŞLADI ===")
    root = ROOT_DEFAULT
    rep = Report()

    p(f"📌 Proje kökü: {root}")

    # Parallel preflight checks
    preflight_tasks = {
        "structure": lambda: check_root_structure(root),
        "write": lambda: check_write_access(root),
        "node": check_node_npm,
        "net": check_network,
    }

    p("🧪 Preflight kontrolleri paralel başlıyor...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fn): name for name, fn in preflight_tasks.items()}
        for fut in as_completed(futures):
            res = fut.result()
            rep.add(res)
            if res.ok:
                p(f"✅ {res.name} → {res.detail}")
            else:
                p(f"❌ {res.name} → {res.detail} | {res.error}")

    # Gate: if write or node missing, stop heavy ops
    write_ok = any(r.name == "CHUNK-0/WRITE_ACCESS" and r.ok for r in rep.successes)
    node_ok = any(r.name == "CHUNK-0/NODE_NPM" and r.ok for r in rep.successes)
    net_ok = any(r.name == "CHUNK-0/NETWORK" and r.ok for r in rep.successes)

    if not write_ok:
        rep.add(StepResult(
            name="STOP/WRITE_REQUIRED",
            ok=False,
            detail="Yazma izni yok; otomasyon durduruldu.",
            error="Klasörü admin yetkisiyle aç veya izin ver.",
        ))
        safe_write_report(rep)
        p("🛑 Yazma izni olmadan devam edemem. Çıkıyorum.")
        return

    if not node_ok:
        rep.add(StepResult(
            name="STOP/NODE_REQUIRED",
            ok=False,
            detail="Node/NPM yok; otomasyon durduruldu.",
            error="Node.js + npm kur ve PATH'e ekle.",
        ))
        safe_write_report(rep)
        p("🛑 Node/NPM olmadan devam edemem. Çıkıyorum.")
        return

    if not net_ok:
        rep.add(StepResult(
            name="WARN/NETWORK",
            ok=False,
            detail="Ağ erişimi yok; npm install muhtemelen başarısız olacak.",
            error="VPN/Firewall/NAT kontrol et. Yine de 1 kez deneyeceğim.",
        ))
        p("⚠️ Ağ erişimi yok görünüyor, npm install tek deneme yapılacak.")

    # npm install / node_modules
    rep.add(ensure_node_modules(root))

    # If node_modules failed, stop
    nm_ok = any(r.name in ["CHUNK-0/NODE_MODULES", "CHUNK-0/NPM_INSTALL"] and r.ok for r in rep.successes)
    if not nm_ok:
        safe_write_report(rep)
        p("🛑 node_modules hazır değil; test/build aşaması atlandı.")
        return

    # tests + build
    p("🧨 Test + Build tek deneme başlıyor...")
    for r in run_tests_build(root):
        rep.add(r)
        if r.ok:
            p(f"✅ {r.name} → {r.detail}")
        else:
            p(f"❌ {r.name} → {r.detail} | {r.error}")

    safe_write_report(rep)
    p("=== OTOMASYON BİTTİ ===")

if __name__ == "__main__":
    main()
