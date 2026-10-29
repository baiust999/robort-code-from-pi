import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { TelemetrySnapshot, VictimMark } from '../lib/protocol';
import { fetchGpsTrack, victimSnapshotUrl } from '../lib/api';
import { OfflineMapLayer } from './OfflineMapLayer';
import { LocateRobotButton } from './LocateRobotButton';

const robotIcon = L.divIcon({
  className: '',
  html: '<div style="width:14px;height:14px;border-radius:50%;background:#2196F3;border:2px solid white;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

// A red cross; faded when the mark had no GPS fix and sits at the last known point.
const victimIcon = (exact: boolean) =>
  L.divIcon({
    className: '',
    html: `<div style="width:20px;height:20px;border-radius:50%;background:#dc2626;border:2px solid white;color:white;font:700 14px/16px system-ui;text-align:center;opacity:${exact ? 1 : 0.55}">+</div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
const victimIconExact = victimIcon(true);
const victimIconApprox = victimIcon(false);

function victimPosition(m: VictimMark): [number, number] | null {
  if (m.gps_fix && m.lat !== null && m.lon !== null) return [m.lat, m.lon];
  return m.last_fix;
}

// Center of the offline area.pmtiles bounds, so the dashboard opens on the
// offline map area before a GPS fix arrives.
const DEFAULT_CENTER: [number, number] = [23.46, 91.1495];

// Mirrors MIN_TRACK_STEP_M in pi/p1_control/gps_reader.py.
const MIN_TRACK_STEP_M = 10;

export function MapPanel(props: { telemetry: TelemetrySnapshot | null; victims: VictimMark[] }) {
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
      const point: [number, number] = [t.lat, t.lon];
      setLiveTrack((prev) => {
        // Only add a point once the robot has really moved, so GPS drift
        // around a stationary robot doesn't scribble the line. Telemetry also
        // repeats each 1 Hz fix five times; this drops those duplicates too.
        const last = prev[prev.length - 1];
        if (last && L.latLng(last).distanceTo(point) < MIN_TRACK_STEP_M) return prev;
        return [...prev.slice(-999), point];
      });
    }
  }, [t]);

  const robotPosition: [number, number] | null =
    t?.gps_fix && t.lat !== null && t.lon !== null ? [t.lat, t.lon] : null;
  const position = robotPosition ?? DEFAULT_CENTER;

  return (
    <MapContainer center={position} zoom={17} className="h-full w-full rounded-lg">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      <OfflineMapLayer />
      {recoveredTrack.length > 1 && (
        <Polyline positions={recoveredTrack} pathOptions={{ color: '#90CAF9', weight: 3 }} />
      )}
      {liveTrack.length > 1 && (
        <Polyline positions={liveTrack} pathOptions={{ color: '#2196F3', weight: 3 }} />
      )}
      {props.victims.map((m) => {
        const at = victimPosition(m);
        if (!at) return null;
        return (
          <Marker key={m.id} position={at} icon={m.gps_fix ? victimIconExact : victimIconApprox}>
            <Popup>
              <b>Victim</b> {new Date(m.ts).toLocaleTimeString()}
              <br />
              {m.note || '(no note)'}
              {!m.gps_fix && (
                <>
                  <br />
                  <i>No GPS fix: last known robot position</i>
                </>
              )}
              {m.snapshot && (
                <>
                  <br />
                  <a href={victimSnapshotUrl(m.id)} target="_blank" rel="noreferrer">
                    snapshot
                  </a>
                </>
              )}
            </Popup>
          </Marker>
        );
      })}
      {t?.gps_fix && <Marker position={position} icon={robotIcon} />}
      <LocateRobotButton position={robotPosition} />
    </MapContainer>
  );
}
