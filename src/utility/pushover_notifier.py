import os

import requests
from dotenv import load_dotenv

load_dotenv()
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")


def send_to_pushover(name: str, message: str, sound: str = None) -> None:
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("[pushover] Missing token or user key.")
        return

    payload = {
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "title": f"Minecraft {name}",
        "message": message,
        "priority": 1
    }

    if sound:
        payload["sound"] = sound

    try:
        response = requests.post("https://api.pushover.net/1/messages.json",
                                 data=payload,
                                 timeout=15)
        if response.status_code != 200:
            print(f"[pushover] Failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[pushover] Error: {e}")
