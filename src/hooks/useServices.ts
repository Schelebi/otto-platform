import { useState, useCallback, useEffect } from 'react';
import { City, Service } from '../types';
import { DatabaseService } from '../services/databaseService';

export const useServices = () => {
  const [cities, setCities] = useState<City[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadInitial = useCallback(async () => {
    try {
      setLoading(true);
      const db = DatabaseService.getInstance();
      const [citiesData, servicesData] = await Promise.all([
        db.getCities(),
        db.getServices()
      ]);
      setCities(citiesData);
      setServices(servicesData);
      setError(null);
    } catch (err) {
      console.error('Initial load error:', err);
      setError('API bağlantısı yok – demo veriler kullanılabilir');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitial();
  }, [loadInitial]);

  return {
    cities,
    services,
    loading,
    error,
    reload: loadInitial
  };
};
