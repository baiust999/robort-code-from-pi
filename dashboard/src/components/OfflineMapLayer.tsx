import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import type L from 'leaflet';
import { P1_HTTP_BASE } from '../lib/api';

const MAP_URL = `${P1_HTTP_BASE}/maps/area.pmtiles`;

/**
 * Street map read from the map file on the robot, so the map still works on
 * the local network with no internet. It covers only the file's area, drawn over the
 * online OpenStreetMap layer, which still shows everywhere else. If P1 has no
 * map file, nothing is added and the map behaves exactly as before.
 *
 * The map libraries are loaded as a separate chunk after the dashboard is up,
 * so they don't slow its first load over the local network.
 */
export function OfflineMapLayer() {
  const map = useMap();

  useEffect(() => {
    let layer: L.Layer | null = null;
    let cancelled = false;

    (async () => {
      const [{ PMTiles }, { leafletLayer }] = await Promise.all([
        import('pmtiles'),
        import('protomaps-leaflet'),
      ]);
      const archive = new PMTiles(MAP_URL);
      const header = await archive.getHeader();
      if (cancelled) return;
      layer = leafletLayer({
        url: archive,
        flavor: 'light',
        lang: 'en',
        maxDataZoom: header.maxZoom,
        // Only draw inside the file's area; outside it the online map shows.
        bounds: [
          [header.minLat, header.minLon],
          [header.maxLat, header.maxLon],
        ],
        zIndex: 2,
        attribution: 'Offline map: Protomaps, &copy; OpenStreetMap',
      }) as unknown as L.Layer;
      layer.addTo(map);
    })().catch(() => undefined);

    return () => {
      cancelled = true;
      layer?.remove();
    };
  }, [map]);

  return null;
}
