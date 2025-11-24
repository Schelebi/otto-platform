// 1) KOD ADI:
// useGeoLocation (Gerçek Konum Hook)

// 2) KOD YOLU (GÖRELI):
// src/hooks/useGeoLocation.ts

// 3) KODUN AMACI (5 MADDE):
// - Tarayıcıdan gerçek konum almayı standardize etmek.
// - Konum hatalarını sınıflandırıp UI’ya aktarmak.
// - L1–L2–L3 TRY ile konum akışını çökmez hale getirmek.
// - HomePage “Konumumu Kullan” için hazır altyapı sağlamak.
// - Konum izleme (watch) desteğiyle yakın firma senaryosunu güçlendirmek.

// 4) KODLA İLGİLİ TÜM REVİZYONLAR:
// - Yeni hook oluşturuldu.
// - Permission/timeout/unavailable sınıflandırması eklendi.
// - request() tetikleyici fonksiyon eklendi.
// - watchPosition opsiyon desteği eklendi.

// 5) KODLA İLGİLİ TALİMATLARIN TÜMÜ KODLANDI:
// - Üç katmanlı TRY zorunluluğu uygulandı.
// - Akış durmaz, hata loglanır prensibi sağlandı.

import { useCallback, useEffect, useRef, useState } from "react";
import { Coordinates } from "../types";

type GeoErrorCode = "PERMISSION_DENIED" | "POSITION_UNAVAILABLE" | "TIMEOUT" | "UNKNOWN";

interface GeoState {
  position: Coordinates | null;
  error: { code: GeoErrorCode; message: string } | null;
  isSupported: boolean;
  isLoading: boolean;
  request: () => void;
}

export const useGeoLocation = (watch: boolean = false): GeoState => {
  const [position, setPosition] = useState<Coordinates | null>(null);
  const [error, setError] = useState<GeoState["error"]>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const isSupported =
    typeof navigator !== "undefined" && !!navigator.geolocation;

  const watchIdRef = useRef<number | null>(null);

  const classifyError = (err: GeolocationPositionError): GeoState["error"] => {
    switch (err.code) {
      case err.PERMISSION_DENIED:
        return { code: "PERMISSION_DENIED", message: "Konum izni reddedildi." };
      case err.POSITION_UNAVAILABLE:
        return { code: "POSITION_UNAVAILABLE", message: "Konum alınamıyor." };
      case err.TIMEOUT:
        return { code: "TIMEOUT", message: "Konum isteği zaman aşımına uğradı." };
      default:
        return { code: "UNKNOWN", message: "Bilinmeyen konum hatası." };
    }
  };

  const request = useCallback(() => {
    // L1: global hook try
    try {
      if (!isSupported) {
        setError({ code: "UNKNOWN", message: "Tarayıcı konumu desteklemiyor." });
        return;
      }

      setIsLoading(true);
      setError(null);

      // L2: operational geolocation try
      try {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            // L3: record-level coords try
            try {
              const coords = {
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
              };
              setPosition(coords);
            } catch (e) {
              console.error("[L3][useGeoLocation] coords parse hatası", e);
              setError({ code: "UNKNOWN", message: "Konum verisi bozuk geldi." });
            } finally {
              setIsLoading(false);
            }
          },
          (err) => {
            console.warn("[L2][useGeoLocation] geolocation hata", err);
            setError(classifyError(err));
            setIsLoading(false);
          },
          { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 }
        );
      } catch (opErr) {
        console.error("[L2][useGeoLocation] getCurrentPosition çağrı hatası", opErr);
        setError({ code: "UNKNOWN", message: "Konum çağrısı başarısız." });
        setIsLoading(false);
      }
    } catch (globalErr) {
      console.error("[L1][useGeoLocation] kritik hata", globalErr);
      setError({ code: "UNKNOWN", message: "Kritik konum hatası." });
      setIsLoading(false);
    }
  }, [isSupported]);

  useEffect(() => {
    if (!watch || !isSupported) return;

    // L1 watch global try
    try {
      setIsLoading(true);
      watchIdRef.current = navigator.geolocation.watchPosition(
        (pos) => {
          try {
            setPosition({
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
            });
          } catch (e) {
            console.error("[L3][useGeoLocation] watch coords hatası", e);
          } finally {
            setIsLoading(false);
          }
        },
        (err) => {
          setError(classifyError(err));
          setIsLoading(false);
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 }
      );
    } catch (e) {
      console.error("[L1][useGeoLocation] watchPosition kritik hata", e);
      setIsLoading(false);
    }

    return () => {
      if (watchIdRef.current != null) {
        try {
          navigator.geolocation.clearWatch(watchIdRef.current);
        } catch (e) {
          console.warn("[L2][useGeoLocation] clearWatch hata", e);
        }
      }
    };
  }, [watch, isSupported]);

  return { position, error, isSupported, isLoading, request };
};
