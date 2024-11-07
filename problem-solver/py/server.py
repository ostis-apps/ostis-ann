import argparse
import time
from threading import Thread

import sc_kpm
from sc_client.client import create_elements
from sc_client.constants import sc_types
from sc_client.models import ScConstruction
from sc_client.models import ScLinkContent, ScLinkContentType
from sc_kpm import ScServer
from modules.fnnProcessingModule.FnnInterpreterModule import FnnInterpreterModule
from modules.fnnProcessingModule.FnnTrainingModule import FnnTrainingModule
from pathlib import Path

SC_SERVER_PROTOCOL = "protocol"
SC_SERVER_HOST = "host"
SC_SERVER_PORT = "port"

SC_SERVER_PROTOCOL_DEFAULT = "ws"
SC_SERVER_HOST_DEFAULT = "localhost"
SC_SERVER_PORT_DEFAULT = "8090"


def init_trainer():
    time.sleep(1.5)

    construction = ScConstruction()  # First you need initialize

    question_initiated_addr = sc_kpm.ScKeynodes['question_initiated']
    train_mnist_fashion_addr = sc_kpm.ScKeynodes['train_mnist_fashion']

    construction.create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, question_initiated_addr, train_mnist_fashion_addr)

    addrs = create_elements(construction)


def main(args: dict):
    server = ScServer(
        f"{args[SC_SERVER_PROTOCOL]}://{args[SC_SERVER_HOST]}:{args[SC_SERVER_PORT]}")

    with server.connect():
        modules = [
            FnnInterpreterModule(),
            FnnTrainingModule()
        ]
        server.add_modules(*modules)

        thread = Thread(target=init_trainer)
        thread.start()

        with server.register_modules():
            server.serve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--protocol', type=str, dest=SC_SERVER_PROTOCOL, default=SC_SERVER_PROTOCOL_DEFAULT, help="Sc-server protocol")
    parser.add_argument(
        '--host', type=str, dest=SC_SERVER_HOST, default=SC_SERVER_HOST_DEFAULT, help="Sc-server host")
    parser.add_argument(
        '--port', type=int, dest=SC_SERVER_PORT, default=SC_SERVER_PORT_DEFAULT, help="Sc-server port")
    args = parser.parse_args()

    main(vars(args))
