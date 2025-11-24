import os
import re
import json
from datetime import datetime
from pathlib import Path

ROOT = "c:/laragon/www/g/s/all"
REPORT = "c:/laragon/www/g/s/all/otto_api_report.md"

# 🔴 BACKEND ENPOINT PATTERNS DÜZELTİLDİ
backend_endpoint_pattern = re.compile(r"app\.(get|post|put|delete)\s*\(\s*['\"]([^'\"]+)['\"]")
frontend_endpoint_pattern = re.compile(r"(fetch|axios|swr)\s*\(\s*['\"]([^'\"]+)['\"]")
route_pattern = re.compile(r"path:\s*['\"](.*?)['\"]")
function_pattern = re.compile(r"function\s+(\w+)|const\s+(\w+)\s*=\s*\(")
import_pattern = re.compile(r"import.*from\s['\"](.*?)['\"]")
export_pattern = re.compile(r"export\s+(const|function)\s+(\w+)")

def scan_file(path):
    data = {
        "endpoints": [],
        "routes": [],
        "functions": [],
        "imports": [],
        "exports": [],
        "hooks": [],
        "components": [],
        "backend_endpoints": [],
        "api_columns": []
    }

    try:
        with open(path, "r", encoding="utf8", errors="ignore") as f:
            c = f.read()

            # 🔴 BACKEND ENPOINT TARAMASI EKLENDİ
            if path.endswith('.cjs') or path.endswith('.js'):
                backend_endpoints = backend_endpoint_pattern.findall(c)
                data["backend_endpoints"] = [ep[1] for ep in backend_endpoints]

                # 🔴 API COLUMN TARAMASI EKLENDİ (anisa tablosu)
                column_pattern = re.compile(r"col\.Field\.toLowerCase\(\)\.includes\(['\"](.*?)['\"]")
                columns = column_pattern.findall(c)
                data["api_columns"] = list(set(columns))

            # Frontend Endpoints (fetch/axios)
            endpoints = frontend_endpoint_pattern.findall(c)
            data["endpoints"] = [ep[1] for ep in endpoints]

            # Routes
            data["routes"] = route_pattern.findall(c)

            # Functions
            funcs = function_pattern.findall(c)
            flat_funcs = [x for t in funcs for x in t if x]
            data["functions"] = flat_funcs

            # Imports
            imports = import_pattern.findall(c)
            data["imports"] = imports

            # Exports
            exports = export_pattern.findall(c)
            data["exports"] = [exp[1] for exp in exports]

            # Hooks detection
            hook_pattern = re.compile(r"use\w+\s*\(")
            hooks = hook_pattern.findall(c)
            data["hooks"] = list(set(hooks))

            # Components detection
            component_pattern = re.compile(r"export\s+(default\s+)?(?:const|function)\s+(\w+).*?return\s*<")
            components = component_pattern.findall(c)
            data["components"] = [comp[1] for comp in components if comp[1]]

    except Exception as e:
        print(f"Hata: {path} - {e}")

    return data

def analyze_dependencies():
    """7 MADDE - Bağımsız modüller"""
    analysis = {
        "auth_modülü": [],
        "error_handler": [],
        "cache_listener": [],
        "service_mapper": [],
        "router_walker": [],
        "state_tracker": [],
        "component_scanner": []
    }

    # Auth modülü taraması
    auth_files = []
    for root, _, files in os.walk(ROOT):
        for f in files:
            if f.endswith((".ts", ".tsx")):
                p = os.path.join(root, f)
                try:
                    with open(p, "r", encoding="utf8", errors="ignore") as file:
                        content = file.read()
                        if any(word in content.lower() for word in ["auth", "login", "token", "user"]):
                            auth_files.append(p)
                except:
                    pass
    analysis["auth_modülü"] = auth_files

    # Error handler taraması
    error_files = []
    for root, _, files in os.walk(ROOT):
        for f in files:
            if f.endswith((".ts", ".tsx")):
                p = os.path.join(root, f)
                try:
                    with open(p, "r", encoding="utf8", errors="ignore") as file:
                        content = file.read()
                        if "try" in content and "catch" in content:
                            error_files.append(p)
                except:
                    pass
    analysis["error_handler"] = error_files

    return analysis

def walk():
    report = {}
    total_stats = {
        "total_files": 0,
        "total_functions": 0,
        "total_endpoints": 0,
        "total_routes": 0,
        "total_components": 0,
        "total_hooks": 0
    }

    for root, _, files in os.walk(ROOT):
        for f in files:
            if f.endswith((".js",".jsx",".ts",".tsx")):
                p = os.path.join(root, f)
                if "node_modules" not in p:
                    report[p] = scan_file(p)
                    total_stats["total_files"] += 1
                    total_stats["total_functions"] += len(report[p]["functions"])
                    total_stats["total_endpoints"] += len(report[p]["endpoints"])
                    total_stats["total_routes"] += len(report[p]["routes"])
                    total_stats["total_components"] += len(report[p]["components"])
                    total_stats["total_hooks"] += len(report[p]["hooks"])

    return report, total_stats

