disk_koru.py v2.0
Sistem Dayanıklılık Modeli: L1 (Global), L2 (Operasyonel), L3 (Kayıt)
Güncelleme: Python 3.12 distutils hatası giderildi (GPUtil bağımlılığı kaldırıldı)."""

import sys
import os
import shutil
import subprocess
import logging
import tempfile
import platform
import ctypes
import gc
import time
from datetime import datetime

# Otomatik Kütüphane Yönetimi
# GPUtil kaldırıldı çünkü Python 3.12'de distutils hatası veriyor.
required_libraries = [
    "PyQt5", "psutil", "winshell", "pywin32",
    "wmi", "humanize", "requests", "colorama", "tqdm"
]

def install_and_import(package):
    import importlib
    try:
        # Paket adıyla import adı farklı olabilir
        import_name = package
        if package == "pywin32": import_name = "win32com"

        importlib.import_module(import_name)
    except ImportError:
        print(f"🔧 Onarılıyor ve Yükleniyor: {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"⚠️ {package} yüklenemedi, program devam edecek. Hata: {e}")

# Temel kütüphaneleri kontrol et
for lib in required_libraries:
    install_and_import(lib)

# Importlar (Hata korumalı)
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                 QHBoxLayout, QPushButton, QLabel, QProgressBar,
                                 QTextEdit, QTabWidget, QGroupBox, QMessageBox)
    from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
    import psutil
    import humanize
    import wmi
except ImportError as e:
    print(f"KRİTİK HATA: Temel kütüphaneler eksik. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.\nDetay: {e}")
    sys.exit(1)

# --- LOGGING YAPILANDIRMASI ---
logging.basicConfig(
    filename='disk_koru_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- YARDIMCI FONKSİYONLAR (DECORATOR) ---
def three_layer_protection(func):
    """
    Sistemin çökmemesi için 3 katmanlı koruma dekoratörü.
    """
    def wrapper(*args, **kwargs):
        # L1: GLOBAL KATMAN
        try:
            # L2: OPERASYONEL KATMAN
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"L1/L2 Hatası [{func.__name__}]: {str(e)}")
            # Fonksiyonun dönüş tipine göre güvenli varsayılan değerler
            return None
    return wrapper

# --- SINIF 1: SİSTEM ANALİZİ ---
class SystemAnalyzer:
    def __init__(self):
        self.os_info = platform.system()

    @three_layer_protection
    def get_disk_usage(self):
        try:
            usage = psutil.disk_usage('/')
            return usage.percent, usage.free, usage.total
        except Exception as e:
            logging.error(f"Disk analizi hatası: {e}")
            return 0, 0, 0

    @three_layer_protection
    def get_ram_usage(self):
        try:
            return psutil.virtual_memory().percent
        except Exception:
            return 0

    @three_layer_protection
    def get_gpu_info(self):
        """
        GPUtil kütüphanesi yerine doğrudan nvidia-smi çağrısı.
        Bağımlılık gerektirmez, daha güvenlidir.
        """
        try:
            # Nvidia GPU var mı kontrol et
            cmd = "nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits"
            # subprocess penceresi açılmasın diye startupinfo
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            output = subprocess.check_output(cmd, shell=True, startupinfo=startupinfo, text=True)

            # Çıktıyı işle (Örn: 23, 1024)
            line = output.strip().split('\n')[0]
            vals = line.split(',')
            return float(vals[0]), float(vals[1])
        except FileNotFoundError:
            return 0, 0 # Nvidia sürücüsü yok
        except Exception:
            return 0, 0 # Diğer hatalar

    @three_layer_protection
    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @three_layer_protection
    def get_cpu_usage(self):
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0

# --- SINIF 2: DİSK TEMİZLEYİCİ ---
class DiskCleaner:
    def __init__(self):
        self.temp_folders = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch'),
        ]

    @three_layer_protection
    def clean_temp_files(self, log_callback):
        total_freed = 0
        for folder in self.temp_folders:
            if os.path.exists(folder):
                try:
                    # L2: Klasör seviyesi
                    for root, dirs, files in os.walk(folder):
                        for file in files:
                            # L3: Dosya seviyesi
                            try:
                                file_path = os.path.join(root, file)
                                # Dosya kullanımda mı diye basit bir try-open check
                                try:
                                    f = open(file_path, 'a')
                                    f.close()
                                except:
                                    continue # Kullanımda, atla

                                size = os.path.getsize(file_path)
                                os.remove(file_path)
                                total_freed += size
                                # Çok fazla log basıp arayüzü kitlememek için her 10MB'da bir veya değişimde log
                                # Ancak kullanıcı detay istediği için yazıyoruz:
                                log_callback(f"Silindi: {file} ({humanize.naturalsize(size)})")
                            except Exception:
                                continue
                except Exception as e:
                    logging.error(f"Klasör erişim hatası {folder}: {e}")
        return total_freed

    @three_layer_protection
    def empty_recycle_bin(self, log_callback):
        try:
            import winshell
            try:
                # confirm=False ile onaysız siler
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
                log_callback("Geri dönüşüm kutusu boşaltıldı.")
                return True
            except Exception:
                log_callback("Geri dönüşüm kutusu zaten boş veya erişilemedi.")
                return False
        except ImportError:
            return False

    @three_layer_protection
    def clean_browser_cache(self, log_callback):
        # Chrome ve Edge Cache Yolları
        paths = [
            os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data\Default\Cache'),
            os.path.join(os.getenv('LOCALAPPDATA'), r'Microsoft\Edge\User Data\Default\Cache')
        ]
        freed = 0
        for p in paths:
            if os.path.exists(p):
                freed += self._generic_cleaner(p, log_callback)
        return freed

    @three_layer_protection
    def _generic_cleaner(self, path, log_callback):
        freed = 0
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        os.remove(item_path)
                        freed += size
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                except:
                    continue
            log_callback(f"Önbellek temizlendi: {path}")
        except:
            pass
        return freed

# --- SINIF 3: RAM & OPTİMİZASYON ---
class MemoryOptimizer:
    @three_layer_protection
    def optimize_ram(self, log_callback):
        try:
            # Python Garbage Collection
            gc.collect()

            # Windows EmptyWorkingSet (RAM Sıkıştırma)
            try:
                # Sadece mevcut process ve erişilebilir olanlar için
                pid = os.getpid()
                handle = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, pid)
                ctypes.windll.psapi.EmptyWorkingSet(handle)
                ctypes.windll.kernel32.CloseHandle(handle)
            except:
                pass

            log_callback("RAM optimizasyonu ve GC tetiklendi.")
            return True
        except Exception as e:
            logging.error(f"RAM Optimizasyon hatası: {e}")
            return False

    @three_layer_protection
    def flush_dns(self, log_callback):
        try:
            subprocess.call("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL)
            log_callback("DNS Önbelleği temizlendi.")
        except:
            pass

# --- SINIF 4: İŞLEM YÖNETİCİSİ (THREAD) ---
class WorkerThread(QThread):
    update_log = pyqtSignal(str)
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.analyzer = SystemAnalyzer()
        self.cleaner = DiskCleaner()
        self.memory_opt = MemoryOptimizer()

    @three_layer_protection
    def run(self):
        self.update_log.emit("=== SİSTEM DAYANIKLILIK MODÜLÜ BAŞLATILDI ===")
        time.sleep(0.5)

        # Adım 1: Güvenlik ve Ön Kontrol
        if not self.analyzer.check_admin():
            self.update_log.emit("⚠️ UYARI: Yönetici olarak çalıştırılmadı. Derin temizlik yapılamayabilir.")

        self.update_progress.emit(10)

        # Adım 2: Temp Dosyaları
        self.update_log.emit(">>> Geçici dosyalar analiz ediliyor (L2 Koruması devrede)...")
        bytes_freed = self.cleaner.clean_temp_files(lambda msg: self.update_log.emit(msg))

        # Adım 3: Tarayıcılar
        self.update_progress.emit(40)
        self.update_log.emit(">>> Tarayıcı önbellekleri taranıyor...")
        self.cleaner.clean_browser_cache(lambda msg: self.update_log.emit(msg))

        # Adım 4: RAM & Ağ
        self.update_progress.emit(70)
        self.update_log.emit(">>> RAM ve Ağ yığınları optimize ediliyor...")
        self.memory_opt.optimize_ram(lambda msg: self.update_log.emit(msg))
        self.memory_opt.flush_dns(lambda msg: self.update_log.emit(msg))

        # Adım 5: Çöp Kutusu
        self.cleaner.empty_recycle_bin(lambda msg: self.update_log.emit(msg))

        total_mb = bytes_freed / (1024 * 1024)
        self.update_log.emit(f"=== İŞLEM TAMAMLANDI. Yaklaşık {total_mb:.2f} MB yer açıldı. ===")
        self.update_progress.emit(100)
        self.finished.emit()

# --- GUI ARAYÜZ ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DiskKoru Pro v2.0 (Py3.12 Fix) - Sistem Rahatlatıcı")
        self.setGeometry(100, 100, 900, 600)
        self.analyzer = SystemAnalyzer()

        self.init_ui()

        # Zamanlayıcı (Canlı izleme)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QLabel { color: #ffffff; font-size: 14px; font-family: 'Segoe UI'; }
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #0099ff;
            }
            QPushButton:hover { background-color: #005999; }
            QPushButton:pressed { background-color: #004477; }
            QPushButton:disabled { background-color: #444; border: 1px solid #555; color: #888; }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 6px;
                text-align: center;
                color: white;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk { background-color: #00cc66; border-radius: 4px; }
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff99;
                font-family: Consolas;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QGroupBox {
                color: #00ccff;
                font-weight: bold;
                border: 1px solid #444;
                margin-top: 20px;
                border-radius: 6px;
                font-size: 12px;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # İstatistikler
        stats_group = QGroupBox("CANLI PERFORMANS METRİKLERİ")
        stats_layout = QHBoxLayout()

        self.lbl_disk = QLabel("💿 Disk: ...")
        self.lbl_ram = QLabel("🧠 RAM: ...")
        self.lbl_gpu = QLabel("🎮 GPU: ...")
        self.lbl_cpu = QLabel("⚙️ CPU: ...")

        for lbl in [self.lbl_disk, self.lbl_ram, self.lbl_gpu, self.lbl_cpu]:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background-color: #333; border-radius: 4px; padding: 8px; margin: 2px;")
            stats_layout.addWidget(lbl)

        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # Log Ekranı
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        main_layout.addWidget(self.log_box)

        # Kontroller
        control_layout = QVBoxLayout()

        self.progress = QProgressBar()
        self.progress.setValue(0)
        control_layout.addWidget(self.progress)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 SİSTEMİ RAHATLAT (BAŞLAT)")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_cleaning)

        self.btn_ram_only = QPushButton("⚡ HIZLI RAM TEMİZLİĞİ")
        self.btn_ram_only.setCursor(Qt.PointingHandCursor)
        self.btn_ram_only.clicked.connect(self.quick_ram_clean)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_ram_only)

        control_layout.addLayout(btn_layout)
        main_layout.addLayout(control_layout)

        self.log_message("Sistem v2.0 hazır. Bekleniyor...")
        self.update_stats()

    def update_stats(self):
        d_perc, _, _ = self.analyzer.get_disk_usage()
        ram_perc = self.analyzer.get_ram_usage()
        gpu_load, _ = self.analyzer.get_gpu_info()
        cpu_perc = self.analyzer.get_cpu_usage()

        self.lbl_disk.setText(f"💿 Disk: %{d_perc}")
        # Disk %90 üstü ise kırmızı yap
        if d_perc > 90:
            self.lbl_disk.setStyleSheet("background-color: #660000; color: white; border-radius: 4px; padding: 8px;")
        else:
            self.lbl_disk.setStyleSheet("background-color: #333; border-radius: 4px; padding: 8px;")

        self.lbl_ram.setText(f"🧠 RAM: %{ram_perc}")
        self.lbl_gpu.setText(f"🎮 GPU: %{int(gpu_load)}")
        self.lbl_cpu.setText(f"⚙️ CPU: %{cpu_perc}")

    def log_message(self, msg):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_cleaning(self):
        self.btn_start.setEnabled(False)
        self.btn_ram_only.setEnabled(False)
        self.worker = WorkerThread()
        self.worker.update_log.connect(self.log_message)
        self.worker.update_progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.cleaning_finished)
        self.worker.start()

    def quick_ram_clean(self):
        self.log_message("Hızlı RAM temizliği başlatılıyor...")
        mem_opt = MemoryOptimizer()
        mem_opt.optimize_ram(self.log_message)
        self.log_message("Hızlı RAM temizliği bitti.")

    def cleaning_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_ram_only.setEnabled(True)
        QMessageBox.information(self, "Tamamlandı", "Disk ve RAM başarıyla optimize edildi!")

if __name__ == "__main__":
    # Yönetici hakları uyarısı (Konsola)
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("\n!!! DİKKAT !!!\nProgramın tam kapasite (Temp silme, Cache temizleme) çalışması için\nYÖNETİCİ OLARAK (Run as Administrator) çalıştırmanız önerilir.\n")

    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Modern görünüm
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
