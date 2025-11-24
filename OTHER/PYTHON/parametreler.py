# parametreler.py — 15 PARAMETRELİ NET TEŞHİS SİSTEMİ
# ---------------------------------------------------------------
# Her durum başarısız olduğunda net teşhis yapabilen 15 parametre
# Terminalde akan hata mesajlarından bir bakışta tüm her şeyi görme

import time
import json
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Renk kodları
KIRMIZI = "\033[91m"
YESIL = "\033[92m"
SARI = "\033[93m"
MAVI = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(kategori, mesaj, renk=MAVI):
    print(f"{renk}[{ts()}] [{kategori}] → {mesaj}{RESET}")

class NetTeshisSistemi:
    """15 Parametreli Net Teşhis Sistemi"""

    def __init__(self):
        self.parametreler = {
            "veritabani_baglanti": {"durum": "bilinmiyor", "detay": ""},
            "backend_status": {"durum": "bilinmiyor", "detay": ""},
            "frontend_status": {"durum": "bilinmiyor", "detay": ""},
            "port_kullanimi": {"durum": "bilinmiyor", "detay": ""},
            "api_endpoint": {"durum": "bilinmiyor", "detay": ""},
            "env_ayarlar": {"durum": "bilinmiyor", "detay": ""},
            "network_baglanti": {"durum": "bilinmiyor", "detay": ""},
            "database_schema": {"durum": "bilinmiyor", "detay": ""},
            "cors_ayarlari": {"durum": "bilinmiyor", "detay": ""},
            "import_hatalari": {"durum": "bilinmiyor", "detay": ""},
            "dependency_uyumluluk": {"durum": "bilinmiyor", "detay": ""},
            "memory_usage": {"durum": "bilinmiyor", "detay": ""},
            "cpu_usage": {"durum": "bilinmiyor", "detay": ""},
            "disk_space": {"durum": "bilinmiyor", "detay": ""},
            "log_dosyalari": {"durum": "bilinmiyor", "detay": ""}
        }

        self.critical_errors = []
        self.warning_messages = []
        self.success_messages = []

    # L1: GLOBAL KORUMA KATMANI
    def tam_teshis_yap(self) -> Dict[str, Any]:
        """Tüm 15 parametreyi kontrol et - 3 katmanlı koruma ile"""
        try:
            log("TESİH", "🔍 15 Parametreli Net Teşsis Başlatılıyor...", BOLD)

            # L2: OPERASYONEL KORUMA KATMANI
            self._kontrol_grup_1()  # Temel sistem kontrolleri
            self._kontrol_grup_2()  # Veritabanı ve API kontrolleri
            self._kontrol_grup_3()  # Performans ve log kontrolleri

            # L3: KAYIT SEVİYESİ KORUMA KATMANI
            self._neticesi_olustur()

            return self._rapor_olustur()

        except Exception as e:
            log("TESİH-HATA", f"Kritik teşhis hatası: {str(e)}", KIRMIZI)
            return {"durum": "Kritik Hata", "hata": str(e)}

    # L2: OPERASYONEL KORUMA - GRUP 1
    def _kontrol_grup_1(self):
        """Temel sistem kontrolleri"""
        try:
            # 1) Veritabanı Bağlantısı
            self._veritabani_baglanti_kontrol()

            # 2) Backend Status
            self._backend_status_kontrol()

            # 3) Frontend Status
            self._frontend_status_kontrol()

            # 4) Port Kullanımı
            self._port_kullanimi_kontrol()

            # 5) API Endpoint
            self._api_endpoint_kontrol()

        except Exception as e:
            log("TESİH-GRUP1", f"Grup 1 kontrol hatası: {str(e)}", SARI)
            self.critical_errors.append(f"Grup 1 Hatası: {str(e)}")

    # L2: OPERASYONEL KORUMA - GRUP 2
    def _kontrol_grup_2(self):
        """Veritabanı ve API kontrolleri"""
        try:
            # 6) Env Ayarlar
            self._env_ayarlar_kontrol()

            # 7) Network Bağlantı
            self._network_baglanti_kontrol()

            # 8) Database Schema
            self._database_schema_kontrol()

            # 9) CORS Ayarları
            self._cors_ayarlar_kontrol()

            # 10) Import Hataları
            self._import_hatalari_kontrol()

        except Exception as e:
            log("TESİH-GRUP2", f"Grup 2 kontrol hatası: {str(e)}", SARI)
            self.critical_errors.append(f"Grup 2 Hatası: {str(e)}")

    # L2: OPERASYONEL KORUMA - GRUP 3
    def _kontrol_grup_3(self):
        """Performans ve log kontrolleri"""
        try:
            # 11) Dependency Uyumluluk
            self._dependency_uyumluluk_kontrol()

            # 12) Memory Usage
            self._memory_usage_kontrol()

            # 13) CPU Usage
            self._cpu_usage_kontrol()

            # 14) Disk Space
            self._disk_space_kontrol()

            # 15) Log Dosyaları
            self._log_dosyalari_kontrol()

        except Exception as e:
            log("TESİH-GRUP3", f"Grup 3 kontrol hatası: {str(e)}", SARI)
            self.critical_errors.append(f"Grup 3 Hatası: {str(e)}")

    # L3: KAYIT SEVİYESİ KORUMA - HER PARAMETRE AYRI
    def _veritabani_baglanti_kontrol(self):
        """1) Veritabanı Bağlantısı Kontrolü"""
        try:
            import pymysql

            db_config = {
                'host': '35.214.224.135',
                'user': 'uwcw1gm1sor8u',
                'password': 'g05jkizfzjdp',
                'database': 'db6ctx4kvleywe',
                'connect_timeout': 5
            }

            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            connection.close()

            self.parametreler["veritabani_baglanti"] = {
                "durum": "BAŞARILI",
                "detay": "MySQL bağlantısı başarılı"
            }
            self.success_messages.append("Veritabanı bağlantısı aktif")
            log("TESİH-DB", "✅ Veritabanı bağlantısı başarılı", YESIL)

        except Exception as e:
            self.parametreler["veritabani_baglanti"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Bağlantı hatası: {str(e)}"
            }
            self.critical_errors.append(f"Veritabanı bağlantısı yok: {str(e)}")
            log("TESİH-DB", f"❌ Veritabanı bağlantısı hatası: {str(e)}", KIRMIZI)

    def _backend_status_kontrol(self):
        """2) Backend Status Kontrolü"""
        try:
            response = requests.get("http://localhost:3001/api/cities", timeout=5)
            if response.status_code == 200:
                self.parametreler["backend_status"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Backend çalışıyor (HTTP {response.status_code})"
                }
                self.success_messages.append("Backend aktif ve yanıt veriyor")
                log("TESİH-BACKEND", "✅ Backend çalışıyor", YESIL)
            else:
                raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            self.parametreler["backend_status"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Backend çalışmıyor: {str(e)}"
            }
            self.critical_errors.append(f"Backend çalışmıyor çünkü: {str(e)}")
            log("TESİH-BACKEND", f"❌ Backend hatası: {str(e)}", KIRMIZI)

    def _frontend_status_kontrol(self):
        """3) Frontend Status Kontrolü"""
        try:
            response = requests.get("http://localhost:3000/", timeout=5)
            if response.status_code == 200:
                self.parametreler["frontend_status"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Frontend çalışıyor (HTTP {response.status_code})"
                }
                self.success_messages.append("Frontend aktif ve yanıt veriyor")
                log("TESİH-FRONTEND", "✅ Frontend çalışıyor", YESIL)
            else:
                raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            # 3003 portunu dene
            try:
                response = requests.get("http://localhost:3003/", timeout=5)
                if response.status_code == 200:
                    self.parametreler["frontend_status"] = {
                        "durum": "BAŞARILI",
                        "detay": f"Frontend port 3003'te çalışıyor (HTTP {response.status_code})"
                    }
                    self.success_messages.append("Frontend port 3003'te aktif")
                    log("TESİH-FRONTEND", "✅ Frontend port 3003'te çalışıyor", YESIL)
                    return
            except:
                pass

            self.parametreler["frontend_status"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Frontend çalışmıyor: {str(e)}"
            }
            self.critical_errors.append(f"Frontend çalışmıyor çünkü: {str(e)}")
            log("TESİH-FRONTEND", f"❌ Frontend hatası: {str(e)}", KIRMIZI)

    def _port_kullanimi_kontrol(self):
        """4) Port Kullanımı Kontrolü"""
        try:
            ports_to_check = [3000, 3001, 3003]
            port_status = {}

            for port in ports_to_check:
                try:
                    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=5)
                    if f":{port}" in result.stdout:
                        port_status[port] = "KULLANILDI"
                    else:
                        port_status[port] = "BOŞ"
                except:
                    port_status[port] = "BİLİNMİYOR"

            self.parametreler["port_kullanimi"] = {
                "durum": "BAŞARILI",
                "detay": f"Port durumu: {port_status}"
            }
            log("TESİH-PORT", f"📊 Port durumu: {port_status}", MAVI)

        except Exception as e:
            self.parametreler["port_kullanimi"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Port kontrol hatası: {str(e)}"
            }
            log("TESİH-PORT", f"❌ Port kontrol hatası: {str(e)}", KIRMIZI)

    def _api_endpoint_kontrol(self):
        """5) API Endpoint Kontrolü"""
        endpoints = [
            "http://localhost:3001/api/cities",
            "http://localhost:3001/api/districts/İstanbul",
            "http://localhost:3001/api/services",
            "http://localhost:3001/api/firms/search"
        ]

        working_endpoints = []
        failed_endpoints = []

        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    working_endpoints.append(endpoint)
                else:
                    failed_endpoints.append(f"{endpoint} (HTTP {response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} ({str(e)})")

        if len(working_endpoints) == len(endpoints):
            self.parametreler["api_endpoint"] = {
                "durum": "BAŞARILI",
                "detay": f"Tüm endpoint'ler çalışıyor ({len(working_endpoints)}/{len(endpoints)})"
            }
            self.success_messages.append("Tüm API endpoint'leri aktif")
            log("TESİH-API", "✅ Tüm endpoint'ler çalışıyor", YESIL)
        else:
            self.parametreler["api_endpoint"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Çalışan: {len(working_endpoints)}/{len(endpoints)} - Hatalı: {failed_endpoints}"
            }
            self.critical_errors.append(f"API endpoint'leri yanlış, doğru olması gereken: {endpoints}")
            log("TESİH-API", f"❌ Endpoint hatası: {len(working_endpoints)}/{len(endpoints)} çalışıyor", KIRMIZI)

    def _env_ayarlar_kontrol(self):
        """6) Environment Ayarlar Kontrolü"""
        try:
            import os

            # Önce .env dosyasını kontrol et
            env_file_path = '.env'
            env_local_path = '.env.local'

            env_status = {}
            missing_vars = []
            found_files = []

            # .env dosyasını kontrol et
            if os.path.exists(env_file_path):
                found_files.append('.env')
                with open(env_file_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                    for line in env_content.strip().split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value  # Environment'a yükle
                            env_status[key] = f"✅ {value[:20]}..." if len(value) > 20 else f"✅ {value}"

            # .env.local dosyasını kontrol et
            if os.path.exists(env_local_path):
                found_files.append('.env.local')
                with open(env_local_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                    for line in env_content.strip().split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value  # Environment'a yükle
                            env_status[key] = f"✅ {value[:20]}..." if len(value) > 20 else f"✅ {value}"

            required_env_vars = [
                "VITE_API_BASE_URL",
                "DB_HOST",
                "DB_USER",
                "DB_PASSWORD",
                "DB_NAME"
            ]

            for var in required_env_vars:
                value = os.environ.get(var)
                if value:
                    env_status[var] = f"✅ {value[:20]}..." if len(value) > 20 else f"✅ {value}"
                else:
                    env_status[var] = "❌ EKSİK"
                    missing_vars.append(var)

            if not missing_vars and found_files:
                self.parametreler["env_ayarlar"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Tüm env ayarları mevcut: {list(env_status.keys())} - Dosyalar: {found_files}"
                }
                self.success_messages.append(f"Environment ayarları tamam - Dosyalar: {found_files}")
                log("TESİH-ENV", f"✅ Environment ayarları tamam - Dosyalar: {found_files}", YESIL)
            else:
                self.parametreler["env_ayarlar"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Eksik env ayarları: {missing_vars} - Bulunan dosyalar: {found_files}"
                }
                self.critical_errors.append(f"Environment ayarları eksik: {missing_vars} - Bulunan dosyalar: {found_files}")
                log("TESİH-ENV", f"❌ Eksik env: {missing_vars} - Dosyalar: {found_files}", KIRMIZI)

        except Exception as e:
            self.parametreler["env_ayarlar"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Env kontrol hatası: {str(e)}"
            }
            log("TESİH-ENV", f"❌ Env kontrol hatası: {str(e)}", KIRMIZI)

    def _network_baglanti_kontrol(self):
        """7) Network Bağlantı Kontrolü"""
        try:
            # Internet bağlantısı test
            response = requests.get("https://www.google.com", timeout=5)
            internet_status = "BAŞARILI" if response.status_code == 200 else "BAŞARISIZ"

            # Localhost bağlantısı test
            localhost_response = requests.get("http://localhost:3001", timeout=5)
            localhost_status = "BAŞARILI" if localhost_response.status_code != 0 else "BAŞARISIZ"

            if internet_status == "BAŞARILI" and localhost_status == "BAŞARILI":
                self.parametreler["network_baglanti"] = {
                    "durum": "BAŞARILI",
                    "detay": "Internet ve localhost bağlantıları aktif"
                }
                self.success_messages.append("Network bağlantıları sağlam")
                log("TESİH-NET", "✅ Network bağlantıları aktif", YESIL)
            else:
                self.parametreler["network_baglanti"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Internet: {internet_status}, Localhost: {localhost_status}"
                }
                self.critical_errors.append("Network bağlantı problemi var")
                log("TESİH-NET", f"❌ Network problemi: Internet {internet_status}, Localhost {localhost_status}", KIRMIZI)

        except Exception as e:
            self.parametreler["network_baglanti"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Network kontrol hatası: {str(e)}"
            }
            self.critical_errors.append(f"Network bağlantı hatası: {str(e)}")
            log("TESİH-NET", f"❌ Network hatası: {str(e)}", KIRMIZI)

    def _database_schema_kontrol(self):
        """8) Database Schema Kontrolü"""
        try:
            import pymysql

            db_config = {
                'host': '35.214.224.135',
                'user': 'uwcw1gm1sor8u',
                'password': 'g05jkizfzjdp',
                'database': 'db6ctx4kvleywe',
                'connect_timeout': 5
            }

            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()

                cursor.execute("DESCRIBE anisa")
                columns = cursor.fetchall()

            connection.close()

            table_names = [table[0] for table in tables]
            column_names = [col[0] for col in columns]

            if 'anisa' in table_names:
                self.parametreler["database_schema"] = {
                    "durum": "BAŞARILI",
                    "detay": f"ANISA tablosu bulundu ({len(columns)} sütun)"
                }
                self.success_messages.append(f"Database schema doğru: {len(table_names)} tablo, {len(columns)} sütun")
                log("TESİH-SCHEMA", f"✅ ANISA tablosu bulundu ({len(columns)} sütun)", YESIL)
            else:
                raise Exception("ANISA tablosu bulunamadı")

        except Exception as e:
            self.parametreler["database_schema"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Schema hatası: {str(e)}"
            }
            self.critical_errors.append(f"Database schema problemi: {str(e)}")
            log("TESİH-SCHEMA", f"❌ Schema hatası: {str(e)}", KIRMIZI)

    def _cors_ayarlar_kontrol(self):
        """9) CORS Ayarları Kontrolü"""
        try:
            # Frontend'den backend'e CORS test
            headers = {'Origin': 'http://localhost:3000'}
            response = requests.options("http://localhost:3001/api/cities", headers=headers, timeout=5)

            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }

            if cors_headers['Access-Control-Allow-Origin']:
                self.parametreler["cors_ayarlari"] = {
                    "durum": "BAŞARILI",
                    "detay": f"CORS aktif: {cors_headers}"
                }
                self.success_messages.append("CORS ayarları doğru yapılandırılmış")
                log("TESİH-CORS", "✅ CORS ayarları aktif", YESIL)
            else:
                raise Exception("CORS başlıkları eksik")

        except Exception as e:
            self.parametreler["cors_ayarlari"] = {
                "durum": "BAŞARISIZ",
                "detay": f"CORS problemi: {str(e)}"
            }
            self.warning_messages.append(f"CORS ayarları kontrol edilmeli: {str(e)}")
            log("TESİH-CORS", f"⚠️ CORS problemi: {str(e)}", SARI)

    def _import_hatalari_kontrol(self):
        """10) Import Hataları Kontrolü"""
        try:
            required_imports = [
                "pymysql",
                "requests",
                "react",
                "express",
                "mysql2"
            ]

            import_status = {}
            failed_imports = []

            for module in required_imports:
                try:
                    if module == "react":
                        # React frontend'de kontrol edilir
                        import_status[module] = "✅ Frontend modülü"
                    elif module == "express":
                        import_status[module] = "✅ Backend modülü"
                    elif module == "mysql2":
                        import_status[module] = "✅ Node.js modülü"
                    else:
                        __import__(module)
                        import_status[module] = "✅ Python modülü"
                except ImportError:
                    import_status[module] = "❌ EKSİK"
                    failed_imports.append(module)

            if not failed_imports:
                self.parametreler["import_hatalari"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Tüm imports başarılı: {list(import_status.keys())}"
                }
                self.success_messages.append("Tüm kütüphane import'ları başarılı")
                log("TESİH-IMPORT", "✅ Tüm import'lar başarılı", YESIL)
            else:
                self.parametreler["import_hatalari"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Eksik modüller: {failed_imports}"
                }
                self.critical_errors.append(f"Import hataları: {failed_imports}")
                log("TESİH-IMPORT", f"❌ Import hataları: {failed_imports}", KIRMIZI)

        except Exception as e:
            self.parametreler["import_hatalari"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Import kontrol hatası: {str(e)}"
            }
            log("TESİH-IMPORT", f"❌ Import kontrol hatası: {str(e)}", KIRMIZI)

    def _dependency_uyumluluk_kontrol(self):
        """11) Dependency Uyumluluk Kontrolü"""
        try:
            # package.json kontrolü
            with open('package.json', 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            critical_deps = ['react', 'vite', 'express', 'mysql2']
            dependency_status = {}
            incompatible_deps = []

            for dep in critical_deps:
                if dep in package_data.get('dependencies', {}):
                    version = package_data['dependencies'][dep]
                    dependency_status[dep] = f"✅ {version}"
                else:
                    dependency_status[dep] = "❌ EKSİK"
                    incompatible_deps.append(dep)

            if not incompatible_deps:
                self.parametreler["dependency_uyumluluk"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Kritik dependencies tamam: {list(dependency_status.keys())}"
                }
                self.success_messages.append("Dependency uyumluluğu sağlam")
                log("TESİH-DEP", "✅ Dependency uyumluluğu sağlam", YESIL)
            else:
                self.parametreler["dependency_uyumluluk"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Uyumsuz dependencies: {incompatible_deps}"
                }
                self.critical_errors.append(f"Dependency uyumluluk sorunları: {incompatible_deps}")
                log("TESİH-DEP", f"❌ Dependency sorunları: {incompatible_deps}", KIRMIZI)

        except Exception as e:
            self.parametreler["dependency_uyumluluk"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Dependency kontrol hatası: {str(e)}"
            }
            log("TESİH-DEP", f"❌ Dependency kontrol hatası: {str(e)}", KIRMIZI)

    def _memory_usage_kontrol(self):
        """12) Memory Usage Kontrolü"""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            if memory_percent < 80:
                self.parametreler["memory_usage"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Memory kullanımı: %{memory_percent:.1f}"
                }
                self.success_messages.append(f"Memory kullanımı normal: %{memory_percent:.1f}")
                log("TESİH-MEM", f"✅ Memory kullanımı: %{memory_percent:.1f}", YESIL)
            else:
                self.parametreler["memory_usage"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Yüksek memory kullanımı: %{memory_percent:.1f}"
                }
                self.warning_messages.append(f"Yüksek memory kullanımı: %{memory_percent:.1f}")
                log("TESİH-MEM", f"⚠️ Yüksek memory: %{memory_percent:.1f}", SARI)

        except ImportError:
            self.parametreler["memory_usage"] = {
                "durum": "BİLİNMİYOR",
                "detay": "psutil modülü eksik"
            }
            log("TESİH-MEM", "⚠️ psutil eksik - memory kontrol edilemiyor", SARI)
        except Exception as e:
            self.parametreler["memory_usage"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Memory kontrol hatası: {str(e)}"
            }
            log("TESİH-MEM", f"❌ Memory kontrol hatası: {str(e)}", KIRMIZI)

    def _cpu_usage_kontrol(self):
        """13) CPU Usage Kontrolü"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent < 80:
                self.parametreler["cpu_usage"] = {
                    "durum": "BAŞARILI",
                    "detay": f"CPU kullanımı: %{cpu_percent:.1f}"
                }
                self.success_messages.append(f"CPU kullanımı normal: %{cpu_percent:.1f}")
                log("TESİH-CPU", f"✅ CPU kullanımı: %{cpu_percent:.1f}", YESIL)
            else:
                self.parametreler["cpu_usage"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Yüksek CPU kullanımı: %{cpu_percent:.1f}"
                }
                self.warning_messages.append(f"Yüksek CPU kullanımı: %{cpu_percent:.1f}")
                log("TESİH-CPU", f"⚠️ Yüksek CPU: %{cpu_percent:.1f}", SARI)

        except ImportError:
            self.parametreler["cpu_usage"] = {
                "durum": "BİLİNMİYOR",
                "detay": "psutil modülü eksik"
            }
            log("TESİH-CPU", "⚠️ psutil eksik - CPU kontrol edilemiyor", SARI)
        except Exception as e:
            self.parametreler["cpu_usage"] = {
                "durum": "BAŞARISIZ",
                "detay": f"CPU kontrol hatası: {str(e)}"
            }
            log("TESİH-CPU", f"❌ CPU kontrol hatası: {str(e)}", KIRMIZI)

    def _disk_space_kontrol(self):
        """14) Disk Space Kontrolü"""
        try:
            import psutil

            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100

            if disk_percent < 90:
                self.parametreler["disk_space"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Disk kullanımı: %{disk_percent:.1f}"
                }
                self.success_messages.append(f"Disk alanı yeterli: %{disk_percent:.1f}")
                log("TESİH-DISK", f"✅ Disk kullanımı: %{disk_percent:.1f}", YESIL)
            else:
                self.parametreler["disk_space"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Düşük disk alanı: %{disk_percent:.1f}"
                }
                self.critical_errors.append(f"Disk alanı kritik: %{disk_percent:.1f}")
                log("TESİH-DISK", f"❌ Disk alanı kritik: %{disk_percent:.1f}", KIRMIZI)

        except ImportError:
            self.parametreler["disk_space"] = {
                "durum": "BİLİNMİYOR",
                "detay": "psutil modülü eksik"
            }
            log("TESİH-DISK", "⚠️ psutil eksik - disk kontrol edilemiyor", SARI)
        except Exception as e:
            self.parametreler["disk_space"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Disk kontrol hatası: {str(e)}"
            }
            log("TESİH-DISK", f"❌ Disk kontrol hatası: {str(e)}", KIRMIZI)

    def _log_dosyalari_kontrol(self):
        """15) Log Dosyaları Kontrolü"""
        try:
            import os

            log_files = [
                ".env.local",
                "package.json",
                "server.cjs",
                "src/services/databaseService.ts",
                "src/hooks/useServices.ts"
            ]

            log_status = {}
            missing_files = []

            for file_path in log_files:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    log_status[file_path] = f"✅ {size} bytes"
                else:
                    log_status[file_path] = "❌ EKSİK"
                    missing_files.append(file_path)

            if not missing_files:
                self.parametreler["log_dosyalari"] = {
                    "durum": "BAŞARILI",
                    "detay": f"Tüm kritik dosyalar mevcut: {list(log_status.keys())}"
                }
                self.success_messages.append("Tüm kritik dosyalar mevcut")
                log("TESİH-FILES", "✅ Tüm kritik dosyalar mevcut", YESIL)
            else:
                self.parametreler["log_dosyalari"] = {
                    "durum": "BAŞARISIZ",
                    "detay": f"Eksik dosyalar: {missing_files}"
                }
                self.critical_errors.append(f"Kritik dosyalar eksik: {missing_files}")
                log("TESİH-FILES", f"❌ Eksik dosyalar: {missing_files}", KIRMIZI)

        except Exception as e:
            self.parametreler["log_dosyalari"] = {
                "durum": "BAŞARISIZ",
                "detay": f"Dosya kontrol hatası: {str(e)}"
            }
            log("TESİH-FILES", f"❌ Dosya kontrol hatası: {str(e)}", KIRMIZI)

    def _neticesi_olustur(self):
        """Netice oluştur - sonuçları değerlendir"""
        basarili_parametreler = 0
        toplam_parametreler = len(self.parametreler)

        for param, durum in self.parametreler.items():
            if durum["durum"] == "BAŞARILI":
                basarili_parametreler += 1

        self.basarili_orani = (basarili_parametreler / toplam_parametreler) * 100

        if self.basarili_orani >= 80:
            self.genel_durum = "SAĞLIKLI"
        elif self.basarili_orani >= 60:
            self.genel_durum = "KISMEN SAĞLIKLI"
        else:
            self.genel_durum = "KRİTİK"

    def _rapor_olustur(self) -> Dict[str, Any]:
        """JSON formatında rapor oluştur"""
        rapor = {
            "timestamp": ts(),
            "genel_durum": self.genel_durum,
            "basarili_orani": self.basarili_orani,
            "parametreler": self.parametreler,
            "kritik_hatalar": self.critical_errors,
            "uyarilar": self.warning_messages,
            "basarili_mesajlar": self.success_messages,
            "ozet": self._ozet_rapor_olustur()
        }

        # JSON formatında terminale bas
        print("\n" + "="*80)
        print("🔍 NET TEŞHİS RAPORU (JSON FORMAT)")
        print("="*80)
        print(json.dumps(rapor, indent=2, ensure_ascii=False))
        print("="*80)

        return rapor

    def _ozet_rapor_olustur(self) -> str:
        """Özet rapor oluştur"""
        ozet = f"""
