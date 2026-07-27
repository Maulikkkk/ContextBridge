export function ErrorAlert({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6">
      <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-5 shadow-card">
        <svg className="mt-0.5 h-5 w-5 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div className="flex-1">
          <p className="text-sm font-semibold text-red-800">{message}</p>
          {!message.includes('ingest') && !message.includes('502') && !message.includes('backend') && (
            <p className="mt-1 text-xs text-red-600">
              Ensure the backend is reachable and meeting notes are ingested via POST /ingest.
            </p>
          )}
        </div>
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            className="text-red-400 transition-colors hover:text-red-600"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
