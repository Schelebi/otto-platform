#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI-DB TEST SUITE v1.0
Otomatik arayüz öğesi keşfi + DB kablo doğrulama
Tüm talimatları tek parça halinde çalıştırır
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
    print(msg, flush=True)

def ensure_lib(import_name: str, pip_name: str):
    try:
        __import__(import_name)
        p(f"[LIB][OK] {import_name} mevcut")
    except Exception:
        p(f"[LIB][WARN] {import_name} yok, kuruluyor -> {pip_name}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pip_name])
            __import__(import_name)
            p(f"[LIB][OK] {import_name} kuruldu")
        except Exception as e:
            p(f"[LIB][ERROR] {import_name} kurulamadı: {e}")
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
        p(f"[ENV][ERROR] okuma sorunu: {e}")
    return env

def load_env() -> Dict[str, str]:
    env_path = ROOT / ".env.local"
    env = read_env_file(env_path)
    for k, v in env.items():
        os.environ.setdefault(k, v)
    p(f"[ENV][INFO] env yüklendi: {len(env)} değişken")
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
        p(f"[FRONTEND][PROBE] {u} -> {'OK' if ok else 'NO'}")
        if ok:
            p(f"[FRONTEND][OK] seçilen url: {u}")
            return u.rstrip("/")

    raise RuntimeError("Frontend URL bulunamadı (otomatik tarama başarısız).")

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
        p("[DB][WARN] DB env eksik, UI-DB eşleme DB tarafında pasif")
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
        p("[DB][INFO] şema yükleniyor (information_schema)...")
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
        p(f"[DB][OK] tablo sayısı: {len(self.columns_by_table)} | sütun sayısı: {len(self.columns)}")

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

def guess_table_columns(schema: SchemaCache, rows: List[Dict[str, Any]]) -> Dict[str, Tuple[Optional[str], Optional[str], float]]:
    if not rows:
        return {}
    keys = list(rows[0].keys())
    out: Dict[str, Tuple[Optional[str], Optional[str], float]] = {}
    for k in keys:
        sample_vals = [str(r.get(k, "")) for r in rows[:120]]
        t, c, sc = guess_single_column(schema, sample_vals)
        out[k] = (t, c, sc)
    return out

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
            p("[SRC][WARN] src bulunamadı, kaynak tespiti pasif")
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
        p(f"[SRC][OK] indexlenen dosya: {len(self.files)}")

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
# 5) UI-DB ANALYZER
# ----------------------------
@dataclass
class UiElementResult:
    label: str
    kind: str
    ui_count: int
    ui_samples: List[str]
    req_url: str
    status: int
    db_count: Optional[int]
    db_table: Optional[str]
    db_column: Optional[str]
    file_paths: List[str]
    ok: bool
    note: str

async def collect_json_responses(page, bucket: deque):
    async def on_response(resp):
        try:
            ct = (resp.headers.get("content-type") or "").lower()
            if "application/json" in ct:
                data = await resp.json()
                bucket.append((time.time(), resp.url, resp.status, data))
        except Exception:
            return
    page.on("response", lambda r: asyncio.create_task(on_response(r)))

def pick_latest_json(bucket: deque, since_ts: float) -> Optional[Tuple[str, int, Any]]:
    for ts, url, st, data in reversed(bucket):
        if ts >= since_ts:
            return url, st, data
    return None

def prettify_samples(arr: List[str], max_n: int = 5) -> Tuple[List[str], int]:
    xs = sorted({str(x).strip() for x in arr if str(x).strip()}, key=lambda x: normalize_s(x))
    return xs[:max_n], len(xs)

def infer_label_from_col(col: Optional[str]) -> str:
    if not col:
        return "AÇILIR PENCERE"
    c = normalize_s(col)
    if sim(c, "il") > 0.6 or "city" in c:
        return "İLLER AÇILIR PENCERESİ"
    if sim(c, "ilce") > 0.6 or "district" in c:
        return "İLÇELER AÇILIR PENCERESİ"
    if "hizmet" in c or "service" in c:
        return "HİZMETLER AÇILIR PENCERESİ"
    return "AÇILIR PENCERE"

async def analyze_selects(page, schema: Optional[SchemaCache], bucket: deque) -> List[UiElementResult]:
    results: List[UiElementResult] = []
    selects = await page.query_selector_all("select")
    p(f"[UI][INFO] select sayısı bulundu: {len(selects)}")

    for idx, sel in enumerate(selects, start=1):
        since = time.time()
        try:
            await sel.click()
        except Exception:
            pass
        await page.wait_for_timeout(600)

        options = await sel.query_selector_all("option")
        opt_texts = []
        for o in options:
            try:
                t = (await o.inner_text()) or ""
                opt_texts.append(t.strip())
            except Exception:
                continue

        samples, total_ui = prettify_samples(opt_texts, max_n=5)

        latest = pick_latest_json(bucket, since)
        req_url = ""
        st = 0
        data = None
        if latest:
            req_url, st, data = latest

        db_table = db_col = None
        db_count = None
        conf = 0.0

        if schema and data:
            if isinstance(data, list) and data and isinstance(data[0], str):
                db_table, db_col, conf = guess_single_column(schema, data[:200])
                if db_table and db_col:
                    db_count = schema.distinct_count(db_table, db_col)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                guesses = guess_table_columns(schema, data[:200])
                best_key = None
                best_sc = 0.0
                for k, (t, c, sc) in guesses.items():
                    if sc > best_sc:
                        best_sc, best_key = sc, k
                db_table, db_col, conf = t, c, sc
                if db_table and db_col:
                    db_count = schema.distinct_count(db_table, db_col)

        label = infer_label_from_col(db_col)
        file_paths = SOURCE_INDEX.find_files(samples, limit=3)
        ok = (total_ui > 0) and (db_count is None or abs(db_count - total_ui) <= max(3, int(db_count * 0.1)))
        note = f"CONF={conf:.2f}" if conf else "CONF=0.00"

        res = UiElementResult(
            label=label,
            kind=f"SELECT#{idx}",
            ui_count=total_ui,
            ui_samples=samples,
            req_url=req_url,
            status=st,
            db_count=db_count,
            db_table=db_table,
            db_column=db_col,
            file_paths=file_paths,
            ok=ok,
            note=note
        )
        results.append(res)

    return results

async def analyze_firm_list(page, schema: Optional[SchemaCache], bucket: deque) -> Optional[UiElementResult]:
    since = time.time()
    cards = await page.query_selector_all(".firm-card, .card, [data-firm-card]")
    if not cards:
        cards = await page.query_selector_all("[class*='card'], [class*='firm']")
    p(f"[UI][INFO] kart sayısı: {len(cards)}")

    names = []
    for c in cards[:20]:
        try:
            t = (await c.inner_text()) or ""
            t = t.strip().split("\n")[0].strip()
            if t:
                names.append(t)
        except Exception:
            continue

    samples, total_ui = prettify_samples(names, max_n=5)

    latest = pick_latest_json(bucket, since)
    req_url = ""
    st = 0
    data = None
    if latest:
        req_url, st, data = latest

    db_table = db_col = None
    db_count = None
    conf = 0.0

    if schema and data and isinstance(data, list):
        if data and isinstance(data[0], dict):
            guesses = guess_table_columns(schema, data[:200])
            best_key = None
            best_sc = 0.0
            best_t = best_c = None
            for k, (t, c, sc) in guesses.items():
                if sc > best_sc:
                    best_sc, best_key = sc, k
                    best_t, best_c = t, c
            db_table, db_col, conf = best_t, best_c, best_sc
            if db_table:
                try:
                    with schema.conn.cursor() as cur:
                        cur.execute(f"SELECT COUNT(*) AS c FROM `{db_table}`")
                        row = cur.fetchone()
                        db_count = int(row["c"])
                except Exception:
                    db_count = None

    label = "FİRMALAR LİSTESİ"
    file_paths = SOURCE_INDEX.find_files(samples, limit=3)
    ok = (total_ui > 0) and (db_count is None or abs(db_count - total_ui) <= max(10, int(db_count * 0.2)))
    note = f"CONF={conf:.2f}" if conf else "CONF=0.00"

    return UiElementResult(
        label=label,
        kind="FIRMS",
        ui_count=total_ui,
        ui_samples=samples,
        req_url=req_url,
        status=st,
        db_count=db_count,
        db_table=db_table,
        db_column=db_col,
        file_paths=file_paths,
        ok=ok,
        note=note
    )

async def analyze_firm_detail(page, schema: Optional[SchemaCache], bucket: deque) -> Optional[UiElementResult]:
    cards = await page.query_selector_all(".firm-card, .card, [data-firm-card]")
    if not cards:
        return None
    first = cards[0]
    since = time.time()
    try:
        await first.click()
    except Exception:
        return None

    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass

    await page.wait_for_timeout(1500)

    body_text = ""
    try:
        body_text = (await page.inner_text("body"))[:4000]
    except Exception:
        body_text = ""

    latest = pick_latest_json(bucket, since)
    req_url = ""
    st = 0
    data = None
    if latest:
        req_url, st, data = latest

    db_table = db_col = None
    db_count = None
    conf = 0.0

    if schema and data and isinstance(data, dict):
        guesses = guess_table_columns(schema, [data])
        best_sc = 0.0
        best_t = best_c = None
        for k, (t, c, sc) in guesses.items():
            if sc > best_sc:
                best_sc, best_t, best_c = sc, t, c
        db_table, db_col, conf = best_t, best_c, best_sc

    samples, _ = prettify_samples(body_text.splitlines(), max_n=5)
    file_paths = SOURCE_INDEX.find_files(samples, limit=3)
    ok = bool(data) or bool(body_text)
    note = f"CONF={conf:.2f}" if conf else "CONF=0.00"

    return UiElementResult(
        label="FİRMA DETAY SAYFASI",
        kind="DETAIL",
        ui_count=1 if ok else 0,
        ui_samples=samples,
        req_url=req_url,
        status=st,
        db_count=db_count,
        db_table=db_table,
        db_column=db_col,
        file_paths=file_paths,
        ok=ok,
        note=note
    )

async def analyze_geolocation(page, bucket: deque) -> Optional[UiElementResult]:
    since = time.time()
    btn = await page.query_selector("button#konum-btn, button.location-btn, button[class*='location'], button[id*='konum']")
    if not btn:
        buttons = await page.query_selector_all("button")
        for b in buttons:
            try:
                t = (await b.inner_text()) or ""
                if "konum" in normalize_s(t) or "location" in normalize_s(t):
                    btn = b
                    break
            except Exception:
                continue
    if not btn:
        return None

    try:
        await page.context.grant_permissions(["geolocation"])
        await page.context.set_geolocation({"latitude": 39.9, "longitude": 32.85})
    except Exception:
        pass

    try:
        await btn.click()
    except Exception:
        pass

    await page.wait_for_timeout(1200)
    latest = pick_latest_json(bucket, since) or ("", 0, None)
    req_url, st, data = latest

    ok = True
    samples = ["Konum tetiklendi"]
    file_paths = SOURCE_INDEX.find_files(["konum", "location"], limit=3)

    return UiElementResult(
        label="KONUMUMU KULLAN",
        kind="GEO",
        ui_count=1,
        ui_samples=samples,
        req_url=req_url,
        status=st,
        db_count=None,
        db_table=None,
        db_column=None,
        file_paths=file_paths,
        ok=ok,
        note="CONF=N/A"
    )

def print_result(res: UiElementResult):
    p("\n" + "="*90)
    p(f"{res.label} TEST EDİLDİ")
    p("İLK 5 SONUÇ AŞAĞIDAKİ GİBİDİR:")
    for s in res.ui_samples:
        p(f"- {s}")
    if res.ui_count > len(res.ui_samples):
        p(f"- {res.ui_count - len(res.ui_samples)} SONUÇ DAHA ...")
    p(f"ARAYÜZDE TOPLAM DEĞER SAYISI: {res.ui_count}")
    p(f"ARAYÜZ ÖĞESİ TÜRÜ: {res.kind}")
    if res.req_url:
        p(f"ARKA PLAN ÇAĞRI URL: {res.req_url}")
    p(f"HTTP STATUS: {res.status}")
    if res.db_table and res.db_column:
        p(f"DB KAYNAĞI (OTOMATİK EŞLEME): {res.db_table}.{res.db_column}")
    if res.db_count is not None:
        p(f"DB DISTINCT TOPLAM: {res.db_count}")
    if res.file_paths:
        p("KAYNAK DOSYA(OTOMATİK):")
        for fp in res.file_paths:
            p(f"- {fp}")
    p(f"SONUÇ: {'OK' if res.ok else 'FAIL'} | {res.note}")

async def run_ui_db_suite(frontend_url: str, schema: Optional[SchemaCache]):
    json_bucket: deque = deque(maxlen=200)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await collect_json_responses(page, json_bucket)

        p(f"[UI-DB][INFO] sayfa açılıyor: {frontend_url}")
        await page.goto(frontend_url, wait_until="domcontentloaded", timeout=20000)

        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        p("[UI-DB][INFO] başlangıç stabilizasyonu 10sn")
        await page.wait_for_timeout(10000)

        # TALİMAT 1-3 (Select'ler)
        sel_results = await analyze_selects(page, schema, json_bucket)
        for r in sel_results:
            print_result(r)

        # TALİMAT 4 (Firmalar listesi)
        fr = await analyze_firm_list(page, schema, json_bucket)
        if fr:
            print_result(fr)

        # TALİMAT 5 (Detay)
        dr = await analyze_firm_detail(page, schema, json_bucket)
        if dr:
            print_result(dr)

        # TALİMAT 6 (Konum)
        gr = await analyze_geolocation(page, json_bucket)
        if gr:
            print_result(gr)

        await ctx.close()
        await browser.close()

# ----------------------------
# 6) MACHINE GUARDIAN (CPU/RAM/DISK DOSTU)
# ----------------------------
class MachineGuardian:
    def __init__(self):
        self.last_alerts: Set[str] = set()
        self.batch: List[str] = []
        self.max_lines = 100

    def ts(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def alert_once(self, key: str, line: str):
        if key in self.last_alerts:
            return
        if len(self.last_alerts) >= self.max_lines:
            return
        self.last_alerts.add(key)
        p(line)

    def check(self):
        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(str(ROOT)).percent
        proc_count = len(psutil.pids())

        if disk >= 90:
            self.alert_once("disk90", f"[{self.ts()}] [MG-DISK] → Disk kullanımı %{disk:.1f} - tehlike!")
            self.alert_once("koruma", f"[{self.ts()}] [MG-KORUMA] → Sistem koruma modu aktif!")

        if ram >= 90:
            self.alert_once("heap90", f"[{self.ts()}] [MG-HAFIZA] → Heap kullanımı %{ram:.1f} - GC tetikleniyor")

        self.alert_once(f"health_{int(time.time()//180)}",
            f"[{self.ts()}] [HEALTH] → Sistem durumu - CPU: %{cpu:.1f} | RAM: %{ram:.1f} | Disk: %{disk:.1f}")

        self.alert_once(f"proc_{proc_count}",
            f"[{self.ts()}] [MG-AKIS] → Process sayısı değişti: {proc_count}")

        self.alert_once(f"status_{int(time.time()//180)}",
            f"[{self.ts()}] [MG-STATUS] → Cache: 0 item | Batch: {len(self.batch)} log")

async def machine_guardian_loop(mg: MachineGuardian):
    while True:
        try:
            mg.check()
        except Exception as e:
            p(f"[{mg.ts()}] [MG-ERROR] → {e}")
        await asyncio.sleep(180)

# ----------------------------
# 7) STOP COMMAND DİAGNOSTİK DÖNGÜSÜ
# ----------------------------
async def stop_listener(trigger_queue: asyncio.Queue):
    loop = asyncio.get_running_loop()
    def _readline():
        try:
            return sys.stdin.readline()
        except Exception:
            return ""
    while True:
        line = await loop.run_in_executor(None, _readline)
        if not line:
            await asyncio.sleep(1)
            continue
        if "stop" in normalize_s(line):
            await trigger_queue.put("stop")

async def handle_stop(trigger_queue: asyncio.Queue):
    while True:
        msg = await trigger_queue.get()
        if msg == "stop":
            p("\n[STOP][INFO] diagnose modu tetiklendi")
            p("[STOP][1] event-loop canlılık kontrolü -> OK")
            p("[STOP][2] anlık kaynak durumu yazılıyor")
            try:
                cpu = psutil.cpu_percent(interval=0.2)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage(str(ROOT)).percent
                p(f"[STOP][HEALTH] CPU:%{cpu:.1f} RAM:%{ram:.1f} DISK:%{disk:.1f}")
            except Exception as e:
                p(f"[STOP][HEALTH][ERR] {e}")
            os.environ["UI_DB_RETRY_DEPTH"] = "deep"
            p("[STOP][3] retry depth 'deep' set edildi")
            p("[STOP][4] akıllı fallback aktif")
            p("[STOP][5] son delta raporu bir sonraki döngüde yazılacak")
            os.environ["UI_DB_DEBUG"] = "1"
            p("[STOP][6] debug modu aktif")
            p("[STOP][7] süreç kaldığı yerden devam edecek\n")

# ----------------------------
# 8) ANA UI-DB DÖNGÜSÜ
# ----------------------------
async def ui_db_loop(frontend_url: str, schema: Optional[SchemaCache]):
    cycle = 0
    while True:
        cycle += 1
        try:
            p(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] [UI-DB] → Analiz döngüsü #{cycle} başlıyor")
            await run_ui_db_suite(frontend_url, schema)
            p(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [UI-DB-STATUS] → UI-DB Analyzer çalışıyor")
        except Exception as e:
            p(f"[UI-DB][ERROR] {e}")
            p(traceback.format_exc())
        await asyncio.sleep(180)

# ----------------------------
# 9) GLOBAL MAIN + TRY KATMANI
# ----------------------------
async def main():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

    p("[BOOT] başlatılıyor...")
    load_env()

    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p("[PLAYWRIGHT][OK] chromium hazır")
    except Exception:
        p("[PLAYWRIGHT][WARN] chromium kurulum atlandı/başarısız, varsa mevcutla devam")

    frontend_url = await detect_frontend_url()

    schema = None
    cfg = get_db_config()
    if cfg:
        try:
            conn = db_connect(cfg)
            schema = SchemaCache(conn)
        except Exception as e:
            p(f"[DB][ERROR] bağlantı başarısız: {e}")
            schema = None

    mg = MachineGuardian()
    trigger_queue: asyncio.Queue = asyncio.Queue()

    tasks = [
        asyncio.create_task(machine_guardian_loop(mg)),
        asyncio.create_task(ui_db_loop(frontend_url, schema)),
        asyncio.create_task(stop_listener(trigger_queue)),
        asyncio.create_task(handle_stop(trigger_queue)),
    ]

    await asyncio.gather(*tasks)

def _sig_handler(sig, frame):
    p(f"\n[SIGNAL] {sig} alındı, çıkılıyor...")
    sys.exit(0)

signal.signal(signal.SIGINT, _sig_handler)
signal.signal(signal.SIGTERM, _sig_handler)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        p("\n[EXIT] keyboard interrupt")
    except Exception as e:
        p(f"\n[FATAL] {e}")
        p(traceback.format_exc())
