import { chromium } from 'playwright';

async function testCascadeDropdown() {
  console.log('🎭 Playwright başlatılıyor...');

  // Browser aç
  const browser = await chromium.launch({
    headless: false,  // Görünür mod - ekran kaydı için
    slowMo: 1000      // İnsan gibi yavaş hareket
  });

  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 }
  });

  // Ekran kaydı başlat
  const page = await context.newPage();

  try {
    console.log('📹 Ekran kaydı başlatılıyor...');
    await page.goto('http://localhost:5173/search', { waitUntil: 'networkidle' });

    // Başlık kontrolü
    await page.waitForSelector('h1', { timeout: 10000 });
    console.log('✅ Sayfa yüklendi');

    // İl dropdown'unu bekle
    await page.waitForSelector('select[name="cityId"]', { timeout: 10000 });
    console.log('✅ İl dropdown bulundu');

    // Screenshot 1: Başlangıç
    await page.screenshot({ path: 'test_01_start.png' });
    console.log('📸 Başlangıç ekran görüntüsü alındı');

    // İlk ili seç
    console.log('🏙️ İlk şehir seçiliyor...');
    const cityOptions = await page.$eval('select[name="cityId"]', select => {
      const options = Array.from(select.options);
      return options.filter(opt => opt.value && opt.value !== '').slice(0, 1).map(opt => opt.value);
    });

    if (cityOptions.length > 0) {
      await page.selectOption('select[name="cityId"]', cityOptions[0]);
      await page.waitForTimeout(3000); // İlçelerin yüklenmesi için bekle

      // Screenshot 2: Şehir seçildi
      await page.screenshot({ path: 'test_02_city_selected.png' });
      console.log('📸 Şehir seçildikten sonra ekran görüntüsü alındı');

      // İlçe dropdown kontrolü
      const districtSelect = await page.$('select[name="districtId"]');
      const districtOptions = await districtSelect.$$eval('option', options =>
        options.map(opt => ({ value: opt.value, text: opt.text }))
      );

      console.log('📍 İlçe sayısı:', districtOptions.length);
      console.log('📍 İlçeler:', districtOptions.map(opt => opt.text).slice(0, 5));

      // İlçe seç
      if (districtOptions.length > 1) {
        console.log('🏘️ İlk ilçe seçiliyor...');
        await page.selectOption('select[name="districtId"]', districtOptions[1].value);
        await page.waitForTimeout(1000);

        // Screenshot 3: İlçe seçildi
        await page.screenshot({ path: 'test_03_district_selected.png' });
        console.log('📸 İlçe seçildikten sonra ekran görüntüsü alındı');
      }

      // Hizmet seç
      const serviceOptions = await page.$eval('select[name="serviceId"]', select => {
        const options = Array.from(select.options);
        return options.filter(opt => opt.value && opt.value !== '').slice(0, 1).map(opt => opt.value);
      });

      if (serviceOptions.length > 0) {
        console.log('🔧 İlk hizmet seçiliyor...');
        await page.selectOption('select[name="serviceId"]', serviceOptions[0]);
        await page.waitForTimeout(1000);

        // Screenshot 4: Hizmet seçildi
        await page.screenshot({ path: 'test_04_service_selected.png' });
        console.log('📸 Hizmet seçildikten sonra ekran görüntüsü alındı');
      }

      // Arama butonuna tıkla
      console.log('🔍 Arama yapılıyor...');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);

      // Screenshot 5: Sonuçlar
      await page.screenshot({ path: 'test_05_results.png' });
      console.log('📸 Arama sonuçları ekran görüntüsü alındı');

      // Sonuç kartlarını kontrol et
      const resultCards = await page.$$('.bg-white.rounded-lg.shadow');
      console.log('📊 Bulunan firma sayısı:', resultCards.length);

      if (resultCards.length > 0) {
        const firstCard = await resultCards[0].textContent();
        console.log('📋 İlk firma:', firstCard?.substring(0, 100));
      }

      console.log('✅ Test tamamlandı!');
    } else {
      console.log('❌ Şehir seçeneği bulunamadı');
    }

  } catch (error) {
    console.error('❌ Test hatası:', error);
    await page.screenshot({ path: 'test_error.png' });
  } finally {
    await browser.close();
  }
}

// Testi çalıştır
testCascadeDropdown().catch(console.error);
