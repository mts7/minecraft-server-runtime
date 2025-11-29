import re

from slack_notifier import send_to_slack


class SkipLogLine(Exception):
    """Raised when a log line should be skipped entirely"""


EVENT_HANDLERS = {}
SKIP_ERRORS = [
    "dev.kpherox.vihp.client.jade.VillagerInventoryPlugin",
]


def register_event(trigger: str):
    def decorator(func):
        EVENT_HANDLERS[trigger] = func
        return func
    return decorator


def route_event(line: str) -> None:
    for trigger, handler in EVENT_HANDLERS.items():
        if trigger not in line:
            continue

        try:
            message, summary = handler(line)
            send_to_slack(message, summary)
        except SkipLogLine:
            pass

        return


@register_event("logged in with entity id")
def parse_login(line: str) -> tuple[str, str]:
    pattern = (r".+]: (.+)\[\/([^\]]+)\] logged in with "
               r"entity id \d+ at \(([^)]+)\)")
    match = re.search(pattern, line)
    if not match:
        return "👋 Unknown user logged in", "❓ Unknown Login"

    username = match.group(1).strip()
    ip_port = match.group(2).strip()
    location = match.group(3).strip()
    player_type = "Bedrock" if username.startswith(".") else "Java"

    return (
        f"✅ _{player_type}_ player *{username}* "
        f"joined at `{location}` from *{ip_port}*.", "🟢 Player Joined"
    )


@register_event("lost connection")
def parse_lost_connection(line: str) -> tuple[str, str]:
    pattern = r"\[Server thread\/INFO]: (.*) lost connection: (.+)"
    match = re.search(pattern, line)
    if not match:
        return "🚪 Unknown user lost connection", "🔌 Unknown Disconnection"

    username = match.group(1).strip()
    reason = match.group(2).strip()

    return f"🏃‍♀️{username} left: {reason}", "🔴 Player Disconnected"


@register_event("geyser help for help")
def parse_done(line: str) -> tuple[str, str]:
    return f"🟢 Server ready. {line}", "✅ Server Ready"


@register_event("ERROR")
def parse_error(line: str) -> tuple[str, str]:
    for skip in SKIP_ERRORS:
        if skip in line:
            raise SkipLogLine(f"Skipping error {skip}")
    return f"⚠️ {line}", "❌ Server Error"


@register_event("FATAL")
def parse_fatal(line: str) -> tuple[str, str]:
    return f"🛑 {line}", "💀 Server Fatal"
