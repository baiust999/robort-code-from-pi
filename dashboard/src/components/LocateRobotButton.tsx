import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

/**
 * Google Maps-style "my location" button with follow mode. While following,
 * the map keeps the robot centred as new GPS fixes arrive; dragging the map
 * stops following, and clicking the button flies back to the robot and
 * follows again. Following starts on, so a dashboard opened before the first
 * fix moves to the robot once it arrives. Greyed out while there is no fix.
 */
export function LocateRobotButton(props: { position: [number, number] | null }) {
  const map = useMap();
  const [container, setContainer] = useState<HTMLElement | null>(null);
  const [following, setFollowing] = useState(true);

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

    // Only the operator dragging fires dragstart; our own panning doesn't.
    const stopFollowing = () => setFollowing(false);
    map.on('dragstart', stopFollowing);
    return () => {
      map.off('dragstart', stopFollowing);
      control.remove();
    };
  }, [map]);

  // Telemetry arrives 5 times a second but the GPS moves once a second, so
  // depend on the coordinates rather than the array to pan only on a change.
  // Following is read through a ref: turning it on must not pan here, or the
  // pan would cut short the button's own flyTo.
  // Nor may a fix arriving mid-flight, so panning waits for the flyTo to end.
  const followingRef = useRef(following);
  const flyingRef = useRef(false);
  useEffect(() => {
    followingRef.current = following;
  }, [following]);
  const lat = props.position?.[0];
  const lon = props.position?.[1];
  useEffect(() => {
    if (followingRef.current && !flyingRef.current && lat !== undefined && lon !== undefined) {
      map.panTo([lat, lon]);
    }
  }, [map, lat, lon]);

  if (!container) return null;
  const { position } = props;

  let title = 'No GPS fix';
  if (position) title = following ? 'Following robot (drag the map to stop)' : 'Show and follow robot';

  return createPortal(
    <button
      type="button"
      title={title}
      aria-label="Show and follow robot"
      aria-pressed={following}
      disabled={!position}
      onClick={() => {
        if (!position) return;
        setFollowing(true);
        flyingRef.current = true;
        map.once('moveend', () => {
          flyingRef.current = false;
        });
        map.flyTo(position, Math.max(map.getZoom(), 17));
      }}
      className={
        'flex h-[34px] w-[34px] items-center justify-center disabled:cursor-not-allowed disabled:bg-white disabled:text-gray-400 ' +
        (following ? 'bg-[#2196F3] text-white hover:bg-[#1E88E5]' : 'bg-white text-[#2196F3] hover:bg-gray-100')
      }
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
