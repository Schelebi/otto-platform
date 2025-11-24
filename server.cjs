const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');

const app = express();
const PORT = process.env.API_PORT || 3001;

const dbConfig = {
  host: process.env.DB_HOST || '35.214.224.135',
  user: process.env.DB_USER || 'uwcw1gm1sor8u',
  password: process.env.DB_PASSWORD || 'g05jkizfzjdp',
  database: process.env.DB_NAME || 'db6ctx4kvleywe',
  charset: 'utf8mb4',
  waitForConnections: true
};

const slugify = (value = '') =>
  value.toString().trim().toLowerCase()
    .replace(/ı/g, 'i').replace(/ğ/g, 'g').replace(/ü/g, 'u')
    .replace(/ş/g, 's').replace(/ö/g, 'o').replace(/ç/g, 'c')
    .replace(/[^a-z0-9-\s]/g, '')
    .replace(/\s+/g, '-');

let db;

async function initializeDatabase() {
  db = await mysql.createConnection(dbConfig);
  console.log('✅ MySQL bağlantısı hazır');
}

app.use(cors());
app.use(express.json());

app.get('/api/cities', async (req, res) => {
  try {
    const [rows] = await db.execute(
      'SELECT il AS name, MIN(il_id) AS il_id FROM anisa WHERE il_id <> 0 AND il IS NOT NULL GROUP BY il ORDER BY il'
    );
    const cities = rows.map(row => ({
      id: String(row.il_id ?? row.name),
      name: row.name,
      slug: slugify(row.name)
    }));
    res.json({ cities });
  } catch (error) {
    console.error('Cities API error:', error);
    res.status(500).json({ error: 'İller yüklenemedi' });
  }
});

app.get('/api/services', async (req, res) => {
  try {
    const [rows] = await db.execute(
      'SELECT DISTINCT hizmetler FROM anisa WHERE hizmetler IS NOT NULL AND hizmetler <> "" ORDER BY hizmetler'
    );
    const services = rows.map(row => ({
      id: slugify(row.hizmetler),
      name: row.hizmetler,
      slug: slugify(row.hizmetler),
      description: row.hizmetler
    }));
    res.json({ services });
  } catch (error) {
    console.error('Services API error:', error);
    res.status(500).json({ error: 'Hizmetler yüklenemedi' });
  }
});

app.get('/api/firms/search', async (req, res) => {
  try {
    const { cityId, districtId, serviceId, keyword } = req.query;
    console.log('Search params:', { cityId, districtId, serviceId, keyword });
    let query = 'SELECT * FROM anisa WHERE aktif = 1';
    const params = [];

    if (serviceId) { query += ' AND hizmetler = ?'; params.push(serviceId); }
    if (cityId) { query += ' AND il = ?'; params.push(cityId); }
    if (districtId) { query += ' AND ilce = ?'; params.push(districtId); }

    if (keyword) {
      query += ' AND (firma_adi LIKE ? OR all_hepsi LIKE ?)';
      params.push(`%${keyword}%`, `%${keyword}%`);
    }

    query += ' ORDER BY id DESC LIMIT 50';
    const [rows] = await db.execute(query, params);

    const firms = rows.map(row => ({
      id: row.id,
      name: row.firma_adi || 'İsimsiz Firma',
      phone: row.telefon || '',
      whatsapp: row.whatsapp || '',
      email: row.email || '',
      address: row.adres_full || row.adres || '',
      city: row.il || '',
      district: row.ilce || '',
      hizmetler: row.hizmetler || '',
      latitude: row.lat != null ? Number(row.lat) : null,
      longitude: row.lng != null ? Number(row.lng) : null,
      rating: row.puan != null ? Number(row.puan) : 0,
      reviews: row.yorum_sayisi != null ? Number(row.yorum_sayisi) : 0,
      verified: !!row.aktif,
      featured_image: row.featured_image || ''
    }));
    res.json({ firms });
  } catch (error) {
    console.error('Firms search API error:', error);
    res.status(500).json({ error: 'Firmalar yüklenemedi' });
  }
});

// İl bazlı firma arama endpoint'i
app.get('/api/firms/by-city/:city', async (req, res) => {
  try {
    const { city } = req.params;
    console.log('City-based firms search for:', city);

    const [rows] = await db.execute(
      'SELECT * FROM anisa WHERE il = ? AND aktif = 1 ORDER BY firma_adi LIMIT 100',
      [city]
    );

    const firms = rows.map(row => ({
      id: row.id,
      name: row.firma_adi || 'İsimsiz Firma',
      city: row.il || '',
      address: row.adres_full || '',
      slug: row.slug || '',
      phone: row.telefon || '',
      whatsapp: row.whatsapp || '',
      email: row.email || '',
      latitude: row.latitude,
      longitude: row.longitude,
      rating: row.puan != null ? Number(row.puan) : 0,
      reviews: row.yorum_sayisi != null ? Number(row.yorum_sayisi) : 0,
      verified: !!row.aktif,
      featured_image: row.featured_image || ''
    }));

    console.log(`Found ${firms.length} firms for city: ${city}`);
    res.json({ firms });
  } catch (error) {
    console.error('City-based firms API error:', error);
    res.status(500).json({ error: 'Şehre göre firmalar yüklenemedi' });
  }
});

app.get('/api/firms/:id', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM anisa WHERE id = ?', [req.params.id]);
    if (!rows.length) {
      return res.status(404).json({ error: 'Firma bulunamadı' });
    }
    const row = rows[0];
    res.json({
      firm: {
        id: row.id,
        name: row.firma_adi,
        phone: row.telefon,
        whatsapp: row.whatsapp,
        email: row.email,
        address: row.adres_full || row.adres || '',
        city: row.il,
        district: row.ilce,
        hizmetler: row.hizmetler,
        latitude: row.lat != null ? Number(row.lat) : null,
        longitude: row.lng != null ? Number(row.lng) : null,
        rating: row.puan != null ? Number(row.puan) : 0,
        reviews: row.yorum_sayisi != null ? Number(row.yorum_sayisi) : 0,
        verified: !!row.aktif,
        featured_image: row.featured_image || ''
      }
    });
  } catch (error) {
    console.error('Firm detail API error:', error);
    res.status(500).json({ error: 'Firma detayı yüklenemedi' });
  }
});

initializeDatabase().then(() => {
  app.listen(PORT, () => console.log(`🚀 Production API ${PORT} portunda`));
});
