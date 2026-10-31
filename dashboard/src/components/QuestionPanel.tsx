import { useEffect, useState, type FormEvent } from 'react';
import {
  QUESTION_OPTION_MAX,
  QUESTION_OPTIONS_MAX,
  QUESTION_OPTIONS_MIN,
  SCREEN_TEXT_MAX,
  type QuestionStatus,
  type TalkbackState,
} from '../hooks/useTalkback';

const formatRemaining = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

/** Ticks once a second while the question waits, counting down from P2's figure. */
function useRemaining(question: QuestionStatus | null): number | null {
  const [now, setNow] = useState(() => Date.now());
  const waiting = question?.status === 'waiting';
  useEffect(() => {
    if (!waiting) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [waiting]);
  if (!waiting || question.remainingS === null) return null;
  return Math.max(0, question.remainingS - (now - question.receivedAt) / 1000);
}

function QuestionResult({ question }: { question: QuestionStatus }) {
  const remaining = useRemaining(question);
  if (question.status === 'cleared') return null;
  return (
    <div className="rounded border border-white/10 bg-black/30 px-2 py-1 text-xs">
      <div className="truncate text-white/60" title={question.text}>
        “{question.text}”
      </div>
      {question.status === 'waiting' && (
        <div className="text-white/50">
          Waiting for answer…{remaining !== null && ` ${formatRemaining(remaining)} left`}
        </div>
      )}
      {question.status === 'answered' && question.answer !== null && (
        <div className="text-base font-semibold text-green-400">Answer: {question.options[question.answer]}</div>
      )}
      {question.status === 'expired' && <div className="text-amber-300">No answer (5 min)</div>}
    </div>
  );
}

/**
 * Ask the victim a question with 2–4 answer buttons on the robot screen, for
 * someone who can't speak. Nothing is kept: each question is typed fresh and
 * replaces the last; P2 takes it off the screen after 5 minutes unanswered.
 */
export function QuestionPanel(props: { talk: TalkbackState; blocked: boolean }) {
  const { talk, blocked } = props;
  const [text, setText] = useState('');
  const [options, setOptions] = useState<string[]>(['', '']);

  const filled = options.filter((o) => o.trim()).length;
  const ready = text.trim() !== '' && filled >= QUESTION_OPTIONS_MIN;
  const waiting = talk.question?.status === 'waiting';

  function submit(e: FormEvent) {
    e.preventDefault();
    if (talk.askQuestion(text, options)) {
      setText('');
      setOptions(['', '']);
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-1 border-t border-white/10 pt-2">
      <span className="text-xs text-white/50">Ask a question (victim taps an answer)</span>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        maxLength={SCREEN_TEXT_MAX}
        disabled={blocked}
        placeholder="Question, e.g. Are you hurt?"
        className="w-full rounded border border-white/20 bg-black/40 px-2 py-1 disabled:opacity-40"
      />
      {options.map((option, i) => (
        <div key={i} className="flex gap-1">
          <input
            value={option}
            onChange={(e) => setOptions(options.map((o, j) => (j === i ? e.target.value : o)))}
            maxLength={QUESTION_OPTION_MAX}
            disabled={blocked}
            placeholder={`Answer ${i + 1}${i === 0 ? ', e.g. Yes' : i === 1 ? ', e.g. No' : ''}`}
            className="min-w-0 flex-1 rounded border border-white/20 bg-black/40 px-2 py-1 disabled:opacity-40"
          />
          {i >= QUESTION_OPTIONS_MIN && (
            <button
              type="button"
              disabled={blocked}
              onClick={() => setOptions(options.filter((_, j) => j !== i))}
              title="Remove this answer"
              className="rounded bg-white/10 px-2 hover:bg-white/20 disabled:opacity-40"
            >
              ✕
            </button>
          )}
        </div>
      ))}
      {options.length < QUESTION_OPTIONS_MAX && (
        <button
          type="button"
          disabled={blocked}
          onClick={() => setOptions([...options, ''])}
          className="self-start rounded px-2 py-0.5 text-xs text-sky-300 hover:bg-white/10 disabled:opacity-40"
        >
          + Add answer
        </button>
      )}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={blocked || !ready}
          className="flex-1 rounded bg-sky-600 px-3 py-1 font-semibold disabled:opacity-40"
        >
          {waiting ? 'Replace question' : 'Send question'}
        </button>
        <button
          type="button"
          disabled={blocked || !talk.question}
          onClick={talk.clearQuestion}
          className="rounded bg-white/10 px-4 py-1 hover:bg-white/20 disabled:opacity-40"
        >
          Clear
        </button>
      </div>
      {talk.question && <QuestionResult key={talk.question.id} question={talk.question} />}
    </form>
  );
}
