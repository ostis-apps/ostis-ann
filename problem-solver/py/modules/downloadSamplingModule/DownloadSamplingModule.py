from sc_kpm import ScModule
from modules.downloadSamplingModule.DownloadSamplingAgent import DownloadSamplingSolver


class DownloadSamplingModule (ScModule):
    def __init__(self):
        super().__init__(DownloadSamplingSolver()) 