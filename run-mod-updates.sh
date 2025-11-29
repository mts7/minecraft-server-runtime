#!/bin/bash

VENV_PYTHON="/home/archer/Repositories/minecraft-server-runtime/.venv/bin/python"
UPDATER_SCRIPT="/home/archer/Repositories/minecraft-server-runtime/src/updater/mod_updater.py"
SERVERS_DIR="/home/archer/Games/Minecraft/DockerHost/docker/servers"

echo "=== Mod Update Run: $(date) ==="

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

    "$VENV_PYTHON" "$UPDATER_SCRIPT" --config "$config_file"

    if [ $? -eq 0 ]; then
        echo "  ✓ Success for $uuid"
    else
        echo "  ✗ Failed for $uuid"
    fi
done

echo "=== Mod Update Complete: $(date) ===" >> "$LOG_FILE"
echo ""
