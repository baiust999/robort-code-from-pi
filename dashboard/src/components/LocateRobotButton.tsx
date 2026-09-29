import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

/**
 * Google Maps-style "my location" button: centres the map on the robot's GPS
 * position. Greyed out while there is no fix.
 */
export function LocateRobotButton(props: { position: [number, number] | null }) {
  const map = useMap();
  const [container, setContainer] = useState<HTMLElement | null>(null);

  useEffect(() => {
    // A real Leaflet control, so it stacks with the attribution in the corner
    // instead of overlapping it.
    const control = new L.Control({ position: 'bottomright' });
    control.onAdd = () => {
      const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
      // Clicking the button must not also click or drag the map beneath it.
      L.DomEvent.disableClickPropagation(div);
      return div;
    };
    control.addTo(map);
    setContainer(control.getContainer() ?? null);
    return () => {
      control.remove();
    };
  }, [map]);

  if (!container) return null;
  const { position } = props;

  return createPortal(
    <button
      type="button"
      title={position ? 'Show robot location' : 'No GPS fix'}
      aria-label="Show robot location"
      disabled={!position}
      onClick={() => position && map.flyTo(position, Math.max(map.getZoom(), 17))}
      className="flex h-[34px] w-[34px] items-center justify-center bg-white text-[#2196F3] hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400"
    >
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="4" fill="currentColor" stroke="none" />
        <circle cx="12" cy="12" r="7.5" />
        <path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3" strokeLinecap="round" />
      </svg>
    </button>,
    container,
  );
}
