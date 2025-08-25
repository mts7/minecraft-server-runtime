import os
import time
from dotenv import load_dotenv

load_dotenv()
LOG_PATH = os.getenv("LOG_PATH", "/logs/latest.log")

def get_initial_offset(path: str) -> int:
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return 0

def main():
    print(f"[polling] Watching {LOG_PATH}")
    last_size = get_initial_offset(LOG_PATH)

    while True:
        try:
            current_size = os.path.getsize(LOG_PATH)
            if current_size > last_size:
                with open(LOG_PATH, "r") as f:
                    f.seek(last_size)
                    new_data = f.read()
                    for line in new_data.splitlines():
                        if "event test" in line:
                            print(f"[polling] Match: {line.strip()}")
                last_size = current_size
        except FileNotFoundError:
            pass
        time.sleep(1)

if __name__ == "__main__":
    main()

