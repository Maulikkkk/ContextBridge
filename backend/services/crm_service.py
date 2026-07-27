import json

from paths import DATA_DIR


class CRMService:
    """
    Handles retrieval of client and deal information from crm.json.
    """

    def __init__(self, data_dir=None) -> None:
        self._data_dir = data_dir or DATA_DIR
        self._crm: dict | None = None

    def _load_crm(self) -> dict:
        if self._crm is None:
            with open(self._data_dir / "crm.json") as f:
                self._crm = json.load(f)
        return self._crm

    def get_client(self, client: str) -> dict | None:
        crm = self._load_crm()
        for key, record in crm.items():
            if key.lower() == client.lower():
                return record
        return None
