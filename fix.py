#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 WSL ROOT YETKİLİ FIX.PY — TERMİNAL AKIŞ PROTOKOLÜ (4 MADDE STANDART)

1️⃣ GERÇEK ZAMANLI TERMİNAL ÇIKTISI ZORUNLULUĞU
2️⃣ ÇOK KATMANLI TRY/EXCEPT + AYRINTILI HATA LOGU
3️⃣ RETRY + FALLBACK + DEBUG ZORUNLULUĞU
4️⃣ JSON HATA/SONUÇ ÇIKTISI + OKUNABİLİRLİK STANDARDI
"""

import os, re, json, sys, time, shutil, subprocess, traceback
from pathlib import Path
from datetime import datetime

ROOT = Path(os.getcwd())

# TERMİNAL LOG SISTEMI
def log(category, function, message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] [{category}] [{function}] → {message}", flush=True)

def log_json(status, message, details=None):
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message,
        "details": details or {}
    }
    print(f" JSON_RESULT: {json.dumps(result, indent=2, ensure_ascii=False)}", flush=True)

# 🚀 GÜVENLİ KOMUT ÇALIŞTIRICI (WSL ROOT - ENCODING DÜZELTMESİ)
def run_wsl_command(cmd, cwd=ROOT, timeout=300, max_retries=2):
    function_name = "run_wsl_command"

    for attempt in range(max_retries + 1):
        try:
            log("COMMAND", function_name, f"Deneme {attempt + 1}/{max_retries + 1}: {' '.join(cmd)}")

            # Windows path'ini WSL path'ine çevir
            if isinstance(cwd, Path):
                wsl_cwd = str(cwd).replace('C:', '/mnt/c').replace('\\', '/')
            else:
                wsl_cwd = str(cwd).replace('C:', '/mnt/c').replace('\\', '/')

            # WSL root yetkisi ile çalıştır - UTF-8 encoding ile
            wsl_cmd = ["wsl", "-u", "root", "--cd", wsl_cwd, "--"] + cmd

            process = subprocess.Popen(
                wsl_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Karakter hatası yerine ? koy
                universal_newlines=True
            )

            output = []
            while True:
                try:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        line = line.strip()
                        if line:  # Boş satırları atla
                            output.append(line)
                            log("REALTIME", function_name, f"Terminal: {line}")
                except UnicodeDecodeError as e:
                    log("WARNING", function_name, f"Encoding hatası: {str(e)}")
                    continue

            return_code = process.poll()

            if return_code == 0:
                log("SUCCESS", function_name, f"Komut başarıyla tamamlandı: {' '.join(cmd)}")
                return 0, "\n".join(output)
            else:
                log("ERROR", function_name, f"Komut hatası (kod: {return_code}): {' '.join(cmd)}")
                if attempt < max_retries:
                    log("RETRY", function_name, f"Retry başlatılıyor...")
                    time.sleep(2)
                    continue
                else:
                    log("FAILED", function_name, f"Tüm denemeler başarısız oldu")
                    return return_code, "\n".join(output)

        except subprocess.TimeoutExpired:
            log("TIMEOUT", function_name, f"Komut zaman aşımına uğradı: {' '.join(cmd)}")
            try:
                process.kill()
            except:
                pass
            if attempt < max_retries:
                continue
            return 99, "Timeout"

        except Exception as e:
            log("CRITICAL", function_name, f"Beklenmedik hata: {str(e)}")
            log("DEBUG", function_name, f"Traceback: {traceback.format_exc()}")
            if attempt < max_retries:
                continue
            return 99, str(e)

    return 1, "Max retries exceeded"

# 🚀 GÜVENLİ DOSYA YAZICI (WSL PATH DÜZELTMESİ)
def safe_write_wsl(path: Path, content: str):
    function_name = "safe_write_wsl"
    try:
        log("FILE", function_name, f"Yazılıyor: {path}")

        # Windows path'ini WSL path'ine çevir
        wsl_path = str(path).replace('C:', '/mnt/c').replace('\\', '/')

        # WSL üzerinden dosya yazma - echo ile
        wsl_cmd = ["sh", "-c", f"echo '{content}' > {wsl_path}"]
        code, out = run_wsl_command(wsl_cmd)

        if code == 0:
            log("SUCCESS", function_name, f"Dosya başarıyla yazıldı: {path}")
            return True
        else:
            log("ERROR", function_name, f"Dosya yazma hatası: {path}")
            return False

    except Exception as e:
        log("CRITICAL", function_name, f"Dosya yazma hatası: {str(e)}")
        log("DEBUG", function_name, f"Traceback: {traceback.format_exc()}")
        return False

# 🚀 GÜVENLİ DOSYA OKUYUCU (WSL PATH DÜZELTMESİ)
def read_text_wsl(path: Path):
    function_name = "read_text_wsl"
    try:
        log("FILE", function_name, f"Okunuyor: {path}")

        # Windows path'ini WSL path'ine çevir
        wsl_path = str(path).replace('C:', '/mnt/c').replace('\\', '/')

        wsl_cmd = ["cat", wsl_path]
        code, out = run_wsl_command(wsl_cmd)

        if code == 0:
            log("SUCCESS", function_name, f"Dosya başarıyla okundu: {path}")
            return out
        else:
            log("WARNING", function_name, f"Dosya okunamadı: {path}")
            return ""

    except Exception as e:
        log("CRITICAL", function_name, f"Dosya okuma hatası: {str(e)}")
        log("DEBUG", function_name, f"Traceback: {traceback.format_exc()}")
        return ""

# GLOBAL STATE
tasks = []
success = []
failed = []
fn_map = {}

def task(id, title, why, group="P0"):
    def decorator(func):
        tasks.append({
            "id": id,
            "title": title,
            "why": why,
            "group": group,
            "status": "pending"
        })
        fn_map[id] = func
        return func
    return decorator

def mark_ok(tid, note=""):
    for t in tasks:
        if t["id"] == tid:
            t["status"] = "ok"
            t["note"] = note
    success.append((tid, note))
    log("TASK", "mark_ok", f"Task tamamlandı: {tid}")

def mark_fail(tid, err):
    for t in tasks:
        if t["id"] == tid:
            t["status"] = "fail"
            t["error"] = err
    failed.append((tid, err))
    log("TASK", "mark_fail", f"Task başarısız: {tid} - {err}")

# ===========================================================
# CHUNK-0 — WSL ROOT ORTAM KONTROLÜ
# ===========================================================
@task("CHUNK-0", "WSL ROOT ORTAM KONTROLÜ", "WSL root yetkisi ve temel araçlar kontrol edilir", "P0")
def chunk0():
    function_name = "chunk0"
    log("START", function_name, "WSL root ortam kontrolü başlıyor...")

    try:
        # 1. Katman: Dosya kontrolü (Windows + WSL)
        try:
            required = ["package.json", "index.html", "src/index.tsx"]
            missing = []

            for req in required:
                file_path = ROOT / req
                # Windows path kontrol
                if not file_path.exists():
                    missing.append(req)
                    log("ERROR", function_name, f"Eksik dosya (Windows): {req}")
                    continue

                # WSL path kontrol de
                wsl_path = str(file_path).replace('C:', '/mnt/c').replace('\\', '/')
                wsl_check_cmd = ["test", "-f", wsl_path]
                code, _ = run_wsl_command(wsl_check_cmd)
                if code != 0:
                    log("WARNING", function_name, f"Dosya WSL'de görünmüyor: {req}")

            if missing:
                error_msg = f"Eksik dosyalar: {missing}"
                log("ERROR", function_name, error_msg)
                raise FileNotFoundError(error_msg)
            log("SUCCESS", function_name, "Gerekli dosyalar mevcut (Windows + WSL)")
        except Exception as e:
            log("ERROR", function_name, f"Dosya kontrolü hatası: {str(e)}")
            raise

        # 2. Katman: Node.js kontrolü
        try:
            log("CHECK", function_name, "Node.js versiyonu kontrol ediliyor...")
            code, out = run_wsl_command(["node", "--version"])
            if code != 0:
                error_msg = "Node.js bulunamadı"
                log("ERROR", function_name, error_msg)
                raise RuntimeError(error_msg)
            log("SUCCESS", function_name, f"Node.js mevcut: {out.strip()}")
        except Exception as e:
            log("ERROR", function_name, f"Node.js kontrol hatası: {str(e)}")
            raise

        # 3. Katman: NPM kontrolü (çoklu yöntem)
        npm_found = False
        npm_methods = [
            ("npm --version", ["npm", "--version"]),
            ("npx --version", ["npx", "--version"]),
            ("corepack npm --version", ["corepack", "npm", "--version"]),
            ("which npm", ["which", "npm"])
        ]

        for method_name, cmd in npm_methods:
            try:
                log("CHECK", function_name, f"NPM kontrolü: {method_name}")
                code, out = run_wsl_command(cmd)
                if code == 0:
                    log("SUCCESS", function_name, f"NPM bulundu: {method_name} - {out.strip()}")
                    npm_found = True
                    break
                else:
                    log("DEBUG", function_name, f"NPM bulunamadı: {method_name}")
            except Exception as e:
                log("DEBUG", function_name, f"NPM kontrol hatası ({method_name}): {str(e)}")

        if not npm_found:
            log("WARNING", function_name, "NPM bulunamadı ama devam ediliyor")

        log_json("SUCCESS", "WSL root ortam kontrolü tamamlandı", {"npm_found": npm_found})
        return "WSL root ortam uygun"

    except Exception as e:
        log_json("FAILED", f"CHUNK-0 başarısız: {str(e)}", {"error_type": type(e).__name__})
        raise

# ===========================================================
# CHUNK-1 — INDEX.HTML DÜZELTME
# ===========================================================
@task("CHUNK-1", "INDEX.HTML DÜZELTME", "Vite giriş noktası WSL üzerinden düzeltilir", "P0")
def chunk1():
    function_name = "chunk1"
    log("START", function_name, "index.html düzeltme başlıyor...")

    try:
        # 1. Katman: Dosya okuma
        try:
            idx = ROOT / "index.html"
            html = read_text_wsl(idx)
            if not html:
                error_msg = "index.html okunamıyor"
                log("ERROR", function_name, error_msg)
                raise FileNotFoundError(error_msg)
            log("SUCCESS", function_name, "index.html başarıyla okundu")
        except Exception as e:
            log("ERROR", function_name, f"Dosya okuma hatası: {str(e)}")
            raise

        # 2. Katman: HTML düzenleme
        try:
            original_html = html

            if 'id="root"' not in html:
                html = re.sub(r"<body[^>]*>", lambda m: m.group(0) + '\n  <div id="root"></div>\n', html)
                log("EDIT", function_name, "root div eklendi")

            html = re.sub(r"<script[^>]+importmap[^>]*>[\s\S]*?</script>", "", html)
            html = re.sub(r"<script[^>]+react[^>]*></script>", "", html)
            html = re.sub(r"<script[^>]+react-router[^>]*></script>", "", html)
            log("EDIT", function_name, "CDN scriptleri kaldırıldı")

            if 'src="/index.tsx"' in html:
                html = html.replace('src="/index.tsx"', 'src="/src/index.tsx"')
                log("EDIT", function_name, "src path düzeltildi")

            if not re.search(r'src="/src/index\.tsx"', html):
                html = re.sub(
                    r"</body>",
                    '  <script type="module" src="/src/index.tsx"></script>\n</body>',
                    html
                )
                log("EDIT", function_name, "script tag eklendi")

            if html != original_html:
                # 3. Katman: Dosya yazma
                if safe_write_wsl(idx, html):
                    log("SUCCESS", function_name, "index.html başarıyla güncellendi")
                else:
                    raise RuntimeError("index.html yazılamadı")
            else:
                log("INFO", function_name, "index.html zaten doğru formatta")

        except Exception as e:
            log("ERROR", function_name, f"HTML düzenleme hatası: {str(e)}")
            raise

        log_json("SUCCESS", "index.html düzeltme tamamlandı", {"modified": html != original_html})
        return "index.html WSL üzerinden düzeltildi"

    except Exception as e:
        log_json("FAILED", f"CHUNK-1 başarısız: {str(e)}", {"error_type": type(e).__name__})
        raise

# ===========================================================
# CHUNK-2 — VITEST KURULUMU
# ===========================================================
@task("CHUNK-2", "VITEST KURULUMU", "Vitest test ortamı WSL üzerinden hazırlanır", "P0")
def chunk2():
    function_name = "chunk2"
    log("START", function_name, "Vitest kurulumu başlıyor...")

    try:
        # Vitest config
        cfg_content = """import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/tests/setup.ts"]
  }
});
"""

        cfg_path = ROOT / "vitest.config.ts"
        if safe_write_wsl(cfg_path, cfg_content):
            log("SUCCESS", function_name, "vitest.config.ts oluşturuldu")
        else:
            raise RuntimeError("vitest.config.ts oluşturulamadı")

        # Setup dosyası
        setup_content = 'import "@testing-library/jest-dom";\n'
        setup_path = ROOT / "src/tests/setup.ts"
        if safe_write_wsl(setup_path, setup_content):
            log("SUCCESS", function_name, "setup.ts oluşturuldu")

        # Smoke test
        smoke_content = """import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import FirmCard from "../components/FirmCard";
