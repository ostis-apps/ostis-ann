#!/usr/bin/env bash
set -eo pipefail

source "$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)/set_vars.sh"

source "$APP_ROOT_PATH/.venv/bin/activate"
python3 "$APP_ROOT_PATH"/problem-solver/py/modules/server.py "$@"
