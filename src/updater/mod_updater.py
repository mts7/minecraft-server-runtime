#!/usr/bin/env python3
import argparse
import json
import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, TypedDict

import requests

from src.utility.server_discovery import get_server_name
from src.utility.slack_notifier import send_to_slack

LOG_FILE: str = "mod_update.log"
LOG_LEVELS: Dict[str, int] = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
}
MODRINTH_API: str = "https://api.modrinth.com/v2"
SCRIPT_DIR: Path = Path(__file__).resolve().parent
SLUG_OVERRIDES_PATH: Path = SCRIPT_DIR / "mod_slugs.json"


class UpdateSettings(TypedDict):
    mods_dir: Path
    game_version: str
    loader: str
    log_level: str
    log_path: Path


class UpdateError(Exception):
    """Base exception for known errors during the update process."""


class ApiFailed(UpdateError):
    """Raised when the Modrinth API request fails."""


class MissingSetting(UpdateError):
    """Raised when required settings are not provided."""


class NoCompatibleVersion(UpdateError):
    """Raised when no compatible version of a mod can be found."""


def get_latest_compatible_version(
        slug: str, game_version: str, loader: str
) -> Dict[str, Any]:
    versions = _get_version_data(slug, game_version, loader, "release")
    if not versions:
        logging.debug(f"Looking for beta version for {slug}")
        versions = _get_version_data(slug, game_version, loader, "beta")
    if not versions:
        logging.debug(f"Looking for beta version for {slug}")
        versions = _get_version_data(slug, game_version, loader, "alpha")

    if not versions:
        raise NoCompatibleVersion(
            f"No compatible release, beta, or alpha version for {slug} "
            f"(MC {game_version}, loader {loader})"
        )

    return versions[0]


def get_slug_from_filename(filename: str) -> str:
    """
    Tries to determine a mod's project slug from its JAR filename.
    e.g., "fabric-api-0.91.0+1.20.1.jar" -> "fabric-api"
    """
    base: str = filename.removesuffix(".jar").lower()

    base = re.sub(r'[-_](fabric|forge)?[-_]?mc?\d+(\.\d+)*.*$', '', base)
    base = re.sub(r'[-_](fabric|forge)(?!\w)', '', base)
    base = re.sub(r'[-_]\d+(\.\d+)*.*$', '', base)

    overrides = load_slug_overrides()
    return overrides.get(base, base)


def _get_version_data(
        slug: str, game_version: str, loader: str, version_type: str
) -> list[Dict[str, Any]]:
    """Helper function to get versions from the Modrinth API."""
    url = f"{MODRINTH_API}/project/{slug}/version"
    params = {
        "game_versions": json.dumps([game_version]),
        "loaders": json.dumps([loader]),
        "version_type": version_type,
    }

    response = requests.get(url, params=params, timeout=15)
    if not response.ok:
        raise ApiFailed(
            "Modrinth API failed for "
            f"{slug}: {response.status_code} - {response.text}"
        )

    return response.json()


def load_config(config_path: Path) -> Dict[str, Any]:
    with open(config_path) as f:
        config: Dict[str, Any] = json.load(f)

    config_dir: Path = config_path.parent
    config["mods_dir"] = Path(config["mods_dir"])
    config["log_path"] = Path(config.get(
        "log_path", config_dir / LOG_FILE
    ))
    return config


def load_slug_overrides() -> Dict[str, str]:
    if not SLUG_OVERRIDES_PATH.exists():
        return {}
    with open(SLUG_OVERRIDES_PATH) as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minecraft Mod Updater")

    parser.add_argument("--mods-dir", type=Path,
                        help="Path to mods directory")
    parser.add_argument("--game-version", type=str,
                        help="Minecraft version")
    parser.add_argument("--loader", type=str, choices=["fabric", "forge"],
                        help="Mod loader")
    parser.add_argument("--log-path", type=Path,
                        help="Path to log file")
    parser.add_argument("--log-level", type=str, choices=LOG_LEVELS.keys(),
                        help="Logging level")
    parser.add_argument("--config", type=Path,
                        help="Path to config file (optional)")
    parser.add_argument("--uuid", type=str,
                        help="UUID (optional)")

    return parser.parse_args()


def resolve_settings(args: argparse.Namespace) -> UpdateSettings:
    config: dict[str, Any] = {}
    if args.config and args.config.exists():
        config = load_config(args.config)

    def get(key: str, fallback: Any = None) -> Any:
        return getattr(args, key) or config.get(key) or fallback

    mods_dir = get("mods_dir")
    game_version = get("game_version")
    loader = get("loader")

    missing = []
    if mods_dir is None:
        missing.append("mods_dir")
    if game_version is None:
        missing.append("game_version")
    if loader is None:
        missing.append("loader")

    if missing:
        raise MissingSetting(
            f"Missing required settings: {', '.join(missing)}"
        )

    log_path = get("log_path", Path("../scripts"))
    log_level = get("log_level", "INFO")

    return {
        "mods_dir": Path(mods_dir),
        "game_version": str(game_version),
        "loader": str(loader),
        "log_path": Path(log_path),
        "log_level": str(log_level).upper()
    }


def setup_logging(log_path: Path, level_str: str) -> None:
    """Configures logging to both console and a rotating file."""
    log_level = LOG_LEVELS.get(level_str.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Console handler (for user feedback)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(console_handler)

    # File handler (for detailed debugging)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(file_handler)


def update_mod(
        file: Path, mods_dir: Path,
        game_version: str, loader: str
) -> int:
    slug: str = get_slug_from_filename(file.name)
    latest: Dict[str, Any] = get_latest_compatible_version(
        slug, game_version, loader
    )

    latest_filename: str = latest["files"][0]["filename"]
    if latest_filename == file.name:
        logging.info(f"File {latest_filename} matches current file")
        return 0

    logging.info(f"\nUpdating {file.name} → {latest_filename}")
    url: str = latest["files"][0]["url"]
    new_path: Path = mods_dir / latest_filename

    response = requests.get(url, timeout=30)
    new_path.write_bytes(response.content)

    logging.debug(f"Deleting {file.name}")
    file.unlink()

    return 1


def main() -> None:
    try:
        args = parse_args()
        settings = resolve_settings(args)

        log_path: Path = Path(settings["log_path"]) / LOG_FILE
        setup_logging(log_path, settings["log_level"])

        updates = 0

        for mod_file in settings["mods_dir"].glob("*.jar"):
            try:
                updates += update_mod(
                    mod_file,
                    settings["mods_dir"],
                    settings["game_version"],
                    settings["loader"]
                )
            except UpdateError as e:
                logging.error(f"❌ Error: {e}")
        if updates > 0:
            server_name = get_server_name(args.uuid)
            send_to_slack(
                server_name,
                f"Need to restart *{server_name}* at _{args.uuid}_"
                f" due to {updates} mod updates.",
                f"Updated {updates} mods"
            )
    except Exception as e:
        logging.error(f"Unknown exception: {e}")


if __name__ == "__main__":
    main()