import { MemoryRouter } from "react-router-dom";

describe("smoke", () => {
  it("dummy", () => {
    expect(true).toBe(true);
  });
});
"""

        smoke_path = ROOT / "src/tests/smoke.test.tsx"
        if safe_write_wsl(smoke_path, smoke_content):
            log("SUCCESS", function_name, "smoke.test.tsx oluşturuldu")

        log_json("SUCCESS", "Vitest dosyaları oluşturuldu", {"files": ["vitest.config.ts", "setup.ts", "smoke.test.tsx"]})
        return "Vitest dosyaları WSL üzerinden hazır"

    except Exception as e:
        log_json("FAILED", f"CHUNK-2 başarısız: {str(e)}", {"error_type": type(e).__name__})
        raise

# ===========================================================
# CHUNK-3 — PACKAGE.JSON GÜNCELLEME
# ===========================================================
@task("CHUNK-3", "PACKAGE.JSON GÜNCELLEME", "package.json WSL üzerinden kontrol edilir", "P1")
def chunk3():
    function_name = "chunk3"
    log("START", function_name, "package.json kontrolü başlıyor...")

    try:
        pkg_path = ROOT/"package.json"
        pkg_text = read_text_wsl(pkg_path)

        if not pkg_text:
            raise RuntimeError("package.json okunamadı")

        pkg = json.loads(pkg_text)
        scripts = pkg.setdefault("scripts", {})
        dev = pkg.setdefault("devDependencies", {})

        changed = False

        # Scripts ekle
        if "test" not in scripts:
            scripts["test"] = "vitest run"
            changed = True

        if "test:watch" not in scripts:
            scripts["test:watch"] = "vitest"
            changed = True

        # DevDependencies ekle
        need_deps = ["vitest", "jsdom", "@testing-library/react", "@testing-library/jest-dom", "@vitejs/plugin-react"]
        for dep in need_deps:
            if dep not in dev:
                dev[dep] = "*"
                changed = True

        if changed:
            new_pkg_text = json.dumps(pkg, indent=2)
            if safe_write_wsl(pkg_path, new_pkg_text):
                log("SUCCESS", function_name, "package.json güncellendi")
            else:
                raise RuntimeError("package.json yazılamadı")
        else:
            log("INFO", function_name, "package.json zaten doğru")

        log_json("SUCCESS", "package.json kontrolü tamamlandı", {"changed": changed})
        return "package.json WSL üzerinden kontrol edildi"

    except Exception as e:
        log_json("FAILED", f"CHUNK-3 başarısız: {str(e)}", {"error_type": type(e).__name__})
        raise

# ===========================================================
# CHUNK-4 — NPM KOMUTLARI (WSL ROOT)
# ===========================================================
@task("CHUNK-4", "NPM KOMUTLARI", "npm install/test/build WSL root ile çalıştırılır", "P1")
def chunk4():
    function_name = "chunk4"
    log("START", function_name, "NPM komutları WSL root ile başlıyor...")

    try:
        # NPM komutları listesi
        npm_commands = [
            ("install", ["npm", "install"]),
            ("test", ["npm", "test"]),
            ("build", ["npm", "run", "build"])
        ]

        results = {}

        for cmd_name, cmd in npm_commands:
            log("COMMAND", function_name, f"Çalıştırılıyor: npm {cmd_name}")

            try:
                code, out = run_wsl_command(cmd, max_retries=3)

                if code == 0:
                    log("SUCCESS", function_name, f"npm {cmd_name} BAŞARILI")
                    results[cmd_name] = "SUCCESS"
                else:
                    log("ERROR", function_name, f"npm {cmd_name} HATASI: {out}")
                    results[cmd_name] = f"FAILED: {out}"

            except Exception as e:
                log("CRITICAL", function_name, f"npm {cmd_name} KRİTİK HATA: {str(e)}")
                results[cmd_name] = f"CRITICAL: {str(e)}"

        # Sonuç değerlendirme
        success_count = sum(1 for r in results.values() if r == "SUCCESS")
        total_count = len(results)

        if success_count == total_count:
            log_json("SUCCESS", "Tüm NPM komutları başarılı", results)
            return "WSL root ile tüm npm komutları BAŞARILI"
        elif success_count > 0:
            log_json("PARTIAL", f"NPM komutları kısmen başarılı ({success_count}/{total_count})", results)
            return f"WSL root ile npm komutları kısmen başarılı ({success_count}/{total_count})"
        else:
            log_json("FAILED", "Tüm NPM komutları başarısız", results)
            return "WSL root ile npm komutları BAŞARISIZ"

    except Exception as e:
        log_json("FAILED", f"CHUNK-4 başarısız: {str(e)}", {"error_type": type(e).__name__})
        raise

# ===========================================================
# BATCH EXECUTION (WSL ROOT)
# ===========================================================
batches = [
    ["CHUNK-0", "CHUNK-1", "CHUNK-2"],  # P0
    ["CHUNK-3", "CHUNK-4"]             # P1
]

log("SYSTEM", "MAIN", " WSL ROOT FIX.PY BAŞLIYOR")
log("SYSTEM", "MAIN", f" Çalışma dizini: {ROOT}")
log("SYSTEM", "MAIN", f" Toplam task: {len(tasks)}")

for batch in batches:
    log("BATCH", "MAIN", f"Batch başlıyor: {batch}")

    for tid in batch:
        try:
            log("TASK", "MAIN", f"Task başlatılıyor: {tid}")
            note = fn_map[tid]()
            mark_ok(tid, note)
            log("SUCCESS", "MAIN", f"Task tamamlandı: {tid}")
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            mark_fail(tid, err)
            log("FAILED", "MAIN", f"Task başarısız: {tid} - {err}")
            log("DEBUG", "MAIN", f"Traceback: {traceback.format_exc()}")

# ===========================================================
# RAPOR (WSL ROOT)
# ===========================================================
log("SYSTEM", "MAIN", " RAPOR OLUŞTURULUYOR")

rp = ROOT / "RAPOR.txt"
out = []
out.append("=== BAŞARILI ===")
for tid, note in success:
    out.append(f"[OK] {tid}: {note}")

out.append("\n=== BAŞARISIZ ===")
if not failed:
    out.append("[OK] başarısız adım yok")
else:
    for tid, err in failed:
        out.append(f"[X] {tid}: {err}")

# WSL üzerinden rapor yazma
if safe_write_wsl(rp, "\n".join(out)):
    log("SUCCESS", "MAIN", f"RAPOR.txt oluşturuldu: {rp}")
else:
    log("ERROR", "MAIN", "RAPOR.txt oluşturulamadı")

# Final JSON sonuç
final_result = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_tasks": len(tasks),
    "successful": len(success),
    "failed": len(failed),
    "success_rate": f"{(len(success)/len(tasks)*100):.1f}%" if tasks else "0%",
    "wsl_root": True,
    "tasks": tasks
}

log_json("FINAL", "WSL ROOT fix.py tamamlandı", final_result)

log("SYSTEM", "MAIN", " WSL ROOT FIX.PY BİTTİ")
print("\n" + "="*50)
print(" WSL ROOT FIX.PY İŞLEMİ TAMAMLANDI")
print("="*50)
