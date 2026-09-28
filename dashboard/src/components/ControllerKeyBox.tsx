import { useState, type FormEvent } from 'react';

/** Enter or forget the controller key; `problem` explains a failed check. */
export function ControllerKeyBox(props: {
  controllerKey: string | null;
  onChange: (key: string | null) => void;
  problem: string | null;
}) {
  const { controllerKey, onChange, problem } = props;
  const [draft, setDraft] = useState('');

  function submit(e: FormEvent) {
    e.preventDefault();
    const key = draft.trim();
    if (!key) return;
    onChange(key);
    setDraft('');
  }

  return (
    <div className="ml-auto flex items-center gap-2">
      {problem && <span className="text-xs font-medium text-red-400">{problem}</span>}
      {controllerKey && !problem ? (
        <button
          type="button"
          onClick={() => onChange(null)}
          className="rounded border border-white/20 px-2 py-0.5 text-xs text-white/70 hover:bg-white/10"
        >
          Forget key
        </button>
      ) : (
        <form onSubmit={submit} className="flex items-center gap-1">
          <input
            type="password"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Controller key"
            autoComplete="off"
            aria-label="Controller key"
            className="w-32 rounded border border-white/20 bg-black/40 px-2 py-0.5 text-xs"
          />
          <button
            type="submit"
            disabled={!draft.trim()}
            className="rounded bg-sky-600 px-2 py-0.5 text-xs font-semibold disabled:opacity-40"
          >
            Unlock
          </button>
        </form>
      )}
    </div>
  );
}
