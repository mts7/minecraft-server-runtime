import os
from dotenv import load_dotenv
from inotify_simple import INotify, flags

load_dotenv()
LOG_PATH = os.getenv("LOG_PATH", "/logs/latest.log")
LOG_DIR = os.path.dirname(LOG_PATH)
LOG_NAME = os.path.basename(LOG_PATH)

def main() -> None:
    print(f"[inotify] Watching {LOG_PATH}")
    inotify = INotify()
    watch_flags = flags.MODIFY | flags.CLOSE_WRITE | flags.MOVE_SELF | flags.DELETE_SELF
    wd = inotify.add_watch(LOG_DIR, watch_flags)

    try:
        last_position = os.path.getsize(LOG_PATH)
    except FileNotFoundError:
        last_position = 0

    while True:
        for event in inotify.read(timeout=1000):
            if event.name != LOG_NAME:
                continue
            try:
                with open(LOG_PATH, "r") as f:
                    f.seek(last_position)
                    new_data = f.read()
                    last_position = f.tell()
                    for line in new_data.splitlines():
                        if "event test" in line:
                            print(f"[inotify] Match: {line.strip()}")
            except Exception as e:
                print(f"[inotify] Error: {e}")

