export function StatusBadge({ mode }) {
  if (!mode) return null;

  const isGemini = mode === 'gemini';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
        isGemini
          ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200'
          : 'bg-orange-50 text-orange-700 ring-1 ring-orange-200'
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${isGemini ? 'bg-emerald-500' : 'bg-orange-500'}`}
      />
      {isGemini ? 'Gemini' : 'Mock Fallback'}
    </span>
  );
}
