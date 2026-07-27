import { useState, useEffect } from 'react';

export function ContextEnvelope({ data, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (data) setOpen(true);
  }, [data]);

  if (!data) return null;

  const json = JSON.stringify(data, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <section className="mx-auto max-w-6xl px-4 pb-12 sm:px-6">
      <div className="overflow-hidden rounded-xl border border-surface-border bg-white shadow-card">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="flex w-full items-center justify-between px-6 py-5 text-left transition-colors hover:bg-surface-muted"
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">{open ? '▼' : '▶'}</span>
            <div>
              <span className="text-sm font-semibold text-ink">View Context Envelope</span>
              <p className="mt-0.5 text-xs text-ink-faint">
                The structured context package sent to the LLM — inspect what the model received
              </p>
            </div>
            <span className="ml-2 rounded-full bg-accent-light px-2.5 py-0.5 text-xs font-medium text-accent">
              JSON
            </span>
          </div>
          <svg
            className={`h-5 w-5 shrink-0 text-ink-faint transition-transform ${open ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {open && (
          <div className="border-t border-surface-border">
            <div className="flex items-center justify-between border-b border-slate-700 bg-slate-800 px-4 py-2.5">
              <span className="font-mono text-xs font-medium text-slate-400">context_package</span>
              <button
                type="button"
                onClick={handleCopy}
                className="rounded-md bg-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 transition-colors hover:bg-slate-600"
              >
                {copied ? '✓ Copied!' : 'Copy'}
              </button>
            </div>
            <pre className="max-h-[28rem] overflow-auto bg-slate-900 p-5 font-mono text-xs leading-relaxed text-slate-300">
              {json}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}
