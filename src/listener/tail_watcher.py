import os
import subprocess
from dotenv import load_dotenv
from event_router import route_event

load_dotenv()
LOG_PATH = os.getenv("LOG_PATH", "/logs/latest.log")

def main():
    print(f"[tail] Watching {LOG_PATH}")
    proc = subprocess.Popen(["tail", "-n", "0", "-F", LOG_PATH], stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        route_event(line.strip())

if __name__ == "__main__":
    main()

