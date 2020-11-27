import os
import requests

from neural_networks.ann_app_base import AnnAppBase


class AnnApp(AnnAppBase):

    def process(self, path):
        f_path = open(os.path.abspath(path), 'rb')
        file = {'file': f_path}
        quality = requests.post('http://localhost:8080/classify', files=file)
        return quality.text
