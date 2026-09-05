import { useEffect, useRef, useState } from 'react';

const KEY_TO_DIR: Record<string, 'F' | 'R' | 'L' | 'G'> = {
  ArrowUp: 'F',
  w: 'F',
  ArrowDown: 'R',
  s: 'R',
  ArrowLeft: 'L',
  a: 'L',
  ArrowRight: 'G',
  d: 'G',
};

export function DriveControl(props: {
  onDrive: (dir: 'F' | 'R' | 'L' | 'G', speed: number) => void;
  onStop: () => void;
  disabled: boolean;
}) {
  const { onDrive, onStop, disabled } = props;
  const [speed, setSpeed] = useState(120);
  const activeDir = useRef<string | null>(null);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const dir = KEY_TO_DIR[e.key];
      if (!dir || disabled || activeDir.current === dir) return;
      activeDir.current = dir;
      onDrive(dir, speed);
    }
    function onKeyUp(e: KeyboardEvent) {
      const dir = KEY_TO_DIR[e.key];
      if (!dir) return;
      if (activeDir.current === dir) {
        activeDir.current = null;
        onStop();
      }
    }
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);
    return () => {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
    };
  }, [onDrive, onStop, speed, disabled]);

  function press(dir: 'F' | 'R' | 'L' | 'G') {
    if (disabled) return;
    onDrive(dir, speed);
  }

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-white/50">Drive</h3>
      <div className="grid w-40 grid-cols-3 gap-1">
        <div />
        <button
          className="rounded bg-white/10 py-2 hover:bg-white/20 disabled:opacity-30"
          disabled={disabled}
          onPointerDown={() => press('F')}
          onPointerUp={onStop}
          onPointerLeave={onStop}
        >
          ▲
        </button>
        <div />
        <button
          className="rounded bg-white/10 py-2 hover:bg-white/20 disabled:opacity-30"
          disabled={disabled}
          onPointerDown={() => press('L')}
          onPointerUp={onStop}
          onPointerLeave={onStop}
        >
          ◀
        </button>
        <button
          className="rounded bg-red-500/30 py-2 font-semibold hover:bg-red-500/50"
          onClick={onStop}
        >
          ■
        </button>
        <button
          className="rounded bg-white/10 py-2 hover:bg-white/20 disabled:opacity-30"
          disabled={disabled}
          onPointerDown={() => press('G')}
          onPointerUp={onStop}
          onPointerLeave={onStop}
        >
          ▶
        </button>
        <div />
        <button
          className="rounded bg-white/10 py-2 hover:bg-white/20 disabled:opacity-30"
          disabled={disabled}
          onPointerDown={() => press('R')}
          onPointerUp={onStop}
          onPointerLeave={onStop}
        >
          ▼
        </button>
        <div />
      </div>
      <label className="flex flex-col gap-1 text-xs text-white/50">
        Speed: {speed}
        <input
          type="range"
          min={0}
          max={180}
          value={speed}
          onChange={(e) => setSpeed(Number(e.target.value))}
        />
      </label>
    </div>
  );
}
