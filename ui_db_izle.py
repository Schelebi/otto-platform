#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI-DB İZLE v1.0 - 3 KATMANLI DAYANIKLI TEST SİSTEMİ
Tüm arayüz öğelerini otomatik keşfeder, DB ile kablolar ve raporlar
Her hata seviyesine göre yakalanır, sistem asla çökmez
"""

import os, sys, re, json, time, asyncio, traceback, subprocess, signal, difflib
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque

ROOT = Path(__file__).resolve().parent

# ----------------------------
# 0) OTOMATİK KÜTÜPHANE KURULUMU
# ----------------------------
EXT_LIBS = [
    ("playwright", "playwright"),
    ("psutil", "psutil"),
    ("pymysql", "pymysql"),
]

def p(msg: str):
    """Renkli terminal çıktısı"""
    colors = {
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'RESET': '\033[0m'
    }

    # Mesaj tipine göre renk seç
    if '✅' in msg or 'BAŞARILI' in msg:
        color = colors['GREEN']
    elif '❌' in msg or 'HATA' in msg or 'ERROR' in msg:
        color = colors['RED']
    elif '⚠️' in msg or 'UYARI' in msg:
        color = colors['YELLOW']
    elif '🔍' in msg or 'TEST' in msg:
        color = colors['BLUE']
    elif '📊' in msg or 'RAPOR' in msg:
        color = colors['CYAN']
    else:
        color = colors['WHITE']

    print(f"{color}{msg}{colors['RESET']}", flush=True)

def ensure_lib(import_name: str, pip_name: str):
    try:
        __import__(import_name)
        p(f"✅ {import_name} mevcut")
    except Exception:
        p(f"⚠️ {import_name} yok, kuruluyor -> {pip_name}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pip_name])
            __import__(import_name)
            p(f"✅ {import_name} kuruldu")
        except Exception as e:
            p(f"❌ {import_name} kurulamadı: {e}")
            raise

for imp, pipn in EXT_LIBS:
    ensure_lib(imp, pipn)

from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError
import psutil
import pymysql

# ----------------------------
# 1) ENV OKUMA (OTOMATİK)
# ----------------------------
def read_env_file(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.exists():
        return env
    try:
        for raw in path.read_text("utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
            if not m:
                continue
            k, v = m.group(1), m.group(2).strip()
            if v and len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            env[k] = v
    except Exception as e:
        p(f"❌ Env okuma hatası: {e}")
    return env

def load_env() -> Dict[str, str]:
    env_path = ROOT / ".env.local"
    env = read_env_file(env_path)
    for k, v in env.items():
        os.environ.setdefault(k, v)
    p(f"✅ Env yüklendi: {len(env)} değişken")
    return env

# ----------------------------
# 2) FRONTEND URL OTOMATİK BULMA
# ----------------------------
async def detect_frontend_url() -> str:
    candidates: List[str] = []
    for k in ["VITE_DEV_URL", "FRONTEND_URL", "DEV_URL", "VITE_ORIGIN"]:
        v = os.environ.get(k)
        if v:
            candidates.append(v.rstrip("/"))

    vite_cfg = ROOT / "vite.config.ts"
    if vite_cfg.exists():
        try:
            txt = vite_cfg.read_text("utf-8", errors="ignore")
            m = re.search(r"port\s*:\s*(\d+)", txt)
            if m:
                port = int(m.group(1))
                candidates.append(f"http://localhost:{port}")
        except Exception:
            pass

    for port in range(5173, 5180):
        candidates.append(f"http://localhost:{port}")

    import urllib.request
    loop = asyncio.get_running_loop()

    async def probe(url: str) -> bool:
        def _do():
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    body = r.read(20000).decode("utf-8", errors="ignore")
                    return r.status, body
            except Exception:
                return None, ""
        st, body = await loop.run_in_executor(None, _do)
        if st == 200 and ("id=\"root\"" in body or "<title" in body):
            return True
        return False

    for u in candidates:
        ok = await probe(u)
        p(f"🔍 Frontend probe: {u} -> {'✅' if ok else '❌'}")
        if ok:
            p(f"✅ Frontend URL: {u}")
            return u.rstrip("/")

    raise RuntimeError("❌ Frontend URL bulunamadı")

# ----------------------------
# 3) DB BAĞLANTISI (OTOMATİK)
# ----------------------------
def get_db_config() -> Optional[Dict[str, Any]]:
    host = os.environ.get("DB_HOST") or os.environ.get("MYSQL_HOST")
    user = os.environ.get("DB_USER") or os.environ.get("MYSQL_USER")
    pwd = os.environ.get("DB_PASSWORD") or os.environ.get("MYSQL_PASSWORD") or ""
    name = os.environ.get("DB_NAME") or os.environ.get("MYSQL_DATABASE")
    port = int(os.environ.get("DB_PORT") or "3306")
    if not (host and user and name):
        p("⚠️ DB env eksik, DB eşleme pasif")
        return None
    return {
        "host": host,
        "user": user,
        "password": pwd,
        "database": name,
        "port": port,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }

def db_connect(cfg: Dict[str, Any]):
    return pymysql.connect(**cfg)

def normalize_s(x: str) -> str:
    return re.sub(r"\s+", " ", str(x).strip().lower())

def sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize_s(a), normalize_s(b)).ratio()

class SchemaCache:
    def __init__(self, conn):
        self.conn = conn
        self.schema = conn.db.decode() if isinstance(conn.db, bytes) else conn.db
        self.columns: List[Tuple[str, str, str]] = []
        self.columns_by_table: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        self.distinct_cache: Dict[Tuple[str, str], Set[str]] = {}
        self._load()

    def _load(self):
        p("📊 DB şema yükleniyor...")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE "
                    "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s",
                    (self.schema,)
                )
                rows = cur.fetchall()
                for r in rows:
                    t, c, dt = r["TABLE_NAME"], r["COLUMN_NAME"], r["DATA_TYPE"]
                    self.columns.append((t, c, dt))
                    self.columns_by_table[t].append((c, dt))
            p(f"✅ {len(self.columns_by_table)} tablo, {len(self.columns)} sütun")
        except Exception as e:
            p(f"❌ Şema yükleme hatası: {e}")

    def string_columns(self) -> List[Tuple[str, str, str]]:
        out = []
        for t, c, dt in self.columns:
            if dt in ("varchar", "text", "longtext", "mediumtext", "char"):
                out.append((t, c, dt))
        return out

    def sample_distinct(self, table: str, column: str, limit: int = 400) -> Set[str]:
        key = (table, column)
        if key in self.distinct_cache:
            return self.distinct_cache[key]
        vals: Set[str] = set()
        try:
            with self.conn.cursor() as cur:
                q = f"SELECT DISTINCT `{column}` AS v FROM `{table}` WHERE `{column}` IS NOT NULL LIMIT {limit}"
                cur.execute(q)
                rows = cur.fetchall()
                for r in rows:
                    v = r.get("v")
                    if v is None:
                        continue
                    s = normalize_s(v)
                    if s:
                        vals.add(s)
        except Exception:
            pass
        self.distinct_cache[key] = vals
        return vals

    def distinct_count(self, table: str, column: str) -> Optional[int]:
        try:
            with self.conn.cursor() as cur:
                q = f"SELECT COUNT(DISTINCT `{column}`) AS c FROM `{table}` WHERE `{column}` IS NOT NULL"
                cur.execute(q)
                row = cur.fetchone()
                return int(row["c"])
        except Exception:
            return None

def guess_single_column(schema: SchemaCache, values: List[str]) -> Tuple[Optional[str], Optional[str], float]:
    if not values:
        return None, None, 0.0
    vals_norm = [normalize_s(v) for v in values if v is not None]
    vals_set = set(vals_norm)
    best_t = best_c = None
    best_score = 0.0

    candidates = schema.string_columns()
    scored = []
    for t, c, dt in candidates:
        nm_score = max(sim(c, "name"), sim(c, "title"), sim(c, "city"), sim(c, "district"), sim(c, "service"))
        scored.append((nm_score, t, c))
    scored.sort(reverse=True)
    short = scored[:60] if len(scored) > 60 else scored

    for _, t, c in short:
        db_vals = schema.sample_distinct(t, c, limit=300)
        if not db_vals:
            continue
        overlap = len(vals_set & db_vals)
        score = overlap / max(1, len(vals_set))
        if score > best_score:
            best_score, best_t, best_c = score, t, c
    return best_t, best_c, best_score

# ----------------------------
# 4) KAYNAK DOSYA OTOMATİK TESPİTİ
# ----------------------------
class SourceIndex:
    def __init__(self, root: Path):
        self.root = root
        self.files: Dict[Path, str] = {}
        self._index()

    def _index(self):
        src = self.root / "src"
        if not src.exists():
            p("⚠️ src bulunamadı, kaynak tespiti pasif")
            return
        for dp, _, fns in os.walk(src):
            for fn in fns:
                if not fn.endswith((".ts", ".tsx", ".js", ".jsx", ".html", ".css")):
                    continue
                fp = Path(dp) / fn
                try:
                    self.files[fp] = fp.read_text("utf-8", errors="ignore")
                except Exception:
                    continue
        p(f"✅ {len(self.files)} kaynak dosya indexlendi")

    def find_files(self, needles: List[str], limit: int = 3) -> List[str]:
        if not needles:
            return []
        hits: List[Tuple[int, str]] = []
        for fp, txt in self.files.items():
            score = 0
            for n in needles:
                if n and n in txt:
                    score += 1
            if score:
                hits.append((score, str(fp)))
        hits.sort(reverse=True)
        return [h[1] for h in hits[:limit]]

SOURCE_INDEX = SourceIndex(ROOT)

# ----------------------------
# 5) UI-DB TEST SONUÇ VERİ YAPISI
# ----------------------------
@dataclass
class UiTestResult:
    talimat_no: int
    element_name: str
    element_type: str
    ui_samples: List[str]
    ui_count: int
    db_table: Optional[str]
    db_column: Optional[str]
    db_count: Optional[int]
    source_files: List[str]
    confidence: float
    success: bool
    error: Optional[str]

# ----------------------------
# 6) 3 KATMANLI DAYANIKLI TEST MOTORU
# ----------------------------
class ResilientUITester:
    def __init__(self, frontend_url: str, schema: Optional[SchemaCache]):
        self.frontend_url = frontend_url
        self.schema = schema
        self.json_bucket: deque = deque(maxlen=200)
        self.error_log: List[Dict] = []
        self.success_count = 0
        self.test_count = 0

    async def collect_json_responses(self, page):
        """L1: Global - Network response collector"""
        async def on_response(resp):
            try:
                ct = (resp.headers.get("content-type") or "").lower()
                if "application/json" in ct:
                    data = await resp.json()
                    self.json_bucket.append((time.time(), resp.url, resp.status, data))
            except Exception as e:
                self.log_error("NETWORK_RESPONSE", str(e), resp.url)
        page.on("response", lambda r: asyncio.create_task(on_response(r)))

    def log_error(self, stage: str, error: str, context: str = ""):
        """L3: Record - Error logging with deduplication"""
        error_key = f"{stage}:{error[:50]}"
        if error_key not in [e["key"] for e in self.error_log]:
            self.error_log.append({
                "timestamp": time.time(),
                "stage": stage,
                "error": error,
                "context": context,
                "key": error_key
            })
            p(f"❌ [{stage}] {error}")

    def pick_latest_json(self, since_ts: float) -> Optional[Tuple[str, int, Any]]:
        """L2: Operational - JSON response picker"""
        for ts, url, st, data in reversed(self.json_bucket):
            if ts >= since_ts:
                return url, st, data
        return None

    def prettify_samples(self, arr: List[str], max_n: int = 5) -> Tuple[List[str], int]:
        """L3: Record - Sample formatter"""
        xs = sorted({str(x).strip() for x in arr if str(x).strip()}, key=lambda x: normalize_s(x))
        return xs[:max_n], len(xs)

    async def test_element(self, talimat_no: int, element_name: str, element_type: str,
                          selector: str, test_action=None) -> UiTestResult:
        """L1: Global - Main test wrapper"""
        self.test_count += 1

        try:
            # L2: Operational - Playwright interaction
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                ctx = await browser.new_context()
                page = await ctx.new_page()
                await self.collect_json_responses(page)

                # Navigate to page
                await page.goto(self.frontend_url, wait_until="domcontentloaded", timeout=20000)

                # React component'lerinin yüklenmesini bekle
                p(f"⏳ React component'leri yükleniyor...")
                await page.wait_for_timeout(5000)  # 5 saniye bekle

                # SearchPage'a yönlendir
                try:
                    await page.goto(f"{self.frontend_url}/search", wait_until="domcontentloaded", timeout=20000)
                    await page.wait_for_timeout(3000)
                    p(f"✅ SearchPage'a yönlendirildi")
                except Exception as e:
                    p(f"⚠️ SearchPage yönlendirme hatası: {e}")

                # Find element
                since = time.time()
                element = None
                try:
                    element = await page.query_selector(selector)
                    if not element:
                        raise Exception(f"Element bulunamadı: {selector}")
                except Exception as e:
                    self.log_error("ELEMENT_FIND", str(e), selector)
                    return UiTestResult(
                        talimat_no=talimat_no,
                        element_name=element_name,
                        element_type=element_type,
                        ui_samples=[],
                        ui_count=0,
                        db_table=None,
                        db_column=None,
                        db_count=None,
                        source_files=[],
                        confidence=0.0,
                        success=False,
                        error=f"Element bulunamadı: {e}"
                    )

                # Test action
                if test_action:
                    try:
                        await test_action(element, page)
                    except Exception as e:
                        self.log_error("TEST_ACTION", str(e), selector)

                await page.wait_for_timeout(1000)

                # Collect UI data
                ui_data = []
                try:
                    if element_type == "SELECT":
                        options = await element.query_selector_all("option")
                        for opt in options[:10]:  # Limit to prevent overload
                            try:
                                text = (await opt.inner_text()) or ""
                                ui_data.append(text.strip())
                            except Exception:
                                continue
                    elif element_type == "FIRM_LIST":
                        cards = await page.query_selector_all(".firm-card, .card, [data-firm-card]")
                        for card in cards[:10]:
                            try:
                                text = (await card.inner_text()) or ""
                                ui_data.append(text.strip().split("\n")[0].strip())
                            except Exception:
                                continue
                    elif element_type == "BUTTON":
                        try:
                            text = (await element.inner_text()) or ""
                            ui_data.append(text.strip())
                        except Exception:
                            pass
                except Exception as e:
                    self.log_error("UI_DATA_COLLECTION", str(e), selector)

                samples, total_ui = self.prettify_samples(ui_data, max_n=5)

                # Get latest JSON response
                latest = self.pick_latest_json(since)
                req_url = ""
                status = 0
                data = None
                if latest:
                    req_url, status, data = latest

                # DB Analysis
                db_table = db_column = None
                db_count = None
                confidence = 0.0

                if self.schema and data:
                    try:
                        if isinstance(data, list) and data and isinstance(data[0], str):
                            db_table, db_column, confidence = guess_single_column(self.schema, data[:200])
                            if db_table and db_column:
                                db_count = self.schema.distinct_count(db_table, db_column)
                        elif isinstance(data, list) and data and isinstance(data[0], dict):
                            # For complex data, analyze keys
                            keys = list(data[0].keys())
                            for key in keys[:5]:  # Analyze first 5 keys
                                sample_vals = [str(item.get(key, "")) for item in data[:100]]
                                t, c, conf = guess_single_column(self.schema, sample_vals)
                                if conf > confidence:
                                    db_table, db_column, confidence = t, c, conf
                            if db_table and db_column:
                                db_count = self.schema.distinct_count(db_table, db_column)
                    except Exception as e:
                        self.log_error("DB_ANALYSIS", str(e), req_url)

                # Source file detection
                source_files = SOURCE_INDEX.find_files(samples, limit=3)

                # Success criteria
                success = (total_ui > 0) and (
                    db_count is None or
                    abs(db_count - total_ui) <= max(3, int(db_count * 0.1))
                )

                if success:
                    self.success_count += 1

                await ctx.close()
                await browser.close()

                return UiTestResult(
                    talimat_no=talimat_no,
                    element_name=element_name,
                    element_type=element_type,
                    ui_samples=samples,
                    ui_count=total_ui,
                    db_table=db_table,
                    db_column=db_column,
                    db_count=db_count,
                    source_files=source_files,
                    confidence=confidence,
                    success=success,
                    error=None
                )

        except Exception as e:
            self.log_error("GLOBAL_TEST", str(e), f"Talimat {talimat_no}")
            return UiTestResult(
                talimat_no=talimat_no,
                element_name=element_name,
                element_type=element_type,
                ui_samples=[],
                ui_count=0,
                db_table=None,
                db_column=None,
                db_count=None,
                source_files=[],
                confidence=0.0,
                success=False,
                error=str(e)
            )

    def print_result(self, result: UiTestResult):
        """L2: Operational - Result formatter"""
        status = "✅ BAŞARILI" if result.success else "❌ BAŞARISIZ"
        p(f"\n🔍 TALİMAT NO : {result.talimat_no}")
        p(f"📋 ARAYÜZ ÖĞESİ ADI : {result.element_name}")
        p(f"🏷️  ARAYÜZ ÖĞESİ TÜRÜ : {result.element_type}")

        p(f"🎯 İLK 5 SONUÇ AŞAĞIDAKİ GİBİDİR")
        for i, sample in enumerate(result.ui_samples, 1):
            p(f"   {i}. {sample}")

        if result.ui_count > len(result.ui_samples):
            remaining = result.ui_count - len(result.ui_samples)
            p(f"   ... ve {remaining} sonuç daha (alfabeye göre)")

        p(f"📊 ARAYÜZDE TOPLAM DEĞER SAYISI : {result.ui_count}")

        if result.db_table and result.db_column:
            p(f"🗄️  DB DE İLGİLİ TABLO : {result.db_table}")
            p(f"📝 DB DE İLGİLİ SÜTUN : {result.db_column}")
            if result.db_count is not None:
                p(f"🔢 DB DEN GELEN TOPLAM İL SAYISI : {result.db_count}")

        if result.source_files:
            p(f"📂 ARAYÜZ ÖĞESİNİN BULUNDUĞU DOSYA : {result.source_files[0] if result.source_files else 'OTOMATİK TESPİT EDİLEMEDİ'}")

        p(f"🎯 GÜVEN SKORU : %{result.confidence * 100:.1f}")
        p(f"📈 DURUM : {status}")

        if result.error:
            p(f"❌ HATA : {result.error}")

    async def discover_elements(self, page):
        """Sayfadaki tüm elementleri otomatik keşfet"""
        p("🔍 ELEMENT KEŞİFİ BAŞLATILIYOR...")

        # Tüm select elementleri
        selects = await page.query_selector_all("select")
        p(f"📋 SELECT ELEMENTS: {len(selects)} adet")
        for i, sel in enumerate(selects[:5]):
            try:
                id_attr = await sel.get_attribute("id") or ""
                name_attr = await sel.get_attribute("name") or ""
                class_attr = await sel.get_attribute("class") or ""
                p(f"   {i+1}. ID='{id_attr}' NAME='{name_attr}' CLASS='{class_attr[:50]}'")
            except Exception:
                pass

        # Tüm input elementleri
        inputs = await page.query_selector_all("input")
        p(f"📝 INPUT ELEMENTS: {len(inputs)} adet")
        for i, inp in enumerate(inputs[:5]):
            try:
                type_attr = await inp.get_attribute("type") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                class_attr = await inp.get_attribute("class") or ""
                p(f"   {i+1}. TYPE='{type_attr}' PLACEHOLDER='{placeholder}' CLASS='{class_attr[:50]}'")
            except Exception:
                pass

        # Tüm button elementleri
        buttons = await page.query_selector_all("button")
        p(f"🔘 BUTTON ELEMENTS: {len(buttons)} adet")
        for i, btn in enumerate(buttons[:5]):
            try:
                class_attr = await btn.get_attribute("class") or ""
                text = await btn.inner_text() or ""
                p(f"   {i+1}. TEXT='{text[:30]}' CLASS='{class_attr[:50]}'")
            except Exception:
                pass

        # Grid/Div elementleri
        divs = await page.query_selector_all(".grid > div, .flex > div, [class*='grid'] > div")
        p(f"📦 GRID/DIV ELEMENTS: {len(divs)} adet")
        for i, div in enumerate(divs[:3]):
            try:
                class_attr = await div.get_attribute("class") or ""
                text = await div.inner_text() or ""
                p(f"   {i+1}. TEXT='{text[:30]}' CLASS='{class_attr[:50]}'")
            except Exception:
                pass

    async def run_all_tests(self):
        """L1: Global - Complete test suite"""
        p("🚀 UI-DB İZLE TEST SUİTİ BAŞLATILIYOR...")
        p("=" * 80)

        # Test configurations - GERÇEK SearchPage SELECTOR'LARI
        tests = [
            (1, "İLLER AÇILİR PENCERESİ", "SELECT", "select", lambda el, page: el.click()),
            (2, "HİZMETLER AÇILİR PENCERESİ", "SELECT", "select", lambda el, page: el.click()),
            (3, "İLÇELER AÇILİR PENCERESİ", "SELECT", "select", lambda el, page: el.click()),
            (4, "FİRMALAR LİSTESİ", "FIRM_LIST", ".grid > div, .flex > div, [class*='grid'] > div", None),
            (5, "FİRMA DETAYLARI", "FIRM_DETAIL", ".grid > div, .flex > div, [class*='grid'] > div", lambda el, page: el.click()),
            (6, "KONUMUMU KULLAN", "BUTTON", "button, .text-gray-600, [class*='location']", lambda el, page: el.click()),
            (7, "ARAMA KUTUSU", "INPUT", "input[type='text'], input[placeholder*='Firma']", lambda el, page: el.fill("test")),
            (8, "FİLTRELEME BUTONU", "BUTTON", "button, [class*='filter'], .filter-btn", lambda el, page: el.click()),
            (9, "SIRALAMA DROWDOWN", "SELECT", "select, [role='combobox'], [class*='sort']", lambda el, page: el.click()),
            (10, "SAYFALAMA", "PAGINATION", ".pagination, .page-nav, [class*='page']", None),
            (11, "HARİTA GÖRÜNÜMÜ", "MAP", ".map, #map, [class*='map'], .leaflet-container", None),
            (12, "İLETİŞİM BUTONU", "BUTTON", "button, [class*='contact'], [class*='whatsapp']", lambda el, page: el.click()),
        ]

        # Run tests with resilience
        for talimat_no, name, element_type, selector, action in tests:
            try:
                p(f"\n🔍 TEST EDİLİYOR: {name}")
                result = await self.test_element(talimat_no, name, element_type, selector, action)
                self.print_result(result)

                # Small delay between tests
                await asyncio.sleep(1)

            except Exception as e:
                self.log_error("TEST_EXECUTION", str(e), f"Talimat {talimat_no}")

        # Final summary
        p("\n" + "=" * 80)
        p("📊 TEST ÖZETİ")
        p(f"✅ BAŞARILI TEST : {self.success_count}/{self.test_count}")
        p(f"❌ BAŞARISIZ TEST : {self.test_count - self.success_count}/{self.test_count}")
        p(f"📈 BAŞARI ORANI : %{(self.success_count / max(1, self.test_count)) * 100:.1f}")

        if self.error_log:
            p(f"\n⚠️ TOPLAM HATA : {len(self.error_log)}")
            for error in self.error_log[:5]:  # Show first 5 errors
                p(f"   ❌ {error['stage']}: {error['error']}")

        p("=" * 80)

# ----------------------------
# 7) ANA ÇALIŞTIRMA FONKSİYONU
# ----------------------------
async def main():
    """L1: Global - Main execution wrapper"""
    try:
        p("🚀 UI-DB İZLE SİSTEMİ BAŞLATILIYOR...")
        load_env()

        # Detect frontend URL
        frontend_url = await detect_frontend_url()

        # Connect to database
        schema = None
        cfg = get_db_config()
        if cfg:
            try:
                conn = db_connect(cfg)
                schema = SchemaCache(conn)
                p("✅ DB bağlantısı başarılı")
            except Exception as e:
                p(f"⚠️ DB bağlantı hatası: {e}")
                schema = None
        else:
            p("⚠️ DB konfigürasyonu bulunamadı")

        # Create tester and run tests
        tester = ResilientUITester(frontend_url, schema)
        await tester.run_all_tests()

    except Exception as e:
        p(f"❌ KRİTİK HATA: {e}")
        p(traceback.format_exc())
    finally:
        p("🏁 UI-DB İZLE SİSTEMİ TAMAMLANDI")

if __name__ == "__main__":
    asyncio.run(main())
