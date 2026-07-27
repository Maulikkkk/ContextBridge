import json
from datetime import date, timedelta
from pathlib import Path


class CalendarService:
    """
    Handles retrieval of structured meeting information from calendar.json.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._calendar: list[dict] | None = None

    def _load_calendar(self) -> list[dict]:
        if self._calendar is None:
            with open(self._data_dir / "calendar.json") as f:
                self._calendar = json.load(f)
        return self._calendar

    def _resolve_date(self, date_str: str) -> str:
        keyword = date_str.lower()
        today = date.today()
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
