export function EmptyState() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <div className="rounded-2xl border border-dashed border-surface-border bg-white px-6 py-16 text-center shadow-card">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-surface-muted text-2xl">
          📋
        </div>
        <p className="mx-auto mt-5 max-w-md text-base text-ink-muted">
          Enter a meeting request above to generate an AI-powered meeting brief.
        </p>
        <p className="mt-2 text-sm text-ink-faint">
          Try: &ldquo;Prepare me for Globex meeting&rdquo;
        </p>
      </div>
    </section>
  );
}
