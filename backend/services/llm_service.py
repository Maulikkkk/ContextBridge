import json
import logging
import os
import re
import time

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")


def get_llm_mode() -> str:
    return "gemini" if os.getenv("GEMINI_API_KEY") else "mock"


def build_prompt(context_package: dict, user_query: str) -> str:
    meeting = context_package.get("meeting", {})
    client = context_package.get("client", {})
    tasks = context_package.get("pending_tasks", [])
    notes = context_package.get("retrieved_notes", [])

    agenda = ", ".join(meeting.get("agenda", []))
    attendees = ", ".join(
        f"{a['name']} ({a['role']})" for a in meeting.get("attendees", [])
        if isinstance(a, dict)
    )

    tasks_text = "\n".join(
        f"- {task['title']} | due: {task.get('due_date', 'N/A')} | priority: {task.get('priority', 'N/A')}"
        for task in tasks
    ) or "None"

    notes_text = "\n\n".join(
        f"Source: {note.get('metadata', {}).get('filename', 'unknown')} "
        f"(relevance: {note.get('final_score', note.get('score', 0))})\n"
        f"{note.get('content', '')}"
        for note in notes
    ) or "None available"

    contact = client.get("primary_contact", {})
    contact_line = ""
    if isinstance(contact, dict) and contact.get("name"):
        contact_line = f"Primary Contact: {contact['name']}, {contact.get('title', '')}"

    return f"""You are a sales meeting preparation assistant.

User request: {user_query}

=== CONTEXT PACKAGE ===

## Meeting
Title: {meeting.get('title', 'N/A')}
Date: {meeting.get('date', 'N/A')} at {meeting.get('time', 'N/A')}
Location: {meeting.get('location', 'N/A')}
Attendees: {attendees or 'N/A'}
Agenda: {agenda or 'N/A'}

## Client (CRM)
Company: {client.get('company', 'N/A')}
Industry: {client.get('industry', 'N/A')}
Deal Stage: {client.get('deal_stage', 'N/A')}
Contract Value: {client.get('annual_contract_value', 'N/A')}
{contact_line}
Account Notes: {client.get('notes', 'N/A')}

## Pending Tasks
{tasks_text}

## Prior Meeting Notes (ranked)
{notes_text}

=== INSTRUCTIONS ===

Using ONLY the context above, produce a concise meeting preparation brief.
Respond with valid JSON only — no markdown fences — using exactly these keys:
{{
  "meeting_summary": "2-3 sentence overview of the upcoming meeting",
  "client_background": "2-3 sentence client context",
  "pending_tasks": ["task 1", "task 2"],
  "risks": ["risk 1", "risk 2"],
  "suggested_talking_points": ["point 1", "point 2", "point 3"],
  "sources_used": ["calendar", "crm", "tasks", "meeting_notes/Acme.md"]
}}
"""


def generate_meeting_brief(context_package: dict, user_query: str) -> dict:
    start = time.perf_counter()

    prompt = build_prompt(context_package, user_query)
    mode = get_llm_mode()
    logger.info(f"Prompt built ({len(prompt)} chars)")
    logger.info(f"LLM mode: {mode}")

    if mode == "gemini":
        try:
            brief = _generate_gemini(prompt)
            logger.info(f"Gemini generation succeeded (model={GEMINI_MODEL})")
        except Exception as exc:
            logger.warning(
                f"Gemini failed ({type(exc).__name__}: {exc}), falling back to mock"
            )
            brief = _generate_mock(context_package)
    else:
        brief = _generate_mock(context_package)

    if not brief.get("sources_used"):
        brief["sources_used"] = _collect_sources(context_package)

    elapsed = time.perf_counter() - start
    logger.info(f"Generation completed in {elapsed:.2f}s")

    return brief


def _collect_sources(context_package: dict) -> list[str]:
    sources = ["calendar", "crm", "tasks"]
    for note in context_package.get("retrieved_notes", []):
        filename = note.get("metadata", {}).get("filename")
        if filename:
            sources.append(f"meeting_notes/{filename}")
    return list(dict.fromkeys(sources))


def _generate_gemini(prompt: str) -> dict:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    text = response.text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    return json.loads(text)


def _generate_mock(context_package: dict) -> dict:
    meeting = context_package.get("meeting", {})
    client = context_package.get("client", {})
    tasks = context_package.get("pending_tasks", [])
    notes = context_package.get("retrieved_notes", [])

    company = client.get("company", meeting.get("client", "Unknown"))
    title = meeting.get("title", "Upcoming meeting")
    agenda = meeting.get("agenda", [])
    task_titles = [task["title"] for task in tasks]

    meeting_summary = (
        f"{title} on {meeting.get('date', 'N/A')} at {meeting.get('time', 'N/A')}. "
        f"Location: {meeting.get('location', 'N/A')}. "
        f"Agenda: {', '.join(agenda) if agenda else 'Not specified'}."
    )

    client_background = (
        f"{company} ({client.get('industry', 'N/A')}) — "
        f"deal stage: {client.get('deal_stage', 'N/A')}, "
        f"health: {client.get('health_score', 'N/A')}. "
        f"{client.get('notes', '')}"
    ).strip()

    risks = _extract_bullets_from_notes(notes, after_keyword="concern")
    if not risks:
        risks = _extract_bullets_from_notes(notes)

    talking_points = agenda[:5] if agenda else []

    note_summaries = [
        f"{note.get('metadata', {}).get('filename', 'note')}: "
        f"{note.get('content', '')[:200].strip()}"
        for note in notes
    ]
    if note_summaries and not talking_points:
        talking_points = [f"Review prior notes — {note_summaries[0][:120]}"]

    return {
        "meeting_summary": meeting_summary,
        "client_background": client_background,
        "pending_tasks": task_titles,
        "risks": risks,
        "suggested_talking_points": talking_points,
        "sources_used": _collect_sources(context_package),
    }


def _extract_bullets_from_notes(notes: list[dict], after_keyword: str = "") -> list[str]:
    bullets: list[str] = []
    capture = not after_keyword

    for note in notes:
        for line in note.get("content", "").split("\n"):
            stripped = line.strip()
            if after_keyword and after_keyword in stripped.lower():
                capture = True
                continue
            if capture and stripped.startswith("- "):
                item = stripped[2:].strip()
                if item and item not in bullets:
                    bullets.append(item)

    return bullets[:5]
