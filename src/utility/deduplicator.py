"""
Deduplication utility for log messages.
"""
import re
import time
from typing import Dict


class MessageDeduplicator:
    """Deduplicates log messages within a time window, ignoring timestamps."""

    def __init__(self, window_seconds: int = 30):
        self.window_seconds = window_seconds
        self._seen_messages: Dict[str, float] = {}

    def _extract_core_message(self, message: str) -> str:
        """
        Extract the core message content, removing timestamps and other time-related elements.
        This helps in identifying when the actual message content is the same.
        """
        timestamp_pattern = r'^\[[\d\-:T\s]+\]\s*'
        core_message = re.sub(timestamp_pattern, '', message, count=1)

        return core_message.strip()

    def is_unique(self, message: str) -> bool:
        """
        Returns True if a message is unique within the time window.
        Uses core message content for duplicate detection, but preserves full message.
        Updates the timestamp for the message if it's unique.
        """
        current_time = time.time()

        expired = [
            msg for msg, timestamp in self._seen_messages.items()
            if current_time - timestamp > self.window_seconds
        ]
        for msg in expired:
            del self._seen_messages[msg]

        core_message = self._extract_core_message(message)

        if core_message not in self._seen_messages:
            self._seen_messages[core_message] = current_time
            return True

        return False
