import csv
import os
import requests

from ...neural_networks.ann_app_base import AnnAppBase
from .data_processing.data_processing_module import DataProcessingModule


class AnnApp(AnnAppBase):

    @staticmethod
    def writeToTsv(path, uniformity, mass_fat_fraction, mass_protein_fraction, has_mold):
        out_file = open(path, 'wt')
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(['Uniformity', 'Mass fat fraction', 'Mass protein fraction', 'Has mold'])
        tsv_writer.writerow([uniformity, mass_fat_fraction, mass_protein_fraction, has_mold])

    def process(self, path):
        module = DataProcessingModule()
        uniformity, mass_fat_fraction, mass_protein_fraction, has_mold = module.parseInputData(path)
        self.writeToTsv(path, uniformity, mass_fat_fraction, mass_protein_fraction, has_mold)

        f_path = open(os.path.abspath(path), 'rb')
        file = {'file': f_path}
        quality = requests.post('http://localhost:8080/classify', files=file)

        module.processAnswer(path, quality)
        return quality.text
