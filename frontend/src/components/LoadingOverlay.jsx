export function LoadingOverlay({ message }) {
  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6">
      <div className="flex items-center gap-4 rounded-xl border border-accent/20 bg-accent-light px-6 py-5">
        <svg className="h-6 w-6 animate-spin text-accent" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <div>
          <p className="text-sm font-semibold text-ink">{message}</p>
          <p className="mt-0.5 text-xs text-ink-muted animate-pulse-soft">
            Assembling context from multiple enterprise sources...
          </p>
        </div>
      </div>
    </div>
  );
}