def write_markdown_report(data, stats, analysis):
    with open(REPORT, "w", encoding="utf8") as r:
        r.write("# 🚀 OTTO Rehberi - API & Component Analiz Raporu\n\n")
        r.write(f"**Oluşturuldu:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        r.write(f"**Proje:** OTTO - Türkiye Oto Çekici/Kurtarma Firmaları Rehberi\n")
        r.write(f"**Kök Dizin:** {ROOT}\n\n")

        # İstatistikler Tablosu
        r.write("## 📊 Genel İstatistikler\n\n")
        r.write("| Metrik | Değer |\n")
        r.write("|--------|-------|\n")
        r.write(f"| Toplam Dosya | {stats['total_files']} |\n")
        r.write(f"| Toplam Fonksiyon | {stats['total_functions']} |\n")
        r.write(f"| Toplam Endpoint | {stats['total_endpoints']} |\n")
        r.write(f"| Toplam Route | {stats['total_routes']} |\n")
        r.write(f"| Toplam Bileşen | {stats['total_components']} |\n")
        r.write(f"| Toplam Hook | {stats['total_hooks']} |\n\n")

        # 7 MADDE Analizi
        r.write("## 🔍 7 MADDE - Bağımsız Modül Analizi\n\n")
        r.write("| Modül | Dosya Sayısı | Dosyalar |\n")
        r.write("|-------|-------------|----------|\n")

        for modul, files in analysis.items():
            r.write(f"| {modul} | {len(files)} | {', '.join([Path(f).name for f in files[:3]])}{'...' if len(files) > 3 else ''} |\n")
        r.write("\n")

        # Dosya Detayları
        r.write("## 📁 Dosya Detayları\n\n")
        for file_path, info in sorted(data.items()):
            rel_path = Path(file_path).relative_to(ROOT)
            r.write(f"### 📄 {rel_path}\n\n")

            if info["functions"]:
                r.write(f"**Fonksiyonlar ({len(info['functions'])}):** {', '.join(info['functions'])}\n\n")

            if info["endpoints"]:
                r.write(f"**Endpoints ({len(info['endpoints'])}):** {', '.join(info['endpoints'])}\n\n")

            if info["routes"]:
                r.write(f"**Routes ({len(info['routes'])}):** {', '.join(info['routes'])}\n\n")

            if info["components"]:
                r.write(f"**Bileşenler ({len(info['components'])}):** {', '.join(info['components'])}\n\n")

            if info["hooks"]:
                r.write(f"**Hooks ({len(info['hooks'])}):** {', '.join(info['hooks'])}\n\n")

            if info["imports"]:
                r.write(f"**Imports:** {', '.join(info['imports'][:5])}{'...' if len(info['imports']) > 5 else ''}\n\n")

            r.write("---\n\n")

        # Endpoint Özeti
        r.write("## 🌐 Endpoint Özeti\n\n")
        all_endpoints = []
        for info in data.values():
            all_endpoints.extend(info["endpoints"])

        unique_endpoints = list(set(all_endpoints))
        r.write(f"**Toplam Unique Endpoint:** {len(unique_endpoints)}\n\n")
        r.write("| Endpoint | Kullanım Sayısı |\n")
        r.write("|----------|----------------|\n")

        for endpoint in unique_endpoints:
            count = all_endpoints.count(endpoint)
            r.write(f"| {endpoint} | {count} |\n")
        r.write("\n")

        # Component Özeti
        r.write("## 🧩 Component Özeti\n\n")
        all_components = []
        for info in data.values():
            all_components.extend(info["components"])

        unique_components = list(set(all_components))
        r.write(f"**Toplam Unique Component:** {len(unique_components)}\n\n")
        r.write("| Component | Dosya |\n")
        r.write("|-----------|-------|\n")

        for component in unique_components:
            for file_path, info in data.items():
                if component in info["components"]:
                    r.write(f"| {component} | {Path(file_path).relative_to(ROOT)} |\n")
                    break
        r.write("\n")

        r.write("---\n\n")
        r.write("*Rapor OTTO API Analiz Betiği tarafından otomatik oluşturuldu*\n")

if __name__ == "__main__":
    print("🔍 OTTO API Analizi Başlatılıyor...")
    result, stats = walk()
    analysis = analyze_dependencies()
    write_markdown_report(result, stats, analysis)
    print(f"✅ Rapor oluşturuldu: {REPORT}")
    print(f"📊 {stats['total_files']} dosya tarandı")
    print(f"🔧 {stats['total_functions']} fonksiyon bulundu")
    print(f"🔴 {stats.get('total_backend_endpoints', 0)} backend endpoint bulundu")
    print(f"🌐 {stats['total_endpoints']} frontend endpoint bulundu")
    print(f"📋 {stats.get('total_api_columns', 0)} API column bulundu")
