import { useEffect, useMemo, useRef, useState } from 'react';
import { useControlSocket } from './hooks/useControlSocket';
import { useWebrtcVideo } from './hooks/useWebrtcVideo';
import { useTalkback } from './hooks/useTalkback';
import { usePersonDetection } from './hooks/usePersonDetection';
import { useRecorder } from './hooks/useRecorder';
import { ConnectionStatusBar } from './components/ConnectionStatusBar';
import { SignalWarningBanner } from './components/SignalWarningBanner';
import { MissionStateIndicator } from './components/MissionStateIndicator';
import { DriveControl } from './components/DriveControl';
import { ServoControl } from './components/ServoControl';
import { EmergencyStop } from './components/EmergencyStop';
import { VideoSurface } from './components/VideoSurface';
import { TalkPanel } from './components/TalkPanel';
import { MapPanel } from './components/MapPanel';
import { SensorCardGrid } from './components/SensorCardGrid';
import { GpsStatusCard } from './components/GpsStatusCard';
import { AlertLog } from './components/AlertLog';
import { ControllerKeyBox } from './components/ControllerKeyBox';
import { MarkVictimButton } from './components/MarkVictimButton';
import { VictimList } from './components/VictimList';
import { describeAuth, deriveMissionState, FW_STATE_DRIVING } from './lib/protocol';
import { loadControllerKey, saveControllerKey } from './lib/controllerKey';

/** At most one "possible person" alert per this long, so a person in view doesn't flood the log. */
const PERSON_ALERT_COOLDOWN_MS = 30_000;

function App() {
  const [controllerKey, setControllerKey] = useState(loadControllerKey);
  // Why the last key was refused; kept after the key itself is dropped.
  const [keyProblem, setKeyProblem] = useState<string | null>(null);
  const changeKey = (key: string | null) => {
    saveControllerKey(key);
    setControllerKey(key);
    setKeyProblem(null);
  };
  const {
    connected,
    role,
    auth,
    retryAfterS,
    telemetry,
    signalLevel,
    lastAckMs,
    alerts,
    pushAlert,
    victimMarks,
    addVictimMark,
    removeVictimMark,
    clearVictimMarks,
    sendMotor,
    sendServo,
    sendStopAll,
  } = useControlSocket(controllerKey);
  const video = useWebrtcVideo(controllerKey);

  // Drop a refused key, or every reconnect would resend it and count toward
  // the robot's lockout.
  useEffect(() => {
    const problem = describeAuth(auth, retryAfterS);
    if (!problem || !controllerKey) return;
    saveControllerKey(null);
    setControllerKey(null);
    setKeyProblem(problem);
  }, [auth, retryAfterS, controllerKey]);
  const talk = useTalkback(video.talkLink);
  const detection = usePersonDetection(video.videoRef, video.connected);
  const recorder = useRecorder(video.remoteStream, video.talkLink, video.connected);

  // Log when a person comes into view, not every frame they stay in it.
  const lastPersonAlert = useRef(0);
  const { personPresent, bestScore } = detection;
  useEffect(() => {
    if (!personPresent || Date.now() - lastPersonAlert.current < PERSON_ALERT_COOLDOWN_MS) return;
    lastPersonAlert.current = Date.now();
    pushAlert(`AI: possible person in view (${Math.round((bestScore ?? 0) * 100)}%)`);
    // bestScore changes every frame; only the rising edge matters.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [personPresent, pushAlert]);

  const missionState = useMemo(
    () =>
      deriveMissionState({
        wsConnected: connected,
        serialOk: telemetry?.serial_ok ?? false,
        videoActive: video.connected,
        lastCmdAckMs: lastAckMs,
        commandActive: telemetry?.fw_state === FW_STATE_DRIVING,
      }),
    [connected, telemetry, lastAckMs, video.connected],
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
        signalDbm={telemetry?.signal_dbm ?? null}
        signalLevel={signalLevel}
      >
        <ControllerKeyBox
          controllerKey={controllerKey}
          onChange={changeKey}
          problem={keyProblem}
        />
      </ConnectionStatusBar>
      <SignalWarningBanner level={signalLevel} signalDbm={telemetry?.signal_dbm ?? null} />
      {/* Top row: video and the readings beside it. Bottom row: one map spanning
          both, filling the rest of the height. The controls span both rows. */}
      <div className="grid flex-1 grid-cols-[22%_52%_26%] grid-rows-[auto_minmax(0,1fr)] gap-3 overflow-hidden p-3">
        <aside className="row-span-2 flex flex-col gap-4 overflow-y-auto rounded-lg border border-white/10 bg-white/5 p-3">
          <MissionStateIndicator state={missionState} />
          <DriveControl onDrive={sendMotor} onStop={sendStopAll} disabled={controlsDisabled} />
          <ServoControl
            pan={telemetry?.pan_angle ?? 90}
            tilt={telemetry?.tilt_angle ?? 90}
            onPan={(angle) => sendServo('pan', angle)}
            onTilt={(angle) => sendServo('tilt', angle)}
            disabled={controlsDisabled}
          />
          <EmergencyStop onStop={sendStopAll} disabled={controlsDisabled} />
          <TalkPanel
            talk={talk}
            linkUp={video.connected}
            isController={!controlsDisabled}
            videoRef={video.videoRef}
            onReply={(rise) => pushAlert(`sound after call-out (+${rise} dB): listen to the robot mic`)}
          />
        </aside>

        <main className="flex flex-col gap-2">
          <VideoSurface video={video} detection={detection} recorder={recorder} />
          <MarkVictimButton
            videoRef={video.videoRef}
            boxes={detection.boxes}
            bestScore={detection.bestScore}
            controllerKey={controllerKey}
            disabled={controlsDisabled}
            onSaved={addVictimMark}
          />
        </main>

        <aside className="flex flex-col gap-3 overflow-y-auto rounded-lg border border-white/10 bg-white/5 p-3">
          <SensorCardGrid telemetry={telemetry} />
          <GpsStatusCard telemetry={telemetry} />
          <VictimList
            marks={victimMarks}
            controllerKey={controllerKey}
            onDeleted={removeVictimMark}
            onNewMission={clearVictimMarks}
          />
          <div className="flex-1">
            <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-white/50">
              Alerts
            </h3>
            <AlertLog alerts={alerts} />
          </div>
        </aside>

        <div className="col-span-2 min-h-0 overflow-hidden rounded-lg border border-white/10">
          <MapPanel telemetry={telemetry} victims={victimMarks} />
        </div>
      </div>
    </div>
  );
}

export default App;
