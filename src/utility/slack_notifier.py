import os

import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def send_to_slack(name: str, message: str, summary: str) -> None:
    if not SLACK_WEBHOOK:
        print("[slack] No webhook configured.")
        return

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Minecraft {name}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ],
        "text": f"Minecraft {name} Alert: {summary}"
    }

    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"[slack] Failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[slack] Error: {e}")
