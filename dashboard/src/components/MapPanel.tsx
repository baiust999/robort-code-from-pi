import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet';
import L from 'leaflet';
import type { TelemetrySnapshot } from '../lib/protocol';
import { fetchGpsTrack } from '../lib/api';

const robotIcon = L.divIcon({
  className: '',
  html: '<div style="width:14px;height:14px;border-radius:50%;background:#2196F3;border:2px solid white;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const DEFAULT_CENTER: [number, number] = [23.8103, 90.4125];

export function MapPanel(props: { telemetry: TelemetrySnapshot | null }) {
  const t = props.telemetry;
  const [recoveredTrack, setRecoveredTrack] = useState<[number, number][]>([]);
  const [liveTrack, setLiveTrack] = useState<[number, number][]>([]);

  useEffect(() => {
    fetchGpsTrack()
      .then((track) => {
        setRecoveredTrack(track.coordinates.map(([lon, lat]) => [lat, lon]));
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (t?.gps_fix && t.lat !== null && t.lon !== null) {
      setLiveTrack((prev) => [...prev.slice(-999), [t.lat as number, t.lon as number]]);
    }
  }, [t]);

  const position: [number, number] =
    t?.gps_fix && t.lat !== null && t.lon !== null ? [t.lat, t.lon] : DEFAULT_CENTER;

  return (
    <MapContainer center={position} zoom={17} className="h-full w-full rounded-lg">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      {recoveredTrack.length > 1 && (
        <Polyline positions={recoveredTrack} pathOptions={{ color: '#90CAF9', weight: 3 }} />
      )}
      {liveTrack.length > 1 && (
        <Polyline positions={liveTrack} pathOptions={{ color: '#2196F3', weight: 3 }} />
      )}
      {t?.gps_fix && <Marker position={position} icon={robotIcon} />}
    </MapContainer>
  );
}
