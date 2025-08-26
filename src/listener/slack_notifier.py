import os

import requests

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def send_to_slack(message: str, color: str = "#cccccc") -> None:
    if not SLACK_WEBHOOK:
        print("[slack] No webhook configured.")
        return

    payload = {
        "attachments": [
            {
                "color": color,
                "text": message,
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"[slack] Failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[slack] Error: {e}")
