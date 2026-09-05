import { useMemo } from 'react';
import { useControlSocket } from './hooks/useControlSocket';
import { ConnectionStatusBar } from './components/ConnectionStatusBar';
import { MissionStateIndicator } from './components/MissionStateIndicator';
import { DriveControl } from './components/DriveControl';
import { ServoControl } from './components/ServoControl';
import { EmergencyStop } from './components/EmergencyStop';
import { VideoSurface } from './components/VideoSurface';
import { MapPanel } from './components/MapPanel';
import { SensorCardGrid } from './components/SensorCardGrid';
import { GpsStatusCard } from './components/GpsStatusCard';
import { AlertLog } from './components/AlertLog';
import { deriveMissionState, FW_STATE_STOPPED } from './lib/protocol';

function App() {
  const { connected, role, telemetry, lastAckMs, alerts, sendMotor, sendServo, sendStopAll } =
    useControlSocket();

  const missionState = useMemo(
    () =>
      deriveMissionState({
        wsConnected: connected,
        serialOk: telemetry?.serial_ok ?? false,
        videoActive: true,
        meshOk: true,
        lastCmdAckMs: lastAckMs,
        commandActive: telemetry
          ? telemetry.fw_state !== FW_STATE_STOPPED && telemetry.motion === 1
          : false,
      }),
    [connected, telemetry, lastAckMs],
  );

  const controlsDisabled = !connected || role !== 'controller';

  return (
    <div className="flex h-screen flex-col bg-neutral-950 text-white">
      <ConnectionStatusBar
        connected={connected}
        role={role}
        missionState={missionState}
        serialOk={telemetry?.serial_ok ?? false}
        gpsFix={telemetry?.gps_fix ?? false}
      />
      <div className="grid flex-1 grid-cols-[22%_52%_26%] gap-3 overflow-hidden p-3">
        <aside className="flex flex-col gap-4 overflow-y-auto rounded-lg border border-white/10 bg-white/5 p-3">
          <MissionStateIndicator state={missionState} />
          <DriveControl onDrive={sendMotor} onStop={sendStopAll} disabled={controlsDisabled} />
          <ServoControl
            pan={telemetry?.pan_angle ?? 90}
            tilt={telemetry?.tilt_angle ?? 90}
            onPan={(angle) => sendServo('pan', angle)}
            onTilt={(angle) => sendServo('tilt', angle)}
            disabled={controlsDisabled}
          />
          <EmergencyStop onStop={sendStopAll} />
        </aside>

        <main className="flex flex-col gap-3 overflow-hidden">
          <VideoSurface />
          <div className="flex-1 overflow-hidden rounded-lg border border-white/10">
            <MapPanel telemetry={telemetry} />
          </div>
        </main>

        <aside className="flex flex-col gap-3 overflow-y-auto rounded-lg border border-white/10 bg-white/5 p-3">
          <SensorCardGrid telemetry={telemetry} />
          <GpsStatusCard telemetry={telemetry} />
          <div className="flex-1">
            <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-white/50">
              Alerts
            </h3>
            <AlertLog alerts={alerts} />
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;
