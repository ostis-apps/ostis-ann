# Установка проекта нативно на Linux

## Установка

```sh
git clone https://github.com/ostis-apps/ostis-ann
cd ostis-ann
git submodule update --init --recursive
./scripts/install_problem_solver_deps.sh
./scripts/install_interface_deps.sh
```

## Сборка

- Сборка решателя задач

  ```sh
  ./scripts/build_problem_solver.sh
  ```

- Сборка базы знаний

  ```sh
  ./scripts/build_kb.sh
  ```

- Сборка sc-web

  ```sh
  ./scripts/build_sc_web.sh
  ```

## 🚀 Запуск

```sh
# Терминал 1
./scripts/run_sc_server.sh

# Терминал 2
./scripts/run_sc_web.sh
```

  Данные команды запустят web-интерфейс:

- sc-web - `localhost:8000`

