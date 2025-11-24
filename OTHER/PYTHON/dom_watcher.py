#!/usr/bin/env python3
"""
DOM Watcher - Browser DOM dinleme sistemi
Frontend'deki tüm DOM değişikliklerini, console mesajlarını
ve network isteklerini gerçek zamanlı olarak izler
"""

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

class DOMWatcher:
    def __init__(self):
        self.console_messages = []
        self.network_requests = []
        self.dom_changes = []
        self.running = True

    def start_watching(self):
        """Browser'ı başlatıp DOM dinlemeye başla"""
        print('🌐 DOM Watcher Başlatılıyor...')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=100)
            page = browser.new_page()

            # Event handlers
            page.on('console', self._handle_console)
            page.on('request', self._handle_request)
            page.on('response', self._handle_response)

            # Frontend'i aç
            page.goto('http://localhost:3000')
            page.wait_for_load_state('networkidle')

            print('✅ Frontend yüklendi - DOM izleme başladı')

            # DOM mutation observer ekle
            page.add_init_script("""
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        console.log('[DOM-CHANGE]', {
                            type: mutation.type,
                            target: mutation.target.tagName,
                            addedNodes: mutation.addedNodes.length,
                            removedNodes: mutation.removedNodes.length
                        });
                    });
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true
                });
            """)

            # Sürekli izleme döngüsü
            while self.running:
                try:
                    # API çağrılarını kontrol et
                    self._check_api_calls(page)

                    # Form elementlerini kontrol et
                    self._check_forms(page)

                    # Console'daki hataları kontrol et
                    self._check_errors()

                    time.sleep(2)  # 2 saniye bekle

                except KeyboardInterrupt:
                    print('\n🛑 DOM izleme durduruluyor...')
                    self.running = False
                except Exception as e:
                    print(f'❌ İzleme hatası: {e}')
                    time.sleep(5)

            browser.close()
            print('✅ DOM Watcher durduruldu')

    def _handle_console(self, msg):
        """Console mesajlarını yakala"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = f'[{timestamp}] [{msg.type}] {msg.text}'
        self.console_messages.append(message)

        if msg.type == 'error':
            print(f'🔴 {message}')
        elif msg.type == 'warning':
            print(f'🟡 {message}')
        elif 'API' in msg.text or 'fetch' in msg.text:
            print(f'🔵 {message}')

    def _handle_request(self, request):
        """Network isteklerini yakala"""
        if '/api/' in request.url:
            timestamp = datetime.now().strftime('%H:%M:%S')
            message = f'[{timestamp}] REQ: {request.method} {request.url}'
            self.network_requests.append(message)
            print(f'📡 {message}')

    def _handle_response(self, response):
        """Network cevaplarını yakala"""
        if '/api/' in response.url:
            timestamp = datetime.now().strftime('%H:%M:%S')
            message = f'[{timestamp}] RES: {response.status} {response.url}'
            self.network_requests.append(message)

            if response.status == 200:
                print(f'✅ {message}')
            else:
                print(f'❌ {message}')

    def _check_api_calls(self, page):
        """API çağrılarının durumunu kontrol et"""
        try:
            # Cities dropdown'u kontrol et
            cities_select = page.locator('select').first
            if cities_select.count() > 0:
                options = cities_select.locator('option')
                if options.count() > 1:
                    print('✅ Cities dropdown dolu')
                else:
                    print('⚠️ Cities dropdown boş')

            # Services dropdown'u kontrol et
            services_select = page.locator('select').nth(1) if page.locator('select').count() > 1 else None
            if services_select and services_select.count() > 0:
                options = services_select.locator('option')
                if options.count() > 1:
                    print('✅ Services dropdown dolu')
                else:
                    print('⚠️ Services dropdown boş')

        except Exception as e:
            print(f'❌ Form kontrol hatası: {e}')

    def _check_forms(self, page):
        """Form elementlerini kontrol et"""
        try:
            # Input alanlarını kontrol et
            inputs = page.locator('input[type="text"], input[type="search"]')
            if inputs.count() > 0:
                print(f'✅ {inputs.count()} adet input alanı bulundu')

            # Butonları kontrol et
            buttons = page.locator('button')
            if buttons.count() > 0:
                print(f'✅ {buttons.count()} adet buton bulundu')

        except Exception as e:
            print(f'❌ Element kontrol hatası: {e}')

    def _check_errors(self):
        """Console'daki hataları analiz et"""
        error_count = len([msg for msg in self.console_messages if '[error]' in msg])
        if error_count > 0:
            print(f'🔴 Toplam {error_count} adet hata tespit edildi')

        warning_count = len([msg for msg in self.console_messages if '[warning]' in msg])
        if warning_count > 0:
            print(f'🟡 Toplam {warning_count} adet uyarı tespit edildi')

if __name__ == '__main__':
    watcher = DOMWatcher()
    watcher.start_watching()