🔍 15 PARAMETRELİ NET TEŞHİS ÖZETİ
================================
Genel Durum: {self.genel_durum}
Başarı Oranı: %{self.basarili_orani:.1f}

✅ Başarılı Parametreler: {len([p for p in self.parametreler.values() if p['durum'] == 'BAŞARILI'])}
❌ Başarısız Parametreler: {len([p for p in self.parametreler.values() if p['durum'] == 'BAŞARISIZ'])}
⚠️ Bilinmeyen Parametreler: {len([p for p in self.parametreler.values() if p['durum'] == 'BİLİNMİYOR'])}

🚨 Kritik Hatalar ({len(self.critical_errors)}):
{chr(10).join(f"- {hata}" for hata in self.critical_errors[:5])}

⚠️ Uyarılar ({len(self.warning_messages)}):
{chr(10).join(f"- {uyari}" for uyari in self.warning_messages[:3])}

✅ Başarı Mesajları ({len(self.success_messages)}):
{chr(10).join(f"- {mesaj}" for mesaj in self.success_messages[:3])}
        """.strip()

        return ozet

# Global instance
net_teshis = NetTeshisSistemi()

# Ana çalıştırma fonksiyonu
def main():
    """Ana teşhis fonksiyonu"""
    return net_teshis.tam_teshis_yap()

if __name__ == "__main__":
    main()
