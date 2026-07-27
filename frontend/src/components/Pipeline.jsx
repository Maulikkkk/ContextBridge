const STEPS = [
  { id: 'calendar', label: 'Calendar' },
  { id: 'crm', label: 'CRM' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'notes', label: 'Meeting Notes' },
  { id: 'search', label: 'Semantic Search' },
  { id: 'ranking', label: 'Ranking' },
  { id: 'envelope', label: 'Context Package' },
  { id: 'llm', label: 'Gemini' },
  { id: 'brief', label: 'Meeting Brief' },
];

function CheckIcon() {
  return (
    <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

export function Pipeline({ activeStep, stepIds, loading, complete, llmLabel = 'Gemini' }) {
  const steps = STEPS.filter((s) => stepIds.includes(s.id)).map((s) =>
    s.id === 'llm' ? { ...s, label: llmLabel } : s,
  );

  const progress = complete
    ? 100
    : loading && activeStep >= 0
      ? Math.round(((activeStep + 1) / steps.length) * 100)
      : 0;

  return (
    <section className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-ink-faint">
          Context Engineering Pipeline
        </h2>
        {(loading || complete) && (
          <span className="text-xs font-medium text-ink-muted">{progress}%</span>
        )}
      </div>

      <div className="rounded-xl border border-surface-border bg-white p-4 shadow-card sm:p-6">
        {(loading || complete) && (
          <div className="mb-5 h-1.5 overflow-hidden rounded-full bg-surface-muted">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        <div className="overflow-x-auto">
          <div className="flex min-w-max items-center gap-1 sm:gap-2">
            {steps.map((step, index) => {
              const stepIndex = stepIds.indexOf(step.id);
              const isCompleted = complete || (loading && stepIndex < activeStep);
              const isCurrent = loading && stepIndex === activeStep;
              const isPending = !isCompleted && !isCurrent;

              return (
                <div key={step.id} className="flex items-center">
                  <div
                    className={`flex flex-col items-center rounded-lg px-2 py-2 transition-all duration-300 sm:px-3 ${
                      isPending ? 'opacity-40' : 'opacity-100'
                    } ${isCurrent ? 'scale-105' : ''}`}
                  >
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300 sm:h-11 sm:w-11 ${
                        isCompleted
                          ? 'border-emerald-500 bg-emerald-500 shadow-sm'
                          : isCurrent
                            ? 'border-accent bg-accent-light ring-2 ring-accent/30 animate-pulse-soft'
                            : 'border-surface-border bg-surface-muted'
                      }`}
                    >
                      {isCompleted ? (
                        <CheckIcon />
                      ) : isCurrent ? (
                        <span className="h-2.5 w-2.5 rounded-full bg-accent" />
                      ) : (
                        <span className="h-2 w-2 rounded-full bg-surface-border" />
                      )}
                    </div>
                    <span
                      className={`mt-2 max-w-[5rem] text-center text-[10px] font-medium leading-tight sm:max-w-none sm:text-xs ${
                        isCompleted
                          ? 'text-emerald-700'
                          : isCurrent
                            ? 'text-accent'
                            : 'text-ink-faint'
                      }`}
                    >
                      {isCompleted && '✓ '}
                      {step.label}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <svg
                      className={`mx-0.5 h-4 w-4 shrink-0 transition-colors duration-300 sm:mx-1 ${
                        isCompleted ? 'text-emerald-400' : 'text-surface-border'
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
