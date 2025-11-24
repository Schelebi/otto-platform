import asyncio
import json
import os
import time
import gzip
from collections import deque
from pathlib import Path
from playwright.async_api import async_playwright, Error as PWError

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
MAX_LOG_BYTES = 2 * 1024 * 1024  # 2MB

class LogRing:
    def __init__(self, maxlen=2000):
        self.buf = deque(maxlen=maxlen)
        self.last_emit = {}  # key -> ts

    def add(self, item):
        self.buf.append(item)

    def throttle_ok(self, key, ms=1000):
        now = time.time() * 1000
        last = self.last_emit.get(key, 0)
        if now - last >= ms:
            self.last_emit[key] = now
            return True
        return False

class DiskLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pending = []
        self.lock = asyncio.Lock()

    async def write(self, obj):
        async with self.lock:
            self.pending.append(obj)

    async def flush(self):
        async with self.lock:
            if not self.pending:
                return
            data = self.pending
            self.pending = []
        self._rotate_if_needed()
        with open(self.file_path, "a", encoding="utf-8") as f:
            for o in data:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")

    def _rotate_if_needed(self):
        if self.file_path.exists() and self.file_path.stat().st_size > MAX_LOG_BYTES:
            ts = time.strftime("%Y%m%d_%H%M%S")
            rotated = self.file_path.with_suffix(f".{ts}.log")
            self.file_path.rename(rotated)
            gz_path = rotated.with_suffix(rotated.suffix + ".gz")
            with open(rotated, "rb") as r, gzip.open(gz_path, "wb") as w:
                w.write(r.read())
            try:
                rotated.unlink(missing_ok=True)
            except Exception:
                pass

def classify_console(msg_text, msg_type):
    t = msg_text.lower()
    if "cors policy" in t:
        return "CORS.BLOCK", "WARN"
    if "failed to load source map" in t:
        return "SOURCEMAP.MISS", "WARN"
    if "unknown property" in t or "css" in t and "warning" in t:
        return "CSS.WARNING", "WARN"
    if "mixed content" in t or "unauthenticated" in t:
        return "SECURITY.MIXED", "ERROR"
    if "forced reflow" in t or "long task" in t:
        return "PERFORMANCE.LAG", "WARN"
    if "heap out of memory" in t:
        return "MEMORY.LEAK", "ERROR"
    if msg_type == "error":
        return "JS.RUNTIME", "ERROR"
    if msg_type == "warning":
        return "JS.WARNING", "WARN"
    return "CONSOLE.INFO", "INFO"

def classify_network(status):
    if status >= 500:
        return "API.FAIL", "ERROR"
    if status >= 400:
        return "API.WARN", "WARN"
    return "API.OK", "INFO"

async def flush_loop(dlog, stop_flag):
    try:
        while not stop_flag["stop"]:
            await dlog.flush()
            await asyncio.sleep(1.0)
    except Exception:
        pass

async def enable_watch_for(ms, state):
    state["watch_until"] = time.time() + (ms / 1000.0)

def watch_active(state):
    return time.time() < state["watch_until"]

async def full_scenario(page, url):
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle")

