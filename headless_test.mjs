import { chromium } from 'playwright';

async function testCascadeDropdownHeadless() {
  console.log('🎭 Playwright Headless Test Başlatılıyor...');

  // Headless modda browser aç
  const browser = await chromium.launch({
    headless: true,   // Headless mod - ekran kaydı yok
    slowMo: 500       // Hızlı test için daha az bekleme
  });

  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 }
  });

  const page = await context.newPage();

  try {
    console.log('📱 Sayfa yükleniyor...');
    await page.goto('http://localhost:3000/search', { waitUntil: 'networkidle' });

    // Başlık kontrolü
    await page.waitForSelector('h1', { timeout: 10000 });
    console.log('✅ Sayfa yüklendi - Başlık bulundu');

    // İl dropdown'unu bekle
    await page.waitForSelector('select[name="cityId"]', { timeout: 10000 });
    console.log('✅ İl dropdown bulundu');

    // İlk ili seç
    console.log('🏙️ İlk şehir seçiliyor...');
    const cityOptions = await page.$eval('select[name="cityId"]', select => {
      const options = Array.from(select.options);
      return options.filter(opt => opt.value && opt.value !== '').slice(0, 1).map(opt => opt.value);
    });

    if (cityOptions.length > 0) {
      console.log(`📍 Seçilen şehir: ${cityOptions[0]}`);
      await page.selectOption('select[name="cityId"]', cityOptions[0]);
      await page.waitForTimeout(2000); // İlçelerin yüklenmesi için bekle

      // İlçe dropdown kontrolü
      const districtSelect = await page.$('select[name="districtId"]');
      const districtOptions = await districtSelect.$$eval('option', options =>
        options.map(opt => ({ value: opt.value, text: opt.text }))
      );

      console.log(`📍 Bulunan ilçe sayısı: ${districtOptions.length}`);
      console.log('📍 İlçeler:', districtOptions.map(opt => opt.text).slice(0, 5));

      // KASKAD TEST BAŞARILI MI?
      if (districtOptions.length > 1) {
        console.log('✅ KASKAD TEST BAŞARILI - İlçeler yüklendi!');

        // İlk ilçeyi seç
        console.log('🏘️ İlk ilçe seçiliyor...');
        await page.selectOption('select[name="districtId"]', districtOptions[1].value);
        await page.waitForTimeout(1000);

        // Hizmet seç
        const serviceOptions = await page.$eval('select[name="serviceId"]', select => {
          const options = Array.from(select.options);
          return options.filter(opt => opt.value && opt.value !== '').slice(0, 1).map(opt => opt.value);
        });

        if (serviceOptions.length > 0) {
          console.log('🔧 İlk hizmet seçiliyor...');
          await page.selectOption('select[name="serviceId"]', serviceOptions[0]);
          await page.waitForTimeout(1000);

          // Arama butonuna tıkla
          console.log('🔍 Arama yapılıyor...');
          await page.click('button[type="submit"]');
          await page.waitForTimeout(3000);

          // Sonuç kartlarını kontrol et
          const resultCards = await page.$$('.bg-white.rounded-lg.shadow');
          console.log(`📊 Bulunan firma sayısı: ${resultCards.length}`);

          if (resultCards.length > 0) {
            const firstCard = await resultCards[0].textContent();
            console.log('📋 İlk firma:', firstCard?.substring(0, 100));
            console.log('✅ TAM TEST BAŞARILI - Kaskad + Arama çalışıyor!');
          } else {
            console.log('⚠️ Arama sonuçları boş - API kontrolü gerekli');
          }
        } else {
          console.log('⚠️ Hizmet seçeneği bulunamadı');
        }
      } else {
        console.log('❌ KASKAD TEST BAŞARISIZ - İlçeler yüklenmedi!');
      }
    } else {
      console.log('❌ Şehir seçeneği bulunamadı');
    }

  } catch (error) {
    console.error('❌ Test hatası:', error.message);

    // Ek hata bilgisi
    if (error.message.includes('net::ERR_CONNECTION_REFUSED')) {
      console.log('💡 Frontend çalışmıyor - npm run dev komutunu çalıştırın');
    } else if (error.message.includes('timeout')) {
      console.log('💡 Sayfa yükleme timeout - Backend/Frontend kontrolü gerekli');
    }
  } finally {
    await browser.close();
    console.log('🏁 Test tamamlandı');
  }
}

// Testi çalıştır
testCascadeDropdownHeadless().catch(console.error);
