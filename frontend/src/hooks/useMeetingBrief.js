import { useState, useCallback, useEffect, useRef } from 'react';
import { generateMeetingBrief, fetchHealth, getApiErrorMessage } from '../services/api';

const LOADING_STAGES = [
  'Building Context Package...',
  'Searching Meeting Notes...',
  'Ranking Context...',
  'Generating Meeting Brief...',
];

const PIPELINE_STEPS = [
  'calendar',
  'crm',
  'tasks',
  'notes',
  'search',
  'ranking',
  'envelope',
  'llm',
  'brief',
];

const STEP_INTERVAL_MS = 700;

export function useMeetingBrief() {
  const [query, setQuery] = useState('Prepare me for Globex meeting');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState(0);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [llmMode, setLlmMode] = useState(null);
  const [activePipelineStep, setActivePipelineStep] = useState(-1);
  const [pipelineComplete, setPipelineComplete] = useState(false);
  const pipelineTimer = useRef(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => setLlmMode(data.mode))
      .catch(() => setLlmMode('mock'));
  }, []);

  const startPipelineAnimation = useCallback(() => {
    setPipelineComplete(false);
    setActivePipelineStep(0);
    let step = 0;

    pipelineTimer.current = setInterval(() => {
      step += 1;
      if (step < PIPELINE_STEPS.length) {
        setActivePipelineStep(step);
      } else {
        clearInterval(pipelineTimer.current);
        setPipelineComplete(true);
      }
    }, STEP_INTERVAL_MS);
  }, []);

  const stopPipelineAnimation = useCallback(() => {
    if (pipelineTimer.current) {
      clearInterval(pipelineTimer.current);
      pipelineTimer.current = null;
    }
  }, []);

  useEffect(() => () => stopPipelineAnimation(), [stopPipelineAnimation]);

  const submit = useCallback(async () => {
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setLoadingStage(0);
    setPipelineComplete(false);
    startPipelineAnimation();

    const stageInterval = setInterval(() => {
      setLoadingStage((prev) => (prev < LOADING_STAGES.length - 1 ? prev + 1 : prev));
    }, 2200);

    try {
      const [data, health] = await Promise.all([
        generateMeetingBrief(query.trim()),
        fetchHealth().catch(() => ({ mode: 'mock' })),
      ]);

      clearInterval(stageInterval);
      stopPipelineAnimation();
      setLlmMode(health.mode);
      setResult(data);
      setActivePipelineStep(PIPELINE_STEPS.length - 1);
      setPipelineComplete(true);
    } catch (err) {
      clearInterval(stageInterval);
      stopPipelineAnimation();
      setActivePipelineStep(-1);
      setPipelineComplete(false);
      setError(
        getApiErrorMessage(err, 'Unable to generate meeting brief. Please try again.'),
      );
    } finally {
      setLoading(false);
      setLoadingStage(0);
    }
  }, [query, loading, startPipelineAnimation, stopPipelineAnimation]);

  const llmLabel = llmMode === 'gemini' ? 'Gemini' : 'Mock LLM';

  return {
    query,
    setQuery,
    loading,
    loadingStage,
    loadingMessage: LOADING_STAGES[loadingStage],
    error,
    result,
    llmMode,
    llmLabel,
    activePipelineStep,
    pipelineComplete,
    submit,
    pipelineSteps: PIPELINE_STEPS,
  };
}

export function deriveRecommendedQuestions(contextPackage, meetingBrief) {
  const meeting = contextPackage?.meeting || {};
  const client = contextPackage?.client || {};
  const company = client.company || meeting.client || 'the client';

  const questions = [
    `What is the current status of our proposal with ${company}?`,
    `Are there any blockers we should address before the meeting on ${meeting.date || 'the scheduled date'}?`,
    `How does ${company}'s timeline align with our ${client.deal_stage || 'current'} stage objectives?`,
  ];

  if (meetingBrief?.suggested_talking_points?.length) {
    questions[0] = `Can we walk through: ${meetingBrief.suggested_talking_points[0]}?`;
  }

  return questions;
}
