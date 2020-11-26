import requests

from neural_networks.ann_app_base import AnnAppBase


class AnnApp(AnnAppBase):

    def process(self, path):
        quality = requests.post('http://localhost:8080/classify', data={'file': path})
        print(quality)
        return quality
