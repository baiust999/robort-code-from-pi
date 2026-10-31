import { createRoot } from 'react-dom/client';
import { useEffect, useState } from 'react';
import { useTalkback } from '/home/pi/robot/dashboard/src/hooks/useTalkback';
import { QuestionPanel } from '/home/pi/robot/dashboard/src/components/QuestionPanel';

// Stands in for the WebRTC data channel: same send/readyState/message events,
// carried over a WebSocket to the real ScreenHub in bridge.py.
class WsChannel extends EventTarget {
  readyState = 'connecting';
  ws = new WebSocket('ws://127.0.0.1:18090/op');
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
  useEffect(() => { (window as any).talk = talk; });
  return <QuestionPanel talk={talk} blocked={false} />;
}
createRoot(document.getElementById('root')!).render(<App />);
