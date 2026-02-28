"""
Unit tests for the MessageDeduplicator.
"""
from src.utility.deduplicator import MessageDeduplicator


def test_deduplicator_only_one_notification_for_same_content_different_timestamps():
    """
    Test that only one notification is sent for log entries with same content but different timestamps.
    """
    deduplicator = MessageDeduplicator(window_seconds=30)

    # Your log entries
    log_entries = [
        "[10:08:36] [Server thread/ERROR]: Block-attached entity at invalid position: null",
        "[10:08:36] [Server thread/ERROR]: Block-attached entity at invalid position: null",
        "[10:08:44] [Server thread/ERROR]: Block-attached entity at invalid position: null",
        "[10:08:44] [Server thread/ERROR]: Block-attached entity at invalid position: null"
    ]

    # Track unique messages
    unique_messages = []

    for entry in log_entries:
        if deduplicator.is_unique(entry):
            unique_messages.append(entry)

    # Only the first message should be unique (all have same core content)
    assert len(unique_messages) == 1
    assert unique_messages[0] == log_entries[0]