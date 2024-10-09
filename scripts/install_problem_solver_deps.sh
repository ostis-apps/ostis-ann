#!/usr/bin/env bash
set -eo pipefail

source "$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)/set_vars.sh"

unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*)
    machine=Linux
    ;;
  Darwin*)
    machine=macOS
    ;;
  *)
    echo "This script isn't supported on your OS '${unameOut}'. Please, use Linux or macOS"
    exit 1
esac

if [ "${machine}" == "Linux" ];
then
  packagelist=(
	python3-pip
	python3-setuptools
	build-essential
	cmake
	nlohmann-json3-dev
	libssl-dev
	file
  )
  sudo apt-get install -y --no-install-recommends "${packagelist[@]}"
elif [ "${machine}" == "macOS" ]; then
  brew install python@3.12 cmake nlohmann-json openssl
fi

"${SC_MACHINE_PATH}/scripts/install_dependencies.sh" --dev
