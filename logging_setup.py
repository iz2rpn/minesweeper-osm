from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

import settings


class DailyOverwriteFileHandler(logging.FileHandler):
    """Single log file that is truncated when the date changes."""

    def __init__(self, filename: str | Path, encoding: str = "utf-8") -> None:
        self.current_day = dt.date.today()
        super().__init__(filename=filename, mode="w", encoding=encoding, delay=False)

    def emit(self, record: logging.LogRecord) -> None:
        today = dt.date.today()
        if today != self.current_day:
            self.current_day = today
            self.acquire()
            try:
                if self.stream:
                    self.stream.close()
                # mode='w' truncates file for the new day
                self.stream = self._open()
            finally:
                self.release()
        super().emit(record)


def configure_logging() -> None:
    """Configures application logging to file only."""
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    file_handler = DailyOverwriteFileHandler(settings.LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[file_handler],
        force=True,
    )
