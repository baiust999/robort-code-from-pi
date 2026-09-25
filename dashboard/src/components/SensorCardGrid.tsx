import { DEFAULT_THRESHOLDS, isAlertActive, type TelemetrySnapshot } from '../lib/protocol';

function cardTone(value: number | null, key: string): string {
  if (value === null) return 'border-white/10';
  const limits = DEFAULT_THRESHOLDS[key];
  if (isAlertActive(value, limits, 'crit')) return 'border-red-500/60 bg-red-500/10';
  if (isAlertActive(value, limits, 'warn')) return 'border-amber-500/60 bg-amber-500/10';
  return 'border-white/10';
}

function Card(props: { label: string; value: string; tone: string }) {
  return (
    <div className={`rounded-lg border p-3 ${props.tone}`}>
      <div className="text-xs uppercase tracking-wide text-white/40">{props.label}</div>
      <div className="text-xl font-semibold">{props.value}</div>
    </div>
  );
}

export function SensorCardGrid(props: { telemetry: TelemetrySnapshot | null }) {
  const t = props.telemetry;
  return (
    <div className="grid grid-cols-2 gap-2">
      <Card
        label="Temperature"
        value={t ? `${t.temperature_c.toFixed(1)} °C` : '—'}
        tone={cardTone(t?.temperature_c ?? null, 'temperature_c')}
      />
      <Card label="Humidity" value={t ? `${t.humidity_pct.toFixed(1)} %` : '—'} tone="border-white/10" />
      <Card
        label="Gas"
        value={t ? `${t.gas_ppm} ppm` : '—'}
        tone={cardTone(t?.gas_ppm ?? null, 'gas_ppm')}
      />
      <Card
        label="Range"
        value={t ? `${t.range_cm} cm` : '—'}
        tone={cardTone(t?.range_cm ?? null, 'range_cm')}
      />
      <Card label="Motion" value={t ? (t.motion ? 'detected' : 'clear') : '—'} tone={t?.motion ? 'border-amber-500/60 bg-amber-500/10' : 'border-white/10'} />
    </div>
  );
}
