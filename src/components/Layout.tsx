/**
 * KOD ADI: LAYOUT — GLOBAL SHELL + ERROR + TOAST
 * KOD YOLU (GÖRELİ): src/components/Layout.tsx
 *
 * KODUN AMACI (5):
 * 1) Tüm sayfalar için ortak header/footer ve responsive iskelet sağlamak.
 * 2) Router geçişlerinde global loading göstermek.
 * 3) Çocuk bileşen hatalarını ErrorBoundary ile yakalayıp çöküşü önlemek.
 * 4) API/UI hataları için üst bildirim (toast) altyapısı sunmak.
 * 5) Scroll/overflow davranışını tüm cihazlarda stabil yönetmek.
 *
 * REVİZYONLAR:
 * - REVİZYON NO: 2 bu sayfada yapıldı → ErrorBoundary + ToastContext + route loader eklendi.
 *
 * TALİMATLAR (ZORUNLU):
 * - L1–L2–L3 TRY modeli layout render ve state akışında uygulanır.
 * - Router değişiminde kısa süreli loading göstergesi zorunlu.
 * - Toast altyapısı dış bileşenlerce kullanılabilir olmalı.
 * - Responsive grid ve overflow-x engeli tüm cihazlarda korunur.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Truck, MapPin, Phone, Menu, X, AlertTriangle, Loader2 } from 'lucide-react';

type ToastType = 'error' | 'info' | 'success';
type Toast = { id: string; type: ToastType; message: string };

const ToastContext = React.createContext<{ pushToast: (message: string, type?: ToastType) => void }>({
  pushToast: () => {},
});

export const useToast = () => React.useContext(ToastContext);

class ErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (err: unknown) => void },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    try {
      console.error('[Layout] ErrorBoundary caught:', error);
      this.props.onError?.(error);
    } catch {}
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center p-6">
          <div className="bg-white border border-red-200 rounded-xl p-6 text-center max-w-md w-full">
            <AlertTriangle className="w-10 h-10 text-red-500 mx-auto mb-3" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Bir hata oluştu</h2>
            <p className="text-gray-600 mb-4">Sayfa geçici olarak yüklenemedi.</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-primary-600 hover:bg-primary-700 text-white px-5 py-2 rounded-lg font-semibold"
            >
              Yenile
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [routeLoading, setRouteLoading] = useState(false);
  const location = useLocation();

  const pushToast = (message: string, type: ToastType = 'info') => {
    try {
      const id = `${Date.now()}-${Math.random()}`;
      setToasts((prev) => [...prev, { id, type, message }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 3500);
    } catch (e) {
      console.warn('[Layout] pushToast failed', e);
    }
  };

  // Route change lightweight loader
  useEffect(() => {
    try {
      setRouteLoading(true);
      const t = setTimeout(() => setRouteLoading(false), 250);
      return () => clearTimeout(t);
    } catch {
      setRouteLoading(false);
    }
  }, [location.pathname, location.search]);

  const ctx = useMemo(() => ({ pushToast }), []);

  // L1: Layout Rendering Try
  try {
    return (
      <ToastContext.Provider value={ctx}>
        <div className="flex flex-col min-h-screen overflow-x-hidden">
          {/* Toast Area */}
          <div className="fixed top-3 right-3 z-[9999] space-y-2">
            {toasts.map((t) => (
              <div
                key={t.id}
                className={`px-4 py-3 rounded-lg shadow-lg text-sm font-semibold text-white ${
                  t.type === 'error'
                    ? 'bg-red-600'
                    : t.type === 'success'
                    ? 'bg-green-600'
                    : 'bg-slate-900'
                }`}
              >
                {t.message}
              </div>
            ))}
          </div>

          {/* Navigation */}
          <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <Link to="/" className="flex-shrink-0 flex items-center gap-2">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center text-white">
                      <Truck size={24} />
                    </div>
                    <div>
                      <h1 className="text-xl font-bold text-gray-900 leading-none">OTTO</h1>
                      <span className="text-xs text-gray-500 font-medium">Oto Kurtarma</span>
                    </div>
                  </Link>
                </div>

                {/* Desktop Menu */}
                <div className="hidden md:flex items-center space-x-8">
                  <Link to="/" className="text-gray-600 hover:text-primary-600 font-medium transition">
                    Ana Sayfa
                  </Link>
                  <Link to="/search" className="text-gray-600 hover:text-primary-600 font-medium transition">
                    Firmalar
                  </Link>
                  <Link to="/add-firm" className="text-gray-600 hover:text-primary-600 font-medium transition">
                    Firma Ekle
                  </Link>
                  <a
                    href="tel:08501234567"
                    className="bg-primary-600 text-white px-5 py-2 rounded-full font-medium hover:bg-primary-700 transition shadow-lg shadow-primary-500/30 flex items-center gap-2"
                  >
                    <Phone size={18} /> Acil Çağrı
                  </a>
                </div>

                {/* Mobile Menu Button */}
                <div className="flex items-center md:hidden">
                  <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-gray-600">
                    {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
                  </button>
                </div>
              </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
              <div className="md:hidden bg-white border-t p-4 space-y-4">
                <Link
                  to="/"
                  onClick={() => setIsMenuOpen(false)}
                  className="block text-gray-700 font-medium"
                >
                  Ana Sayfa
                </Link>
                <Link
                  to="/search"
                  onClick={() => setIsMenuOpen(false)}
                  className="block text-gray-700 font-medium"
                >
                  Firmalar
                </Link>
                <Link
                  to="/add-firm"
                  onClick={() => setIsMenuOpen(false)}
                  className="block text-gray-700 font-medium"
                >
                  Firma Ekle
                </Link>
                <a
                  href="tel:08501234567"
                  className="w-full bg-primary-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2"
                >
                  <Phone size={18} /> Acil Çağrı
                </a>
              </div>
            )}

            {/* Route Loading Bar */}
            {routeLoading && (
              <div className="h-1 w-full bg-primary-100">
                <div className="h-1 bg-primary-600 animate-pulse w-1/2" />
              </div>
            )}
          </nav>

          {/* Main Content */}
          <main className="flex-grow bg-slate-50 overflow-x-hidden">
            <ErrorBoundary onError={() => pushToast('Sayfa hatası yakalandı', 'error')}>
              {children}
            </ErrorBoundary>
          </main>

          {/* Footer */}
          <footer className="bg-secondary-900 text-white py-12">
            <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 bg-primary-600 rounded flex items-center justify-center">
                    <Truck size={18} />
                  </div>
                  <span className="text-xl font-bold">OTTO</span>
                </div>
                <p className="text-slate-400 text-sm">
                  Türkiye'nin en geniş oto kurtarma ve çekici rehberi.
                  ANISA altyapısından gerçek zamanlı beslenir.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4 text-primary-500">Hızlı Bağlantılar</h3>
                <ul className="space-y-2 text-slate-300">
                  <li>
                    <Link to="/search" className="hover:text-white">Çekici Bul</Link>
                  </li>
                  <li>
                    <Link to="/" className="hover:text-white">Hizmet Bölgeleri</Link>
                  </li>
                  <li>
                    <Link to="/" className="hover:text-white">Kurumsal</Link>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4 text-primary-500">İletişim</h3>
                <div className="flex items-center gap-2 text-slate-300 mb-2">
                  <MapPin size={16} /> İstanbul, Türkiye
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <Phone size={16} /> 0850 123 45 67
                </div>
              </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 mt-8 pt-8 border-t border-slate-800 text-center text-slate-500 text-sm">
              &copy; {new Date().getFullYear()} OTTO Platformu. Tüm hakları saklıdır.
            </div>
          </footer>
        </div>
      </ToastContext.Provider>
    );
  } catch (error) {
    console.error('[Layout] render error:', error);
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="animate-spin mr-2" /> Arayüz yüklenemedi.
      </div>
    );
  }
};

export default Layout;
