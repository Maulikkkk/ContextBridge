const features = [
  {
    emoji: '📅',
    title: 'Multi-source Context',
    description: 'Calendar, CRM, tasks, and notes unified into one layer.',
  },
  {
    emoji: '🔍',
    title: 'Semantic Retrieval',
    description: 'Vector search finds the most relevant meeting history.',
  },
  {
    emoji: '🤖',
    title: 'AI Meeting Preparation',
    description: 'Structured context powers auditable meeting briefs.',
  },
];

export function Hero() {
  return (
    <section className="border-b border-surface-border bg-white">
      <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-20">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-surface-border bg-surface-muted px-4 py-1.5 text-xs font-medium text-ink-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            FastAPI + ChromaDB + Gemini
          </div>

          <h1 className="text-4xl font-bold tracking-tight text-ink sm:text-5xl">
            ContextBridge
          </h1>
          <p className="mt-4 text-xl font-medium text-ink-muted sm:text-2xl">
            AI Context Engineering for Enterprise Meeting Preparation
          </p>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-ink-muted">
            Aggregates data from Calendar, CRM, Tasks, and Meeting Notes to build a
            Context Envelope before generating an AI-powered meeting brief.
          </p>
        </div>

        <div className="mx-auto mt-12 grid max-w-4xl gap-4 sm:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border border-surface-border bg-surface-muted/50 p-5 text-center transition-shadow hover:shadow-card-hover"
            >
              <span className="text-2xl" role="img" aria-hidden="true">
                {feature.emoji}
              </span>
              <h3 className="mt-3 text-sm font-semibold text-ink">{feature.title}</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-ink-muted">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
