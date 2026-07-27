function CardShell({ title, icon, children, delay = 0, className = '' }) {
  return (
    <div
      className={`animate-slide-up rounded-xl border border-surface-border bg-white p-7 shadow-card transition-shadow hover:shadow-card-hover ${className}`}
      style={{ animationDelay: `${delay}ms`, opacity: 0 }}
    >
      <div className="mb-5 flex items-center gap-3 border-b border-surface-border pb-4">
        <span className="text-xl" role="img" aria-hidden="true">{icon}</span>
        <h3 className="text-base font-semibold text-ink">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export function MeetingSummaryCard({ meeting, summary, delay = 0 }) {
  const agenda = meeting?.agenda || [];
  const client = meeting?.client || '—';

  return (
    <CardShell title="Meeting Summary" icon="📄" delay={delay} className="border-accent/20 bg-gradient-to-br from-white to-accent-light/30">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">Client</p>
          <p className="mt-1 text-lg font-semibold text-ink">{client}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">Date</p>
          <p className="mt-1 text-lg font-semibold text-ink">{formatDate(meeting?.date)}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">Time</p>
          <p className="mt-1 text-lg font-semibold text-ink">
            {meeting?.time || '—'}
            {meeting?.location && (
              <span className="ml-2 text-sm font-normal text-ink-muted">· {meeting.location}</span>
            )}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">Meeting</p>
          <p className="mt-1 text-base font-medium text-ink">{meeting?.title || '—'}</p>
        </div>
      </div>

      {agenda.length > 0 && (
        <div className="mt-6 border-t border-surface-border pt-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">Agenda</p>
          <ul className="mt-3 space-y-2">
            {agenda.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-ink-muted">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded bg-accent-light text-xs font-semibold text-accent">
                  {i + 1}
                </span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary && (
        <div className="mt-6 border-t border-surface-border pt-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-ink-faint">Overview</p>
          <p className="mt-2 text-base leading-relaxed text-ink-muted">{summary}</p>
        </div>
      )}
    </CardShell>
  );
}

export function ClientBackgroundCard({ background, delay = 0 }) {
  return (
    <CardShell title="Client Background" icon="🏢" delay={delay}>
      <p className="text-sm leading-relaxed text-ink-muted">{background || '—'}</p>
    </CardShell>
  );
}

export function TasksCard({ tasks, delay = 0 }) {
  const items = Array.isArray(tasks) ? tasks : [];
  return (
    <CardShell title="Pending Tasks" icon="✅" delay={delay}>
      {items.length === 0 ? (
        <p className="text-sm text-ink-faint">No pending tasks.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((task, i) => (
            <li key={i} className="flex items-start gap-3 rounded-lg bg-surface-muted px-4 py-3 text-sm text-ink-muted">
              <span className="text-emerald-600">✓</span>
              {typeof task === 'string' ? task : task.title}
            </li>
          ))}
        </ul>
      )}
    </CardShell>
  );
}

export function RisksCard({ risks, delay = 0 }) {
  const items = Array.isArray(risks) ? risks : [];
  return (
    <CardShell title="Risks" icon="⚠️" delay={delay}>
      {items.length === 0 ? (
        <p className="text-sm text-ink-faint">No risks identified.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((risk, i) => (
            <li
              key={i}
              className="rounded-lg border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-900"
            >
              {risk}
            </li>
          ))}
        </ul>
      )}
    </CardShell>
  );
}

export function TalkingPointsCard({ points, delay = 0 }) {
  const items = Array.isArray(points) ? points : [];
  return (
    <CardShell title="Talking Points" icon="💬" delay={delay}>
      {items.length === 0 ? (
        <p className="text-sm text-ink-faint">No talking points generated.</p>
      ) : (
        <ol className="space-y-3">
          {items.map((point, i) => (
            <li key={i} className="flex gap-3 text-sm text-ink-muted">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-light text-xs font-bold text-accent">
                {i + 1}
              </span>
              {point}
            </li>
          ))}
        </ol>
      )}
    </CardShell>
  );
}

export function RecommendedQuestionsCard({ questions, delay = 0 }) {
  const items = Array.isArray(questions) ? questions : [];
  return (
    <CardShell title="Recommended Questions" icon="❓" delay={delay}>
      {items.length === 0 ? (
        <p className="text-sm text-ink-faint">No questions suggested.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((q, i) => (
            <li
              key={i}
              className="rounded-lg border border-surface-border bg-surface-muted px-4 py-3.5 text-sm italic text-ink-muted"
            >
              &ldquo;{q}&rdquo;
            </li>
          ))}
        </ul>
      )}
    </CardShell>
  );
}

const SOURCE_META = [
  { key: 'calendar', label: 'Calendar', icon: '📅' },
  { key: 'crm', label: 'CRM', icon: '🏢' },
  { key: 'tasks', label: 'Tasks', icon: '✅' },
  { key: 'meeting_notes', label: 'Meeting Notes', icon: '📝' },
];

export function SourcesCard({ sources, delay = 0 }) {
  const items = Array.isArray(sources) ? sources : [];

  const activeSources = SOURCE_META.filter((meta) =>
    items.some((s) => s.toLowerCase().includes(meta.key)),
  );

  return (
    <CardShell title="Sources Used" icon="🔗" delay={delay}>
      <p className="mb-4 text-xs text-ink-faint">
        ContextBridge aggregated context from multiple enterprise data sources:
      </p>
      {activeSources.length === 0 ? (
        <p className="text-sm text-ink-faint">No sources recorded.</p>
      ) : (
        <ul className="grid gap-2 sm:grid-cols-2">
          {activeSources.map((source) => (
            <li
              key={source.key}
              className="flex items-center gap-3 rounded-lg border border-emerald-100 bg-emerald-50 px-4 py-3"
            >
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-xs font-bold text-white">
                ✓
              </span>
              <span className="text-sm font-medium text-emerald-900">
                {source.icon} {source.label}
              </span>
            </li>
          ))}
        </ul>
      )}
    </CardShell>
  );
}
