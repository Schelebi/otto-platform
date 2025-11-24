const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');

const app = express();
const PORT = process.env.API_PORT || 3001;

app.use(cors());
app.use(express.json());

// MySQL veritabanı bağlantısı
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'otto_database',
  charset: 'utf8mb4'
};

let db;

async function initializeDatabase() {
  try {
    db = await mysql.createConnection(dbConfig);
    console.log('✅ MySQL veritabanına bağlandı');
    await ensureTablesExist();
  } catch (error) {
    console.error('❌ Veritabanı bağlantı hatası:', error);
    process.exit(1);
  }
}

async function ensureTablesExist() {
  const tables = [
    `CREATE TABLE IF NOT EXISTS cities (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      slug VARCHAR(100) NOT NULL UNIQUE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,

    `CREATE TABLE IF NOT EXISTS districts (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      slug VARCHAR(100) NOT NULL,
      city_id INT NOT NULL,
      FOREIGN KEY (city_id) REFERENCES cities(id),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,

    `CREATE TABLE IF NOT EXISTS services (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      slug VARCHAR(100) NOT NULL UNIQUE,
      description TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,

    `CREATE TABLE IF NOT EXISTS firms (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(200) NOT NULL,
      description TEXT,
      phone VARCHAR(20) NOT NULL,
      whatsapp VARCHAR(20),
      email VARCHAR(100),
      address TEXT NOT NULL,
      city_id INT NOT NULL,
      district_id INT NOT NULL,
      latitude DECIMAL(10, 8),
      longitude DECIMAL(11, 8),
      rating DECIMAL(3, 2) DEFAULT 0,
      reviews INT DEFAULT 0,
      verified BOOLEAN DEFAULT FALSE,
      featured BOOLEAN DEFAULT FALSE,
      working_hours VARCHAR(50),
      website VARCHAR(200),
      established YEAR,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (city_id) REFERENCES cities(id),
      FOREIGN KEY (district_id) REFERENCES districts(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,

    `CREATE TABLE IF NOT EXISTS firm_services (
      id INT AUTO_INCREMENT PRIMARY KEY,
      firm_id INT NOT NULL,
      service_id INT NOT NULL,
      FOREIGN KEY (firm_id) REFERENCES firms(id) ON DELETE CASCADE,
      FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
      UNIQUE KEY unique_firm_service (firm_id, service_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`
  ];

  for (const tableQuery of tables) {
    try {
      await db.execute(tableQuery);
    } catch (error) {
      console.log('Tablo oluşturma hatası (muhtemelen zaten var):', error.message);
    }
  }
}

// İller endpoint
app.get('/api/cities', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM cities ORDER BY name ASC');
    res.json({ cities: rows });
  } catch (error) {
    console.error('Cities API error:', error);
    res.status(500).json({ error: 'İller yüklenemedi' });
  }
});

// İlçeler endpoint
app.get('/api/districts/:cityId', async (req, res) => {
  try {
    const { cityId } = req.params;
    const [rows] = await db.execute(
      'SELECT * FROM districts WHERE city_id = ? ORDER BY name ASC',
      [cityId]
    );
    res.json({ districts: rows });
  } catch (error) {
    console.error('Districts API error:', error);
    res.status(500).json({ error: 'İlçeler yüklenemedi' });
  }
});

// Hizmetler endpoint
app.get('/api/services', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM services ORDER BY name ASC');
    res.json({ services: rows });
  } catch (error) {
    console.error('Services API error:', error);
    res.status(500).json({ error: 'Hizmetler yüklenemedi' });
  }
});

