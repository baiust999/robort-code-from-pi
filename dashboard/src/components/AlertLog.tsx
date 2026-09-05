import type { AlertLogEntry } from '../hooks/useControlSocket';

export function AlertLog(props: { alerts: AlertLogEntry[] }) {
  return (
    <div className="flex h-40 flex-col-reverse overflow-y-auto rounded-lg border border-white/10 bg-black/30 p-2 text-xs">
      {[...props.alerts].reverse().map((a) => (
        <div key={a.id} className="border-b border-white/5 py-1 text-white/60">
          <span className="text-white/30">{new Date(a.ts).toLocaleTimeString()}</span> {a.message}
        </div>
      ))}
      {props.alerts.length === 0 && <div className="text-white/30">no events yet</div>}
    </div>
  );
}
