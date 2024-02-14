FROM ubuntu:focal as base
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
# install dependencies
COPY ./scripts /tmp/scripts
COPY ./problem-solver/sc-machine/scripts /tmp/problem-solver/sc-machine/scripts
COPY ./problem-solver/sc-machine/requirements.txt /tmp/problem-solver/sc-machine/requirements.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends sudo ccache tini tzdata && \
    /tmp/scripts/install_problem_solver_deps.sh

FROM base as builder
ENV CCACHE_DIR=/ccache

RUN apt-get install -y --no-install-recommends git && \
    /tmp/scripts/install_problem_solver_deps.sh --dev

COPY . /ostis-ann
WORKDIR /ostis-ann/scripts
RUN --mount=type=cache,target=/ccache/ ./build_problem_solver.sh -r

FROM base as final
COPY --from=builder /ostis-ann/problem-solver/sc-machine/scripts /ostis-ann/problem-solver/sc-machine/scripts
COPY --from=builder /ostis-ann/problem-solver/sc-machine/requirements.txt /ostis-ann/problem-solver/sc-machine/requirements.txt

COPY --from=builder /ostis-ann/bin /ostis-ann/bin
COPY --from=builder /ostis-ann/scripts /ostis-ann/scripts
COPY --from=builder /ostis-ann/ostis-ann.ini /ostis-ann/ostis-ann.ini

WORKDIR /ostis-ann/scripts
ENTRYPOINT ["/usr/bin/tini", "--", "/ostis-ann/problem-solver/sc-machine/scripts/docker_entrypoint.sh"]
