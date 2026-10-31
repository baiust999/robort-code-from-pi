import { createRoot } from 'react-dom/client';
import { useEffect, useRef, useState } from 'react';
import { useTalkback } from '/home/pi/robot/dashboard/src/hooks/useTalkback';
import { TalkPanel } from '/home/pi/robot/dashboard/src/components/TalkPanel';

// Stands in for the WebRTC data channel, carried over a WebSocket to the real ScreenHub.
class WsChannel extends EventTarget {
  readyState = 'connecting';
  ws = new WebSocket('ws://127.0.0.1:18190/op');
  constructor() {
    super();
    this.ws.onopen = () => { this.readyState = 'open'; this.dispatchEvent(new Event('open')); };
    this.ws.onmessage = (e) => this.dispatchEvent(new MessageEvent('message', { data: e.data }));
  }
  send(d: string) { this.ws.send(d); }
}
const sender = { replaceTrack: async () => {} };
function App() {
  const [link] = useState(() => ({ channel: new WsChannel(), audioSender: sender, videoSender: sender }) as any);
  const talk = useTalkback(link);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  useEffect(() => { (window as any).talk = talk; });
  // The real TalkPanel, as App.tsx renders it.
  return <TalkPanel talk={talk} linkUp isController videoRef={videoRef} controllerKey="browser-test-key" />;
}
createRoot(document.getElementById('root')!).render(<App />);
