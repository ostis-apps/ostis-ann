# Native installation on Linux

## Installation

```sh
git clone https://github.com/ostis-apps/ostis-ann
cd ostis-ann
git submodule update --init --recursive
./scripts/install_problem_solver_deps.sh
./scripts/install_interface_deps.sh
./scripts/install_py_sc_server_deps.sh
```

## Build

- Build problem solver

  ```sh
  ./scripts/build_problem_solver.sh
  ```

- Build knowledge base

  ```sh
  ./scripts/build_kb.sh
  ```

- Build sc-web

  ```sh
  ./scripts/build_sc_web.sh
  ```

## 🚀 Run

  ```sh
  # Terminal 1
  ./scripts/run_sc_server.sh

  # Terminal 2
  ./scripts/run_py_sc_server.sh
  
  # Terminal 3
  ./scripts/run_sc_web.sh
  ```

  This commands will launch UI on your machine:

- sc-web - `localhost:8000`
