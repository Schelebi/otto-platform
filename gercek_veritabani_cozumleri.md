# TALİMATLAR VE KODLAR - GERÇEK VERİTABANI ÇÖZÜMLERİ (MOCK DATA YOK)

## 1- İLLER DROPDOWN ANALİZİ - GERÇEK API ÇÖZÜMÜ
### SORUN: İller dropdown'u boş görünüyor, veri gelmiyor
### ELEMENT: <select class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"><option value="">Tüm İller</option></select>
### KABLOLAMA DURUMU: ❌ Veritabanı ile doğru kablolanmamış
### ÇÖZÜM: Gerçek MySQL/MongoDB veritabanı bağlantısı kur

```typescript
// src/services/databaseService.ts - YENİ GERÇEK DB SERVİSİ
import { City, District, Service, Firm } from '../types';

export class DatabaseService {
  private static instance: DatabaseService;
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';
  }

  static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  // GERÇEK VERİTABANI İLLERİ ÇEK
  async getCities(): Promise<City[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cities`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.cities || [];
    } catch (error) {
      console.error('Cities fetch error:', error);
      throw new Error('İller yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // GERÇEK VERİTABANI İLÇELERİ ÇEK
  async getDistricts(cityId: number): Promise<District[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/districts/${cityId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.districts || [];
    } catch (error) {
      console.error('Districts fetch error:', error);
      throw new Error('İlçeler yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // GERÇEK VERİTABANI HİZMETLERİ ÇEK
  async getServices(): Promise<Service[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/services`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.services || [];
    } catch (error) {
      console.error('Services fetch error:', error);
      throw new Error('Hizmetler yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // GERÇEK VERİTABANI FİRMALAR ARA
  async searchFirms(filters: any): Promise<Firm[]> {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });

      const response = await fetch(`${this.baseUrl}/api/firms/search?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.firms || [];
    } catch (error) {
      console.error('Firms search error:', error);
      throw new Error('Firmalar aranamadı. Lütfen bağlantınızı kontrol edin.');
    }
  }

  // GERÇEK VERİTABANI FİRMA DETAYI
  async getFirmDetail(firmId: number): Promise<Firm> {
    try {
      const response = await fetch(`${this.baseUrl}/api/firms/${firmId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.firm;
    } catch (error) {
      console.error('Firm detail error:', error);
      throw new Error('Firma detayı yüklenemedi. Lütfen bağlantınızı kontrol edin.');
    }
  }
}

export default DatabaseService.getInstance();
```

## 2- GERÇEK BACKEND API SERVER - MySQL/MongoDB BAĞLANTILI

```javascript
// server.js - GERÇEK VERİTABANLI API SERVER
const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise'); // veya mongoose için MongoDB
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.API_PORT || 3001;

app.use(cors());
app.use(express.json());

// GERÇEK MYSQL VERİTABANI BAĞLANTISI
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

    // Tabloların varlığını kontrol et
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

// GERÇEK İLLER ENDPOINT
app.get('/api/cities', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM cities ORDER BY name ASC');
    res.json({ cities: rows });
  } catch (error) {
    console.error('Cities API error:', error);
    res.status(500).json({ error: 'İller yüklenemedi' });
  }
});

// GERÇEK İLÇELER ENDPOINT
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

// GERÇEK HİZMETLER ENDPOINT
app.get('/api/services', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM services ORDER BY name ASC');
    res.json({ services: rows });
  } catch (error) {
    console.error('Services API error:', error);
    res.status(500).json({ error: 'Hizmetler yüklenemedi' });
  }
});

// GERÇEK FİRMA ARAMA ENDPOINT
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

// GERÇEK FİRMA DETAY ENDPOINT
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

// VERİTABANI SEED DATA - SADECE İLK KEZ
app.post('/api/seed', async (req, res) => {
  try {
    // İLLER EKLE
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

    // HİZMETLER EKLE
    const services = [
      ['Oto Çekici', 'oto-cekici', 'Profesyonel oto çekici hizmetleri'],
      ['Kurtarma', 'kurtarma', 'Araç kurtarma ve taşım'],
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
```

## 3- GERÇEK VERİTABANI KULLANAN HOOK'LAR

```typescript
// src/hooks/useServices.ts - GERÇEK DB VERSİYONU
import { useState, useCallback, useEffect } from 'react';
import { City, District, Service } from '../types';
import DatabaseService from '../services/databaseService';

export const useServices = () => {
  const [cities, setCities] = useState<City[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadServices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Gerçek veritabanından illeri çek
      const citiesData = await DatabaseService.getCities();
      setCities(citiesData);

      // Gerçek veritabanından hizmetleri çek
      const servicesData = await DatabaseService.getServices();
      setServices(servicesData);

    } catch (err: any) {
      console.error('Services loading error:', err);
      setError(err.message || 'Veriler yüklenemedi');
      setCities([]);
      setServices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDistricts = useCallback(async (cityId: number) => {
    try {
      const districtsData = await DatabaseService.getDistricts(cityId);
      setDistricts(districtsData);
    } catch (err: any) {
      console.error('Districts loading error:', err);
      setError(err.message || 'İlçeler yüklenemedi');
      setDistricts([]);
    }
  }, []);

  useEffect(() => {
    loadServices();
  }, [loadServices]);

  return {
    cities,
    districts,
    services,
    loading,
    error,
    loadDistricts,
    reloadServices: loadServices
  };
};
```

## 4- GERÇEK VERİTABANI KURULUM SCRIPT'İ

```python
# setup_database.py - GERÇEK VERİTABANI KURULUM
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    try:
        # MySQL bağlantı
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Veritabanı oluştur
            cursor.execute("CREATE DATABASE IF NOT EXISTS otto_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ otto_database veritabanı oluşturuldu")

            # Veritabanını seç
            cursor.execute("USE otto_database")

            # Tabloları oluştur
            tables = [
                """
                CREATE TABLE IF NOT EXISTS cities (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                """
                CREATE TABLE IF NOT EXISTS districts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(100) NOT NULL,
                    city_id INT NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES cities(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                """
                CREATE TABLE IF NOT EXISTS services (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                """
                CREATE TABLE IF NOT EXISTS firms (
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,

                """
                CREATE TABLE IF NOT EXISTS firm_services (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    firm_id INT NOT NULL,
                    service_id INT NOT NULL,
                    FOREIGN KEY (firm_id) REFERENCES firms(id) ON DELETE CASCADE,
                    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_firm_service (firm_id, service_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            ]

            for table_query in tables:
                cursor.execute(table_query)
                print("✅ Tablo oluşturuldu")

            # Seed data ekle
            seed_data(cursor)

            connection.commit()
            print("✅ Veritabanı kurulumu tamamlandı")

    except Error as e:
        print(f"❌ Veritabanı hatası: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def seed_data(cursor):
    # İller
    cities = [
        (1, 'İstanbul', 'istanbul'),
        (2, 'Ankara', 'ankara'),
        (3, 'İzmir', 'izmir'),
        (4, 'Bursa', 'bursa'),
        (5, 'Antalya', 'antalya'),
        (6, 'Adana', 'adana'),
        (7, 'Konya', 'konya'),
        (8, 'Gaziantep', 'gaziantep')
    ]

    cursor.executemany("INSERT IGNORE INTO cities (id, name, slug) VALUES (%s, %s, %s)", cities)

    # İlçeler (örnek)
    districts = [
        (1, 'Kadıköy', 'kadikoy', 1),
        (2, 'Beşiktaş', 'besiktas', 1),
        (3, 'Şişli', 'sisli', 1),
        (4, 'Üsküdar', 'uskudar', 1),
        (5, 'Çankaya', 'cankaya', 2),
        (6, 'Yenimahalle', 'yenimahalle', 2),
        (7, 'Keçiören', 'kecioren', 2),
        (8, 'Mamak', 'mamak', 2)
    ]

    cursor.executemany("INSERT IGNORE INTO districts (id, name, slug, city_id) VALUES (%s, %s, %s, %s)", districts)

    # Hizmetler
    services = [
        (1, 'Oto Çekici', 'oto-cekici', 'Profesyonel oto çekici hizmetleri'),
        (2, 'Kurtarma', 'kurtarma', 'Araç kurtarma ve taşıma'),
        (3, 'Yol Yardım', 'yol-yardim', '7/24 yol yardım hizmetleri'),
        (4, 'Akü Takviyesi', 'aku-takviyesi', 'Akü bitmesi ve takviye'),
        (5, 'Lastik Tamiri', 'lastik-tamiri', 'Lastik patlaması ve tamir')
    ]

    cursor.executemany("INSERT IGNORE INTO services (id, name, slug, description) VALUES (%s, %s, %s, %s)", services)

    print("✅ Seed data eklendi")

if __name__ == "__main__":
    create_database()
```

## 5- ENV KONFİGÜRASYONU

```bash
# .env.local - GERÇEK VERİTABANI AYARLARI
VITE_API_BASE_URL=http://localhost:3001
VITE_API_CITIES=http://localhost:3001/api/cities
VITE_API_SERVICES=http://localhost:3001/api/services
VITE_API_SEARCH=http://localhost:3001/api/firms/search
VITE_API_DISTRICTS=http://localhost:3001/api/districts

# VERİTABANI BAĞLANTI BİLGİLERİ
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=otto_database
API_PORT=3001
```

## 6- PAKET KURULUM KOMUTLARI

```bash
# Backend paketleri
npm install express cors mysql2 bcrypt jsonwebtoken dotenv

# Python veritabanı kurulum
pip install mysql-connector-python python-dotenv

# Veritabanını kur
python setup_database.py

# Backend server'ı başlat
node server.js
```

## ÖZET GERÇEK VERİTABANI ÇÖZÜMÜ
| Eleman | Veri Kaynağı | Çözüm | Dosya |
|--------|-------------|-------|-------|
| İller | MySQL cities tablosu | ✅ Gerçek DB | databaseService.ts |
| İlçeler | MySQL districts tablosu | ✅ Gerçek DB | databaseService.ts |
| Hizmetler | MySQL services tablosu | ✅ Gerçek DB | databaseService.ts |
| Firmalar | MySQL firms tablosu | ✅ Gerçek DB | databaseService.ts |
| Detaylar | JOIN sorguları | ✅ Gerçek DB | server.js |

## KURULUM ADIMLARI
1. MySQL/MariaDB kur ve başlat
2. .env.local dosyasını veritabanı bilgileriyle güncelle
3. `python setup_database.py` çalıştır
4. `node server.js` ile backend'i başlat
5. `npm run dev` ile frontend'i başlat
6. Browser'da test et
