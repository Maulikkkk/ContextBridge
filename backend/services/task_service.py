import json
from pathlib import Path


class TaskService:
    """
    Handles retrieval of pending tasks and action items from tasks.json.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._tasks: list[dict] | None = None

    def _load_tasks(self) -> list[dict]:
        if self._tasks is None:
            with open(self._data_dir / "tasks.json") as f:
                self._tasks = json.load(f)
        return self._tasks

    def get_pending_tasks(self, client: str) -> list[dict]:
        return [
            task
            for task in self._load_tasks()
            if task["client"].lower() == client.lower() and task["status"] == "pending"
        ]
