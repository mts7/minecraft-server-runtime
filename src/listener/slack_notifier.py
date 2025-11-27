import os

import requests

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_UUID = os.getenv("SERVER_UUID")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def send_to_slack(message: str) -> None:
    if not SLACK_WEBHOOK:
        print("[slack] No webhook configured.")
        return

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{SERVER_NAME} Minecrafter Server "
                            f"at {SERVER_UUID}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": message
                }
            }
        ],
        "text": f"Minecraft Alert on {SERVER_NAME} {SERVER_UUID}"
    }

    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"[slack] Failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[slack] Error: {e}")
