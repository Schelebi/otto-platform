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


    # Örnek firmalar
    firms = [
        (1, 'Anadolu Çekici', '7/24 profesyonel çekici hizmeti', '+905321234567', '+905321234567', 'info@anadolu.com', 'İstanbul Kadıköy', 1, 1, 41.0285, 28.9652, 4.5, 127, True, True, '24/7', 'www.anadolu.com', 2015),
        (2, 'Başkurt Oto', 'Ankara merkezli kurtarma hizmeti', '+905327654321', '+905327654321', 'info@baskurt.com', 'Ankara Çankaya', 2, 5, 39.9255, 32.8661, 4.3, 89, True, False, '08:00-22:00', 'www.baskurt.com', 2018),
        (3, 'Ege Çekici', 'İzmir ve çevresi yol yardım', '+905335551234', '+905335551234', 'ege@cekici.com', 'İzmir Konak', 3, 9, 38.4237, 27.1428, 4.7, 203, True, True, '24/7', 'www.ege.com', 2012)
    ]


    cursor.executemany("""
        INSERT IGNORE INTO firms (id, name, description, phone, whatsapp, email, address, city_id, district_id, latitude, longitude, rating, reviews, verified, featured, working_hours, website, established)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, firms)


    # Firma hizmetleri
    firm_services = [
        (1, 1), (1, 2), (1, 3),  # Anadolu Çekici
        (2, 1), (2, 3), (2, 4),  # Başkurt Oto
        (3, 1), (3, 2), (3, 5)   # Ege Çekici
    ]


    cursor.executemany("INSERT IGNORE INTO firm_services (firm_id, service_id) VALUES (%s, %s)", firm_services)


    print("✅ Seed data eklendi")


if __name__ == "__main__":
    create_database()
