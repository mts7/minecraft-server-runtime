import os
import sqlite3

CRAFTY_DB = "/crafty_db/crafty.sqlite"
SERVERS_BASE = "/servers"


def discover_servers():
    servers = {}
    for uuid in get_uuids():
        server_dir = os.path.join(SERVERS_BASE, uuid)
        if not os.path.isdir(server_dir):
            continue

        name = get_server_name(uuid)
        log_file = os.path.join(server_dir, "logs/latest.log")

        servers[uuid] = {
            "name": name,
            "log_file": log_file,
        }

    return servers


def get_server_name(uuid: str) -> str:
    conn = sqlite3.connect(CRAFTY_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT server_name AS Name
        FROM servers
        WHERE server_id = ?
    """, (uuid,))

    row = cur.fetchone()
    conn.close()

    return row["Name"] if row else "Unknown"


def get_uuids() -> list[str]:
    return [
        entry
        for entry in os.listdir(SERVERS_BASE)
        if os.path.isdir(os.path.join(SERVERS_BASE, entry))
    ]
