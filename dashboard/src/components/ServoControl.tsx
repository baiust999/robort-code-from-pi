export function ServoControl(props: {
  pan: number;
  tilt: number;
  onPan: (angle: number) => void;
  onTilt: (angle: number) => void;
  disabled: boolean;
}) {
  const { pan, tilt, onPan, onTilt, disabled } = props;
  return (
    <div className="space-y-2">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-white/50">Camera</h3>
      <label className="flex flex-col gap-1 text-xs text-white/50">
        Pan: {pan}°
        <input
          type="range"
          min={0}
          max={180}
          value={pan}
          disabled={disabled}
          onChange={(e) => onPan(Number(e.target.value))}
        />
      </label>
      <label className="flex flex-col gap-1 text-xs text-white/50">
        Tilt: {tilt}°
        <input
          type="range"
          min={0}
          max={180}
          value={tilt}
          disabled={disabled}
          onChange={(e) => onTilt(Number(e.target.value))}
        />
      </label>
    </div>
  );
}
