#!/bin/bash

VENV_PYTHON="/home/archer/Repositories/minecraft-server-runtime/.venv/bin/python"
UPDATER_SCRIPT="/home/archer/Repositories/minecraft-server-runtime/src/updater/mod_updater.py"
SERVERS_DIR="/home/archer/Games/Minecraft/DockerHost/docker/servers"
LOG_FILE="/var/log/mod-updater.log"

echo "=== Mod Update Run: $(date) ===" >> "$LOG_FILE"

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
        echo "Skipping $uuid: no mod_updates.json config found" >> "$LOG_FILE"
        continue
    fi

    echo "Updating mods for server: $uuid" | tee -a "$LOG_FILE"

    "$VENV_PYTHON" "$UPDATER_SCRIPT" --config "$config_file" >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "  ✓ Success for $uuid" | tee -a "$LOG_FILE"
    else
        echo "  ✗ Failed for $uuid" | tee -a "$LOG_FILE"
    fi
done

echo "=== Mod Update Complete: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
