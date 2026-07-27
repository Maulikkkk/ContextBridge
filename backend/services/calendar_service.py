import json
import os
from datetime import date, timedelta

from paths import DATA_DIR


class CalendarService:
    """
    Handles retrieval of structured meeting information from calendar.json.
    """

    def __init__(self, data_dir=None) -> None:
        self._data_dir = data_dir or DATA_DIR
        self._calendar: list[dict] | None = None

    def _load_calendar(self) -> list[dict]:
        if self._calendar is None:
            with open(self._data_dir / "calendar.json") as f:
                self._calendar = json.load(f)
        return self._calendar

    def _today(self) -> date:
        """Use DEMO_TODAY env var for stable demo dates (e.g. 2026-07-27)."""
        demo_today = os.getenv("DEMO_TODAY")
        if demo_today:
            return date.fromisoformat(demo_today)
        return date.today()

    def _resolve_date(self, date_str: str) -> str:
        keyword = date_str.lower()
        today = self._today()
        if keyword == "today":
            return today.isoformat()
        if keyword == "tomorrow":
            return (today + timedelta(days=1)).isoformat()
        return date_str

    def find_meeting(self, client: str, date_str: str) -> dict | None:
        resolved_date = self._resolve_date(date_str)
        for meeting in self._load_calendar():
            if meeting["client"].lower() == client.lower() and meeting["date"] == resolved_date:
                return meeting
        return None

    def next_meeting_for_client(self, client: str) -> dict | None:
        """Nearest upcoming meeting for this client (by calendar date)."""
        today = self._today()
        client_meetings = [
            m for m in self._load_calendar()
            if m["client"].lower() == client.lower()
        ]
        upcoming = sorted(
            (m for m in client_meetings if m["date"] >= today.isoformat()),
            key=lambda m: m["date"],
        )
        if upcoming:
            return upcoming[0]
        # Demo fallback: return any scheduled meeting for this client
        return client_meetings[0] if client_meetings else None

    def find_meeting_for_client(self, client: str, date_str: str | None = None) -> dict | None:
        """
        Find a meeting by client. If date_str is provided (today/tomorrow), match that date.
        Otherwise return the next scheduled meeting for the client — no date required.
        """
        if date_str:
            return self.find_meeting(client, date_str)
        return self.next_meeting_for_client(client)
