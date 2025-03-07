FROM python:3.11-slim as base

USER root
WORKDIR /ostis-ann/problem-solver

RUN apt-get update && apt-get install -y --no-install-recommends tini

COPY ./problem-solver/py/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt

COPY problem-solver/py/ ./problem-solver/py/

ENTRYPOINT [ "python3", "./problem-solver/py/modules/server.py"]
