export function EmergencyStop(props: { onStop: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={props.onStop}
      disabled={props.disabled}
      title={props.disabled ? 'Only the controller can stop the robot' : undefined}
      className="w-full rounded-lg border-2 border-red-500 bg-red-600/80 py-4 text-lg font-bold tracking-wide text-white hover:bg-red-500 active:bg-red-700 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-red-600/80"
    >
      EMERGENCY STOP
    </button>
  );
}
