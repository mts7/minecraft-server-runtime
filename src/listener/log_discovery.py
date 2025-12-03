import os
from configparser import ConfigParser
from typing import Dict

SERVERS_PATH = "/crafty/servers"

def read_server_name(props_file: str, fallback: str) -> str:
    """Read the server-name from server.properties, fallback to UUID."""
    if not os.path.isfile(props_file):
        return fallback
    config = ConfigParser()
    with open(props_file, "r") as f:
        content = "[dummy_section]\n" + f.read()
    config.read_string(content)
    return config.get("dummy_section", "server-name", fallback=fallback)

def discover_servers(base_path: str) -> Dict[str, dict[str, str]]:
    """
    Discover all Crafty servers with logs.
    Returns: uuid -> {"name": server_name, "log_file": log_path}
    """
    servers = {}
    for uuid in os.listdir(base_path):
        server_dir = os.path.join(base_path, uuid)
        log_file = os.path.join(server_dir, "logs", "latest.log")
        props_file = os.path.join(server_dir, "server.properties")
        if not os.path.isfile(log_file):
            continue
        server_name = read_server_name(props_file, fallback=uuid)
        servers[uuid] = {"name": server_name, "log_file": log_file}
    return servers
