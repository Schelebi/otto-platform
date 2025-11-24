import { useState, useEffect } from 'react';
import { Firm, SearchFilters } from '../types';
import { DatabaseService } from '../services/databaseService';

export function useFetchFirms(filters: SearchFilters) {
  const [firms, setFirms] = useState<Firm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const db = DatabaseService.getInstance();
        const data = await db.searchFirms(filters);
        if (!alive) return;
        setFirms(data);
        setError(null);
      } catch (err) {
        console.error('Firms fetch error:', err);
        if (alive) {
          setFirms([]);
          setError('Firmalar yüklenemedi.');
        }
      } finally {
        alive && setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [filters.cityId, filters.districtId, filters.serviceId, filters.keyword]);

  return { firms, loading, error };
}
