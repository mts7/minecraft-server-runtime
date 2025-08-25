import os
import time
from dotenv import load_dotenv
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Optional

load_dotenv()
LOG_PATH = os.getenv("LOG_PATH", "/logs/latest.log")

class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_position: int = self._get_initial_offset()

    def _get_initial_offset(self) -> int:
        try:
            return os.path.getsize(LOG_PATH)
        except FileNotFoundError:
            return 0

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.src_path != LOG_PATH:
            return

        new_data: Optional[str] = self._read_new_data()
        if not new_data:
            return

        for line in new_data.splitlines():
            if "event test" in line:
                print(f"[watchdog] Match: {line.strip()}")

    def _read_new_data(self) -> Optional[str]:
        try:
            with open(LOG_PATH, "r") as f:
                f.seek(self.last_position)
                data = f.read()
                self.last_position = f.tell()
                return data
        except Exception as e:
            print(f"[watchdog] Error reading log: {e}")
            return None

def main() -> None:
    print(f"[watchdog] Watching {LOG_PATH}")
    observer = PollingObserver()
    observer.schedule(LogHandler(), path=os.path.dirname(LOG_PATH), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

