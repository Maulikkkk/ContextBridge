import { Hero } from '../components/Hero';
import { SearchSection } from '../components/SearchSection';
import { Pipeline } from '../components/Pipeline';
import { LoadingOverlay } from '../components/LoadingOverlay';
import { StatusBadge } from '../components/StatusBadge';
import { ErrorAlert } from '../components/ErrorAlert';
import { ContextEnvelope } from '../components/ContextEnvelope';
import { EmptyState } from '../components/EmptyState';
import { Footer } from '../components/Footer';
import {
  MeetingSummaryCard,
  ClientBackgroundCard,
  TasksCard,
  RisksCard,
  TalkingPointsCard,
  RecommendedQuestionsCard,
  SourcesCard,
} from '../components/ResultCards';
import { useMeetingBrief, deriveRecommendedQuestions } from '../hooks/useMeetingBrief';

export default function Dashboard() {
  const {
    query,
    setQuery,
    loading,
    loadingMessage,
    error,
    result,
    llmMode,
    llmLabel,
    activePipelineStep,
    pipelineComplete,
    submit,
    pipelineSteps,
  } = useMeetingBrief();

  const brief = result?.meeting_brief || {};
  const contextPackage = result?.context_package || null;
  const meeting = contextPackage?.meeting || {};
  const recommendedQuestions = contextPackage
    ? deriveRecommendedQuestions(contextPackage, brief)
    : [];

  const showResults = result && !loading;

  return (
    <div className="flex min-h-screen flex-col">
      <Hero />

      <SearchSection
        query={query}
        onQueryChange={setQuery}
        onSubmit={submit}
        loading={loading}
        disabled={loading}
      />

      <Pipeline
        activeStep={activePipelineStep}
        stepIds={pipelineSteps}
        loading={loading}
        complete={pipelineComplete && !loading}
        llmLabel={llmLabel}
      />

      {loading && <LoadingOverlay message={loadingMessage} />}

      {error && (
        <div className="py-4">
          <ErrorAlert message={error} />
        </div>
      )}

      {!result && !loading && !error && <EmptyState />}

      {showResults && (
        <>
          <section className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-ink">Meeting Brief</h2>
                <p className="mt-1 text-sm text-ink-muted">
                  Generated from your Context Envelope
                </p>
              </div>
              <StatusBadge mode={llmMode} />
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              <div className="sm:col-span-2 lg:col-span-3">
                <MeetingSummaryCard
                  meeting={meeting}
                  summary={brief.meeting_summary}
                  delay={0}
                />
              </div>
              <div className="sm:col-span-2">
                <ClientBackgroundCard background={brief.client_background} delay={80} />
              </div>
              <TasksCard tasks={brief.pending_tasks} delay={160} />
              <RisksCard risks={brief.risks} delay={240} />
              <TalkingPointsCard points={brief.suggested_talking_points} delay={320} />
              <RecommendedQuestionsCard questions={recommendedQuestions} delay={400} />
              <div className="sm:col-span-2 lg:col-span-3">
                <SourcesCard sources={brief.sources_used} delay={480} />
              </div>
            </div>
          </section>

          <ContextEnvelope data={contextPackage} />
        </>
      )}

      <div className="mt-auto">
        <Footer />
      </div>
    </div>
  );
}
