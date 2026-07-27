SOURCE_PRIORITY: dict[str, float] = {
    "meeting_notes": 1.0,
    "crm": 0.7,
    "tasks": 0.6,
    "calendar": 0.5,
}


class Ranker:
    """
    Ranks retrieved context using semantic similarity, freshness, and source priority.
    """

    def rank(self, query: str, meeting_notes: list[dict]) -> list[dict]:
        ranked: list[dict] = []

        for note in meeting_notes:
            semantic_score = float(note.get("score", 0.0))

            # TODO: derive freshness from document timestamps in note metadata when available
            freshness_score = 1.0

            source = note.get("metadata", {}).get("source", "meeting_notes")
            source_priority = SOURCE_PRIORITY.get(source, 0.5)

            final_score = (
                0.6 * semantic_score
                + 0.3 * freshness_score
                + 0.1 * source_priority
            )

            ranked.append({**note, "final_score": round(final_score, 4)})

        ranked.sort(key=lambda item: item["final_score"], reverse=True)
        return ranked
