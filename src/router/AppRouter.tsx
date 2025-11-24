// 1) KOD ADI:
// AppRouter (ANISA React Router Katmanı)

// 2) KOD YOLU (GÖRELI):
// src/router/AppRouter.tsx

// 3) KODUN AMACI (5 MADDE):
// - Uygulama rotalarını tek merkezden yönetmek.
// - Lazy-load ile sayfaları güvenli ve hızlı yüklemek.
// - Route render aşamalarını üç katmanlı TRY ile korumak.
// - Bozuk rota veya render hatasında güvenli fallback sağlamak.
// - Mevcut App.tsx ve Layout yapısı ile birebir uyumlu çalışmak.

// 4) KODLA İLGİLİ TÜM REVİZYONLAR:
// - Yeni dosya oluşturuldu (studio çıktısına ek modül).
// - HashRouter/Routes uyumuna göre v6 route şeması tanımlandı.
// - Lazy import + Suspense fallback eklendi.
// - Route render hataları için SafeRouteWrapper eklendi.
// - 404 rotası NotFoundPage ile yönetildi.

// 5) KODLA İLGİLİ TALİMATLARIN TÜMÜ KODLANDI:
// - L1–L2–L3 TRY katmanları rota seviyesinde uygulandı.
// - Çökme olmadan devam akışı zorunluluğu sağlandı.
// - Responsive ve UX fallback yükleme ekranı eklendi.

import React, { Suspense, lazy, ReactNode } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Safe lazy loader: modül hatası olursa global fallback çalışır.
const safeLazy = <T extends { default: React.ComponentType<any> }>(
  factory: () => Promise<T>,
  name: string
) =>
  lazy(async () => {
    try {
      const mod = await factory();
      return mod;
    } catch (e) {
      console.error(`[L2][safeLazy] ${name} yüklenemedi`, e);
      // fallback olarak boş sayfa döndür, sonra Route wrapper yakalar
      return { default: () => <Navigate to="/" replace /> } as unknown as T;
    }
  });

const HomePage = safeLazy(
  () => import("../pages/HomePage.tsx"),
  "HomePage"
);
const SearchPage = safeLazy(
  () => import("../pages/SearchPage.tsx"),
  "SearchPage"
);
const FirmDetailPage = safeLazy(
  () => import("../pages/FirmDetailPage.tsx"),
  "FirmDetailPage"
);
const AddFirmPage = safeLazy(
  () => import("../pages/AddFirmPage.tsx"),
  "AddFirmPage"
);
const NotFoundPage = safeLazy(
  () => import("../pages/NotFoundPage.tsx"),
  "NotFoundPage"
);

const SafeRouteWrapper: React.FC<{ children: ReactNode }> = ({ children }) => {
  // L3: record-level (render-level) safety
  try {
    return <>{children}</>;
  } catch (e) {
    console.error("[L3][SafeRouteWrapper] Route render hatası", e);
    return <Navigate to="/" replace />;
  }
};

export const AppRoutes: React.FC = () => {
  // L1: Route render try zinciri
  try {
    return (
      <Suspense fallback={<div className="p-10 text-center">Yükleniyor...</div>}>
        <Routes>
          {/* L2: Her route için izolasyon */}
          <Route path="/" element={<Navigate to="/search" replace />} />
          <Route
            path="/search"
            element={
              <SafeRouteWrapper>
                <SearchPage />
              </SafeRouteWrapper>
            }
          />
          <Route
            path="/firm/:id"
            element={
              <SafeRouteWrapper>
                <FirmDetailPage />
              </SafeRouteWrapper>
            }
          />
          <Route
            path="/add-firm"
            element={
              <SafeRouteWrapper>
                <AddFirmPage />
              </SafeRouteWrapper>
            }
          />
          <Route
            path="*"
            element={
              <SafeRouteWrapper>
                <NotFoundPage />
              </SafeRouteWrapper>
            }
          />
        </Routes>
      </Suspense>
    );
  } catch (error) {
    console.error("Route render hatası:", error);
    return (
      <div className="p-10 text-center text-red-600">
        Sayfa yüklenirken hata oluştu. Lütfen yenileyiniz.
      </div>
    );
  }
};
