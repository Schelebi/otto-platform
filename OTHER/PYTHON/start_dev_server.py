#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ANISA GELİŞTİRME SUNUCUSU — TIKIR TIKIR TEST MODU
"""

import os, sys, time, subprocess, signal
from pathlib import Path
from datetime import datetime

ROOT = Path(os.getcwd())

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def check_port(port):
    """Portun kullanımda olup olmadığını kontrol et"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def kill_port(port):
    """Porttaki process'i öldür"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        log(f"Port {port} kapatıldı (PID: {pid})")
        else:  # Linux/Mac
            subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True)
    except Exception as e:
        log(f"Port kapatma hatası: {e}")

def start_dev_server():
    """Geliştirme sunucusunu başlat"""
    log("🚀 ANISA GELİŞTİRME SUNUCUSU BAŞLATILIYOR...")

    # 1. Port kontrolü
    port = 5173
    if check_port(port):
        log(f"⚠️ Port {port} kullanımda, kapatılıyor...")
        kill_port(port)
        time.sleep(2)

    # 2. Node.js kontrolü
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            log("❌ Node.js bulunamadı!")
            return False
        log(f"✅ Node.js mevcut: {result.stdout.strip()}")
    except:
        log("❌ Node.js kontrolü başarısız!")
        return False

    # 3. package.json kontrolü
    package_path = ROOT / "package.json"
    if not package_path.exists():
        log("❌ package.json bulunamadı!")
        return False
    log("✅ package.json mevcut")

    # 4. node_modules kontrolü
    node_modules = ROOT / "node_modules"
    if not node_modules.exists():
        log("⚠️ node_modules bulunamadı, npm install çalıştırılıyor...")
        try:
            subprocess.run(['npm', 'install'], cwd=ROOT, check=True)
            log("✅ npm install tamamlandı")
        except subprocess.CalledProcessError as e:
            log(f"❌ npm install başarısız: {e}")
            return False

    # 5. Vite sunucusunu başlat
    log("🔥 Vite geliştirme sunucusu başlatılıyor...")
    log(f"📍 Dizin: {ROOT}")
    log(f"🌐 Adres: http://localhost:{port}")
    log("="*50)

    try:
        # Windows için özel komut
        if os.name == 'nt':
            cmd = ['cmd', '/c', 'npm', 'run', 'dev']
        else:
            cmd = ['npm', 'run', 'dev']

        process = subprocess.Popen(
            cmd,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Gerçek zamanlı çıktı
        server_started = False
        while True:
            line = process.stdout.readline()
            if not line:
                break

            line = line.strip()
            if line:
                print(f"[VITE] {line}")

                # Sunucu başladığında kontrol et
                if "Local:" in line and "http" in line:
                    server_started = True
                    log("🎉 SUNUCU BAŞLADI!")
                    log(f"🌐 Tarayıcıda aç: http://localhost:{port}")
                    log("="*50)
                    log("⏳ 10 saniye içinde tarayıcıda otomatik açılacak...")

                    # Tarayıcıda otomatik aç
                    import webbrowser
                    time.sleep(2)
                    webbrowser.open(f"http://localhost:{port}")
                    log("✅ Tarayıcı açıldı!")

                # Hata mesajları
                if "ERROR" in line or "error" in line.lower():
                    log(f"⚠️ HATA: {line}")

                # Port bilgisi
                if "port" in line.lower() and str(port) in line:
                    log(f"✅ Port {port} aktif!")

        return_code = process.wait()
        if return_code == 0:
            log("✅ Sunucu başarıyla kapatıldı")
        else:
            log(f"⚠️ Sunucu hata ile kapandı (kod: {return_code})")

    except KeyboardInterrupt:
        log("\n⏹️ Sunucu kullanıcı tarafından durduruldu")
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            pass
    except Exception as e:
        log(f"❌ Sunucu başlatma hatası: {e}")
        return False

    return True

if __name__ == "__main__":
    try:
        success = start_dev_server()
        if success:
            log("🏁 İŞLEM BAŞARILI")
        else:
            log("💥 İŞLEM BAŞARISIZ")
            sys.exit(1)
    except Exception as e:
        log(f"💥 KRİTİK HATA: {e}")
        sys.exit(1)
