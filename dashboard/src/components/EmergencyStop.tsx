export function EmergencyStop(props: { onStop: () => void }) {
  return (
    <button
      onClick={props.onStop}
      className="w-full rounded-lg border-2 border-red-500 bg-red-600/80 py-4 text-lg font-bold tracking-wide text-white hover:bg-red-500 active:bg-red-700"
    >
      EMERGENCY STOP
    </button>
  );
}
