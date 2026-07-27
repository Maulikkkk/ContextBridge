from datetime import datetime, timezone


class ContextBuilder:
    """
    Assembles ranked and structured retrieval results into a Context Package.
    """

    def build(
        self,
        meeting: dict,
        client: dict,
        pending_tasks: list[dict],
        ranked_notes: list[dict],
    ) -> dict:
        top_notes = ranked_notes[:3]

        return {
            "metadata": {
                "intent": "meeting_brief",
                "client": meeting.get("client", ""),
                "meeting_date": meeting.get("date", ""),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "meeting": meeting,
            "client": client,
            "pending_tasks": pending_tasks,
            "retrieved_notes": top_notes,
            "context_summary": {
                "top_note_count": len(top_notes),
                "pending_task_count": len(pending_tasks),
            },
        }
