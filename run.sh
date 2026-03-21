#!/bin/bash
BASE_DIR=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")

# 2. Define your paths relative to that directory
LOG_FILE="$BASE_DIR/service.log"
VENV_PATH="$BASE_DIR/.venv"
SCRIPT_PATH="$BASE_DIR/checkForUpdate.py"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the Python script
python "$SCRIPT_PATH"

# Deactivate the virtual environment
deactivate
