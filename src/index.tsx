/**
 * 1) KOD ADI:
 * OTTO — React Entry Bootstrapper (Gerçek API başlangıç kontrolü)
 *
 * 2) KOD YOLU (GÖRELI):
 * src/index.tsx
 *
 * 3) KODUN AMACI (5 MADDE):
 * - Uygulamayı root elementine güvenle mount etmek.
 * - Gerçek API için zorunlu .env değişkenlerini kontrol etmek.
 * - L1 global try ile açılışta çökme riskini sıfırlamak.
 * - Global hata dinleyicileriyle tüm hataları loglayıp akışı sürdürmek.
 * - Kullanıcıya kritik hata durumunda güvenli fallback ekranı göstermek.
 *
 * 4) KODLA İLGİLİ TÜM REVİZYONLAR:
 * - Mevcut L1 global try bloğu korundu ve genişletildi.
 * - VITE_API_BASE_URL doğrulaması eklendi (gerçek API kablosu).
 * - window.onerror ve unhandledrejection yakalayıcıları eklendi.
 *
 * 5) KODLA İLGİLİ TALİMATLARIN KODLANMIŞ HALİ:
 * - L1: Tüm bootstrap işlemi try içinde sarıldı.
 * - L2: Env kontrolü ayrı try ile güvenli hale getirildi.
 * - L3: Root bulma ve render adımı kayıt/işlem bazında korundu.
 * - Hata loglanır, süreç durmaz, kullanıcıya temiz fallback gösterilir.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// L2: Env doğrulama (gerçek API kablosu için zorunlu)
function validateEnv(): void {
  try {
    const baseUrl = (import.meta as any)?.env?.VITE_API_BASE_URL;
    if (!baseUrl || typeof baseUrl !== "string") {
      console.warn(
        "[ENV][WARN] VITE_API_BASE_URL eksik. Uygulama çalışır ama gerçek API çağrıları başarısız olabilir."
      );
    } else {
      console.info("[ENV][OK] API Base URL:", baseUrl);
    }
  } catch (e) {
    console.warn("[ENV][WARN] Env kontrolü yapılamadı, fallback ile devam.", e);
  }
}

// L1: Global Entry Point Try-Catch
try {
  validateEnv();

  // L2: Global hata dinleyicileri (akış asla durmaz)
  try {
    window.onerror = function (message, source, lineno, colno, error) {
      console.error("[GLOBAL][onerror]", { message, source, lineno, colno, error });
      return false; // tarayıcı default davranışı sürsün
    };
    window.onunhandledrejection = function (event) {
      console.error("[GLOBAL][unhandledrejection]", event.reason);
    };
  } catch (e) {
    console.warn("[GLOBAL][WARN] Hata dinleyicileri kurulamadı.", e);
  }

  // L3: Root element kontrolü
  const rootElement = document.getElementById("root");
  if (!rootElement) {
    throw new Error("Could not find root element to mount to");
  }

  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} catch (fatalError) {
  console.error("FATAL: Application failed to start", fatalError);
  document.body.innerHTML = `
    <div style="font-family: system-ui, sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #f8fafc; color: #334155;">
      <h1 style="color: #e11d48; margin-bottom: 1rem;">Sistem Hatası</h1>
      <p>Uygulama başlatılırken kritik bir hata oluştu.</p>
      <p style="font-size: 0.8rem; opacity: 0.7;">Lütfen sayfayı yenileyiniz.</p>
    </div>
  `;
}
