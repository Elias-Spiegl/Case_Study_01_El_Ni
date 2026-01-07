import json
from pathlib import Path

class JsonRepository:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self._write([])

    def _read(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_all(self):
        return self._read()

    def save_all(self, data):
        self._write(data)
