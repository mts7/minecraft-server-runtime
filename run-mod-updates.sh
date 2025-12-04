#!/bin/bash

. .env

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV="${SCRIPT_DIR}/.venv"
VENV_PYTHON="${VENV}/bin/python3"
UPDATER_SCRIPT="src.updater.mod_updater"
SERVERS_DIR="${CRAFTY_DIRECTORY}/docker/servers"

echo "=== Mod Update Run: $(date) ==="

cd "$SCRIPT_DIR"
python3 -m venv ${VENV}
"${VENV_PYTHON}" -m pip install -r requirements.txt

# Find all directories with a mods subdirectory
for server_dir in "$SERVERS_DIR"/*/; do
    # Check if mods directory exists
    if [ ! -d "${server_dir}mods" ]; then
        continue
    fi

    uuid=$(basename "$server_dir")
    config_file="${server_dir}config/mod_updates.json"

    # Check if config file exists
    if [ ! -f "$config_file" ]; then
        echo "Skipping $uuid: no mod_updates.json config found"
        continue
    fi

    echo "Updating mods for server: $uuid"

    "$VENV_PYTHON" -m "$UPDATER_SCRIPT" --config "$config_file" --uuid "$uuid"

    if [ $? -eq 0 ]; then
        echo "  ✓ Success for $uuid"
    else
        echo "  ✗ Failed for $uuid"
    fi
done

echo "=== Mod Update Complete: $(date) ==="
echo ""
