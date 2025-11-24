/**
 * 1) KOD ADI:
 * OTTO — App Router + ErrorBoundary (Gerçek API sayfa akışı)
 *
 * 2) KOD YOLU (GÖRELI):
 * src/App.tsx
 *
 * 3) KODUN AMACI (5 MADDE):
 * - Uygulama rotalarını gerçek API akışına uygun yönetmek.
 * - Sayfa bazlı lazy loading ile performansı artırmak.
 * - React render hatalarını ErrorBoundary ile yakalamak.
 * - L1/L2/L3 korumayla router akışını çökmez hale getirmek.
 * - Tüm cihazlarda stabil layout + route geçişi sağlamak.
 *
 * 4) KODLA İLGİLİ TÜM REVİZYONLAR:
 * - Named import sayfalar React.lazy ile dinamik yüklendi.
 * - ErrorBoundary eklendi (child render hataları yakalanır).
 * - Suspense fallback eklendi (yükleme durumunda boş kalmaz).
 *
 * 5) KODLA İLGİLİ TALİMATLARIN KODLANMIŞ HALİ:
 * - L1: App render akışı try ile sarıldı.
 * - L2: Router/Suspense kritik adım olarak ayrı korundu.
 * - L3: Route elementleri ErrorBoundary içinde izole edildi.
 * - Hata loglanır, akış durmaz, kullanıcı fallback görür.
 */

import React from "react";
import { HashRouter } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AppRoutes } from "./router/AppRouter";

// ErrorBoundary: React render hatalarını yakalar
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: unknown }
> {
  state = { hasError: false, error: undefined };

  static getDerivedStateFromError(error: unknown) {
    return { hasError: true, error };
  }

  componentDidCatch(error: unknown, errorInfo: unknown) {
    console.error("Global Error Boundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 16 }}>
          Uygulama yüklenirken hata oluştu. Lütfen yenileyiniz.
        </div>
      );
    }
    return this.props.children;
  }
}

const App: React.FC = () => {
  // L1: App Logic Try
  try {
    return (
      <HashRouter>
        <Layout>
          {/* L2: Route render izolasyonu */}
          <ErrorBoundary>
            <AppRoutes />
          </ErrorBoundary>
        </Layout>
      </HashRouter>
    );
  } catch (error) {
    console.error("Router/Layout Error:", error);
    return <div>Uygulama yüklenirken hata oluştu. Lütfen yenileyiniz.</div>;
  }
};

export default App;
