
import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.API_PORT || 3001;

app.use(cors());
app.use(express.json());

// Mock data
const mockCities = [
  { id: 1, name: 'İstanbul', slug: 'istanbul' },
  { id: 2, name: 'Ankara', slug: 'ankara' },
  { id: 3, name: 'İzmir', slug: 'izmir' }
];

const mockServices = [
  { id: 1, name: 'Oto Çekici', slug: 'oto-cekici' },
  { id: 2, name: 'Kurtarıcı', slug: 'kurtarici' },
  { id: 3, name: 'Yardımcı', slug: 'yardimci' }
];

const mockFirms = [
  { id: 1, name: 'Anlaşılan Oto Çekici', city: 'İstanbul', phone: '05551234567' },
  { id: 2, name: 'Hızlı Kurtarıcı', city: 'Ankara', phone: '05559876543' }
];

// API endpoints
app.get('/api/cities', (req, res) => {
  res.json(mockCities);
});

app.get('/api/services', (req, res) => {
  res.json(mockServices);
});

app.get('/api/search', (req, res) => {
  const { il, kelime } = req.query;
  const results = mockFirms.filter(firm =>
    firm.city.toLowerCase().includes(il?.toLowerCase() || '') &&
    firm.name.toLowerCase().includes(kelime?.toLowerCase() || '')
  );
  res.json(results);
});

app.get('/api/districts', (req, res) => {
  const { il } = req.query;
  res.json([]);
});

app.listen(PORT, () => {
  console.log(`Local API server running on port ${PORT}`);
});
