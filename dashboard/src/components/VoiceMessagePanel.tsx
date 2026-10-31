import type { TalkbackState } from '../hooks/useTalkback';
import { VOICE_MAX_S, useVoiceMessage } from '../hooks/useVoiceMessage';

const fmt = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

/**
 * Record a message once; the robot repeats it on its speaker until Stop Play,
 * even if this dashboard loses its link meanwhile. It doesn't take the robot
 * screen (floor), and live "Hold to talk" pauses it until released.
 */
export function VoiceMessagePanel(props: {
  talk: TalkbackState;
  controllerKey: string | null;
  /** Link down or not the controller. */
  disabled: boolean;
}) {
  const { talk, controllerKey, disabled } = props;
  const vm = useVoiceMessage(talk, controllerKey);
  const robotHasClip = talk.voice?.hasClip === true;
  const playing = talk.voice?.playing === true;
  const canPlay = vm.previewUrl !== null || robotHasClip;

  return (
    <div
      className={`flex flex-col gap-2 rounded border p-2 ${
        playing ? 'border-red-500/60 bg-red-500/10' : 'border-white/10'
      }`}
    >
      <div className="flex items-center justify-between text-xs">
        <span className="text-white/50">Voice message (repeats on robot)</span>
        {playing && <span className="font-semibold text-red-300">🔁 Repeating on robot speaker</span>}
      </div>

      <div className="grid grid-cols-3 gap-1">
        <button
          type="button"
          disabled={disabled || !talk.mediaDevicesAvailable || vm.busy || playing}
          onClick={vm.recording ? vm.stopRecording : vm.startRecording}
          title={`Record up to ${VOICE_MAX_S} s from your mic`}
          className={`rounded px-2 py-1.5 text-xs font-semibold disabled:opacity-40 ${
            vm.recording ? 'bg-red-600 text-white' : 'bg-white/10 hover:bg-white/20'
          }`}
        >
          {vm.recording ? `⏹ Stop ${fmt(vm.elapsedS)}` : '🎙 Record Voice'}
        </button>

        <button
          type="button"
          disabled={disabled || vm.recording || vm.busy || (!playing && !canPlay)}
          onClick={playing ? vm.stopPlay : vm.startPlay}
          className={`rounded px-2 py-1.5 text-xs font-semibold disabled:opacity-40 ${
            playing ? 'bg-red-600 text-white' : 'bg-green-700 text-white hover:bg-green-600'
          }`}
        >
          {vm.busy ? 'Sending…' : playing ? '⏹ Stop Play' : '▶ Start Play'}
        </button>

        <button
          type="button"
          disabled={disabled || vm.busy || (!vm.previewUrl && !robotHasClip && !vm.recording)}
          onClick={vm.clear}
          className="rounded bg-white/10 px-2 py-1.5 text-xs hover:bg-white/20 disabled:opacity-40"
        >
          🗑 Clear Voice
        </button>
      </div>

      {vm.previewUrl && !vm.recording && (
        // Preview on this laptop only; the robot plays it on Start Play.
        <audio src={vm.previewUrl} controls className="h-8 w-full" />
      )}

      <p className="text-xs text-white/40">
        {vm.recording
          ? `Recording… stops by itself at ${fmt(VOICE_MAX_S)}.`
          : robotHasClip && !vm.uploaded
            ? vm.previewUrl
              ? 'The robot holds an older message; Start Play sends this new one.'
              : `Robot has a message loaded (${talk.voice?.durationS ?? '?'} s).`
            : robotHasClip
              ? `On the robot (${talk.voice?.durationS ?? '?'} s). Hold to talk pauses it.`
              : vm.previewUrl
                ? 'Recorded. Listen above, then Start Play.'
                : 'Record a message, e.g. "Help is coming, stay where you are."'}
      </p>
    </div>
  );
}
