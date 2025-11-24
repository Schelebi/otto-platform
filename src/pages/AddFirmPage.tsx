import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Send, PhoneCall } from 'lucide-react';

export const AddFirmPage: React.FC = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    try {
      navigate(-1);
    } catch (error) {
      console.warn('[AddFirmPage] navigate back failed', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm uppercase text-gray-500 font-semibold tracking-wide">
              Kayıt Başvurusu
            </p>
            <h1 className="text-3xl font-bold text-gray-900">Firmanızı OTTO Rehberine Ekleyin</h1>
            <p className="text-gray-600">
              Bilgilerinizi bırakın, doğrulama ekibimiz en kısa sürede sizinle iletişime geçsin.
            </p>
          </div>
          <button
            type="button"
            onClick={handleBack}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Geri Dön
          </button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <form
            onSubmit={(e) => e.preventDefault()}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Firma Adı</label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Örn. Ankara Hızır Oto Kurtarma"
                required
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">İl</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="İl"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">İlçe</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="İlçe"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">İletişim Telefonu</label>
              <input
                type="tel"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="0 5xx xxx xx xx"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hizmetler</label>
              <textarea
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows={4}
                placeholder="Oto çekici, yol yardım, vinç..."
              ></textarea>
            </div>
            <button
              type="submit"
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition flex items-center justify-center gap-2"
            >
              <Send size={18} /> Başvuruyu Gönder
            </button>
            <p className="text-xs text-gray-500">
              Form gönderimi demo amaçlıdır. Gerçek başvurular için aşağıdaki iletişim kanallarını kullanın.
            </p>
          </form>
        </div>

        <aside className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6">
          <div className="flex items-center gap-3">
            <FileText className="text-primary-600" />
            <div>
              <p className="font-semibold text-gray-900">Doğrulama Süreci</p>
              <p className="text-sm text-gray-600">
                Başvurular 1 iş günü içinde manuel olarak kontrol edilir.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <PhoneCall className="text-primary-600" />
            <div>
              <p className="font-semibold text-gray-900">Destek Hattı</p>
              <p className="text-sm text-gray-600">0850 123 45 67</p>
            </div>
          </div>
          <div className="bg-primary-50 border border-primary-100 rounded-xl p-4 text-sm text-primary-900">
            Başvurunuz kabul edildiğinde panel erişimi ve API entegrasyonu için yönlendirme yapılır.
          </div>
        </aside>
      </div>
    </div>
  );
};

export default AddFirmPage;