// Firma arama endpoint
app.get('/api/firms/search', async (req, res) => {
  try {
    const { cityId, districtId, serviceId, keyword } = req.query;

    let query = `
      SELECT f.*, c.name as city_name, d.name as district_name
      FROM firms f
      JOIN cities c ON f.city_id = c.id
      JOIN districts d ON f.district_id = d.id
      WHERE 1=1
    `;

    const params = [];

    if (cityId) {
      query += ' AND f.city_id = ?';
      params.push(cityId);
    }

    if (districtId) {
      query += ' AND f.district_id = ?';
      params.push(districtId);
    }

    if (keyword) {
      query += ' AND (f.name LIKE ? OR f.description LIKE ?)';
      params.push(`%${keyword}%`, `%${keyword}%`);
    }

    if (serviceId) {
      query += `
        AND f.id IN (
          SELECT fs.firm_id
          FROM firm_services fs
          WHERE fs.service_id = ?
        )
      `;
      params.push(serviceId);
    }

    query += ' ORDER BY f.featured DESC, f.rating DESC';

    const [rows] = await db.execute(query, params);

    // Hizmetleri ekle
    for (const firm of rows) {
      const [serviceRows] = await db.execute(`
        SELECT s.* FROM services s
        JOIN firm_services fs ON s.id = fs.service_id
        WHERE fs.firm_id = ?
      `, [firm.id]);

      firm.services = serviceRows;
    }

    res.json({ firms: rows });
  } catch (error) {
    console.error('Firms search API error:', error);
    res.status(500).json({ error: 'Firmalar aranamadı' });
  }
});

// Firma detay endpoint
app.get('/api/firms/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const [firmRows] = await db.execute(`
      SELECT f.*, c.name as city_name, d.name as district_name
      FROM firms f
      JOIN cities c ON f.city_id = c.id
      JOIN districts d ON f.district_id = d.id
      WHERE f.id = ?
    `, [id]);

    if (firmRows.length === 0) {
      return res.status(404).json({ error: 'Firma bulunamadı' });
    }

    const firm = firmRows[0];

    // Hizmetleri getir
    const [serviceRows] = await db.execute(`
      SELECT s.* FROM services s
      JOIN firm_services fs ON s.id = fs.service_id
      WHERE fs.firm_id = ?
    `, [firm.id]);

    firm.services = serviceRows;

    res.json({ firm });
  } catch (error) {
    console.error('Firm detail API error:', error);
    res.status(500).json({ error: 'Firma detayı yüklenemedi' });
  }
});

// Seed data endpoint
app.post('/api/seed', async (req, res) => {
  try {
    // İller ekle
    const cities = [
      ['İstanbul', 'istanbul'],
      ['Ankara', 'ankara'],
      ['İzmir', 'izmir'],
      ['Bursa', 'bursa'],
      ['Antalya', 'antalya'],
      ['Adana', 'adana'],
      ['Konya', 'konya'],
      ['Gaziantep', 'gaziantep']
    ];

    for (const [name, slug] of cities) {
      await db.execute('INSERT IGNORE INTO cities (name, slug) VALUES (?, ?)', [name, slug]);
    }

    // İlçeler ekle
    const districts = [
      ['Kadıköy', 'kadikoy', 1],
      ['Beşiktaş', 'besiktas', 1],
      ['Şişli', 'sisli', 1],
      ['Üsküdar', 'uskudar', 1],
      ['Çankaya', 'cankaya', 2],
      ['Yenimahalle', 'yenimahalle', 2],
      ['Keçiören', 'kecioren', 2],
      ['Mamak', 'mamak', 2]
    ];

    for (const [name, slug, cityId] of districts) {
      await db.execute('INSERT IGNORE INTO districts (name, slug, city_id) VALUES (?, ?, ?)', [name, slug, cityId]);
    }

    // Hizmetler ekle
    const services = [
      ['Oto Çekici', 'oto-cekici', 'Profesyonel oto çekici hizmetleri'],
      ['Kurtarma', 'kurtarma', 'Araç kurtarma ve taşıma'],
      ['Yol Yardım', 'yol-yardim', '7/24 yol yardım hizmetleri'],
      ['Akü Takviyesi', 'aku-takviyesi', 'Akü bitmesi ve takviye'],
      ['Lastik Tamiri', 'lastik-tamiri', 'Lastik patlaması ve tamir']
    ];

    for (const [name, slug, description] of services) {
      await db.execute('INSERT IGNORE INTO services (name, slug, description) VALUES (?, ?, ?)',
        [name, slug, description]);
    }

    res.json({ message: 'Veritabanı seed data eklendi' });
  } catch (error) {
    console.error('Seed error:', error);
    res.status(500).json({ error: 'Seed data eklenemedi' });
  }
});

// Server başlat
initializeDatabase().then(() => {
  app.listen(PORT, () => {
    console.log(`🚀 OTTO API Server running on port ${PORT}`);
    console.log(`📊 MySQL veritabanı bağlantısı aktif`);
  });
});
