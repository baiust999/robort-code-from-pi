import type { TelemetrySnapshot } from '../lib/protocol';

export function GpsStatusCard(props: { telemetry: TelemetrySnapshot | null }) {
  const t = props.telemetry;
  return (
    <div className="rounded-lg border border-white/10 p-3 text-sm">
      <div className="text-xs uppercase tracking-wide text-white/40">GPS</div>
      {t?.gps_fix ? (
        <div className="mt-1 space-y-0.5">
          <div>
            {t.lat?.toFixed(6)}, {t.lon?.toFixed(6)}
          </div>
          <div className="text-white/50">{t.gps_sats} satellites</div>
        </div>
      ) : (
        <div className="mt-1 text-white/50">no fix</div>
      )}
    </div>
  );
}
