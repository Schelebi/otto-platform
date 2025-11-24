import { useState, useEffect } from 'react';
import { DatabaseService } from '../services/databaseService';
import { Firm } from '../types';

const dbService = DatabaseService.getInstance();

export const useFirmsByCity = (selectedCity: string | null) => {
  const [firms, setFirms] = useState<Firm[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedCity) {
      setFirms([]);
      setError(null);
      return;
    }

    const fetchFirmsByCity = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log('🔍 Şehre göre firma araması:', selectedCity);
        const cityFirms = await dbService.getFirmsByCity(selectedCity);
        console.log(`✅ ${selectedCity} için ${cityFirms.length} firma bulundu`);
        setFirms(cityFirms);
      } catch (err) {
        console.error('❌ Şehre göre firma arama hatası:', err);
        setError(err instanceof Error ? err.message : 'Firmalar yüklenemedi');
        setFirms([]);
      } finally {
        setLoading(false);
      }
    };

    fetchFirmsByCity();
  }, [selectedCity]);

  return { firms, loading, error };
};