async def run_once(url):
    ring = LogRing()
    d_console = DiskLogger(LOG_DIR / "error_console.log")
    d_net = DiskLogger(LOG_DIR / "network.log")
    stop_flag = {"stop": False}
    state = {"watch_until": 0.0}
    critical_found = {"yes": False}

    try:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()

                # L2: Listener kurulumları
                try:
                    async def on_console(msg):
                        try:
                            mtype = msg.type
                            text = msg.text
                            cls, sev = classify_console(text, mtype)
                            item = {
                                "ts": time.time(),
                                "class": cls,
                                "sev": sev,
                                "type": mtype,
                                "text": text,
                                "url": page.url,
                            }
                            ring.add(item)
                            await d_console.write(item)

                            key = f"{cls}:{text[:60]}"
                            if sev == "ERROR":
                                critical_found["yes"] = True
                                if ring.throttle_ok(key):
                                    print(f"[CRIT][{cls}] {text[:160]}")
                            else:
                                if watch_active(state) and ring.throttle_ok(key):
                                    print(f"[WARN][{cls}] {text[:160]}")
                        except Exception:
                            pass  # L3 koruma
                    page.on("console", on_console)

                    async def on_page_error(err):
                        try:
                            text = str(err)
                            cls = "JS.EXCEPTION"
                            item = {
                                "ts": time.time(),
                                "class": cls,
                                "sev": "ERROR",
                                "text": text,
                                "url": page.url,
                            }
                            ring.add(item)
                            await d_console.write(item)
                            critical_found["yes"] = True
                            key = f"{cls}:{text[:60]}"
                            if ring.throttle_ok(key):
                                print(f"[CRIT][{cls}] {text[:160]}")
                        except Exception:
                            pass
                    page.on("pageerror", on_page_error)

                    async def on_request_failed(req):
                        try:
                            item = {
                                "ts": time.time(),
                                "class": "NETWORK.ERROR",
                                "sev": "ERROR",
                                "url": req.url,
                                "method": req.method,
                                "failure": req.failure,
                            }
                            ring.add(item)
                            await d_net.write(item)
                            critical_found["yes"] = True
                            key = f"REQFAIL:{req.url}"
                            if ring.throttle_ok(key):
                                print(f"[CRIT][NETWORK.ERROR] {req.url}")
                        except Exception:
                            pass
                    page.on("requestfailed", on_request_failed)

                    async def on_response(resp):
                        try:
                            status = resp.status
                            cls, sev = classify_network(status)
                            if status >= 400:
                                item = {
                                    "ts": time.time(),
                                    "class": cls,
                                    "sev": sev,
                                    "status": status,
                                    "url": resp.url,
                                    "method": resp.request.method,
                                }
                                ring.add(item)
                                await d_net.write(item)
                                key = f"{cls}:{status}:{resp.url}"
                                if sev == "ERROR":
                                    critical_found["yes"] = True
                                    if ring.throttle_ok(key):
                                        print(f"[CRIT][{cls}] {status} {resp.url}")
                                else:
                                    if watch_active(state) and ring.throttle_ok(key):
                                        print(f"[WARN][{cls}] {status} {resp.url}")
                        except Exception:
                            pass
                    page.on("response", on_response)

                    # Kullanıcı etkileşimi ile watch tetikleme
                    async def on_user_action(_):
                        try:
                            await enable_watch_for(2500, state)
                        except Exception:
                            pass
                    page.on("click", on_user_action)
                    page.on("keydown", on_user_action)

                except Exception as e:
                    ring.add({"class":"LISTENER.FAIL","sev":"ERROR","text":str(e)})

                # Disk flush task
                flush_task = asyncio.create_task(flush_loop(d_console, stop_flag))
                flush_task2 = asyncio.create_task(flush_loop(d_net, stop_flag))

                # Hızlı başlangıç taraması penceresi
                try:
                    await enable_watch_for(5000, state)  # 5 saniye hızlı tarama
                    await full_scenario(page, url)
                    await asyncio.sleep(2.0)  # tarama penceresi
                except PWError as e:
                    ring.add({"class":"SCENARIO.FAIL","sev":"ERROR","text":str(e)})
                    critical_found["yes"] = True

                # Başlangıç kritik hatası varsa otomatik akışı durdur, izlemeye geç
                if critical_found["yes"]:
                    print("[STOP] Başlangıç kritik hataları bulundu, etkileşim izleme moduna geçildi.")

                # İzleme modu: kullanıcı kapatana kadar düşük kaynakla bekle
                try:
                    while True:
                        await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    pass
                finally:
                    stop_flag["stop"] = True
                    await d_console.flush()
                    await d_net.flush()
                    flush_task.cancel()
                    flush_task2.cancel()
                    await context.close()
                    await browser.close()

            except Exception as e:
                ring.add({"class":"BROWSER.FAIL","sev":"ERROR","text":str(e)})

    except Exception as e:
        ring.add({"class":"GLOBAL.FAIL","sev":"ERROR","text":str(e)})

async def main(url):
    # FULL PROTOKOL: 10 tekrar, 10/10 değilse döngü devam
    success = 0
    run_no = 0
    while success < 10:
        run_no += 1
        try:
            await run_once(url)
            success += 1
        except Exception:
            success = 0
        if success < 10:
            continue

if __name__ == "__main__":
    TARGET_URL = os.environ.get("E2E_URL", "http://localhost:5173/")
    asyncio.run(main(TARGET_URL))
