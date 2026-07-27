export function SearchSection({ query, onQueryChange, onSubmit, loading, disabled }) {
  return (
    <section className="mx-auto max-w-6xl px-4 sm:px-6">
      <div className="rounded-2xl border border-surface-border bg-white p-6 shadow-card sm:p-8">
        <label htmlFor="meeting-query" className="block text-sm font-medium text-ink">
          Meeting preparation query
        </label>
        <input
          id="meeting-query"
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSubmit()}
          disabled={disabled}
          placeholder="Prepare me for tomorrow's Acme meeting"
          className="mt-3 w-full rounded-xl border border-surface-border bg-surface-muted px-4 py-4 text-base text-ink placeholder:text-ink-faint transition-colors focus:border-accent focus:bg-white focus:outline-none focus:ring-2 focus:ring-accent/20 disabled:cursor-not-allowed disabled:opacity-60"
        />
        <div className="mt-5 flex items-center justify-between gap-4">
          <p className="text-xs text-ink-faint">
            Parses client and date, retrieves context, ranks notes, builds package, generates brief.
          </p>
          <button
            type="button"
            onClick={onSubmit}
            disabled={disabled || !query.trim()}
            className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-accent-hover focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate Meeting Brief
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}
