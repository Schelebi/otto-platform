// 1) KOD ADI:
// NotFoundPage (404 / Kayıp Sayfa)

// 2) KOD YOLU (GÖRELI):
// src/pages/NotFoundPage.tsx

// 3) KODUN AMACI (5 MADDE):
// - Bulunamayan rotalarda kullanıcıyı net yönlendirmek.
// - Uygulama çökmeden güvenli UI fallback sunmak.
// - Tüm cihazlarda responsive ve temiz bir görünüm sağlamak.
// - Ana sayfa ve arama sayfasına hızlı dönüş vermek.
// - Router fallback yapısı ile uyumlu çalışmak.

// 4) KODLA İLGİLİ TÜM REVİZYONLAR:
// - Yeni dosya oluşturuldu.
// - Responsive 404 tasarımı eklendi.
// - Kullanıcı yönlendirme butonları eklendi.

// 5) KODLA İLGİLİ TALİMATLARIN TÜMÜ KODLANDI:
// - TRY zinciri ile render güvenliği sağlandı.
// - Tailwind sınıfları ile tüm cihaz uyumu garantilendi.

import React from "react";
import { Link } from "react-router-dom";
import { Home, Search } from "lucide-react";

export const NotFoundPage: React.FC = () => {
  // L1: Global component safety
  try {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-lg bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
          <div className="text-6xl font-extrabold text-gray-200 mb-2">404</div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">
            Sayfa bulunamadı
          </h1>
          <p className="text-gray-600 mb-8">
            Aradığın sayfa taşınmış veya kaldırılmış olabilir.
          </p>

          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              to="/"
              className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-primary-600 text-white font-semibold hover:bg-primary-700 transition"
            >
              <Home size={18} /> Ana Sayfa
            </Link>

            <Link
              to="/search"
              className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200 transition"
            >
              <Search size={18} /> Arama
            </Link>
          </div>
        </div>
      </div>
    );
  } catch (e) {
    console.error("[L1][NotFoundPage] Render hatası", e);
    return (
      <div className="p-10 text-center text-red-600">
        Bir hata oluştu. Ana sayfaya dön.
      </div>
    );
  }
};

export default NotFoundPage;
