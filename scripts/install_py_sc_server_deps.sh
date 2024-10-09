#!/usr/bin/env bash
source "$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)/set_vars.sh"

python3 -m venv "$APP_ROOT_PATH/.venv"
source "$APP_ROOT_PATH/.venv/bin/activate"
pip3 install -r "$APP_ROOT_PATH/problem-solver/py/requirements.txt"
