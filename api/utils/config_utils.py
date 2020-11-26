import json
import os
from utils.json_utils import *


class ConfigManager:
    def __init__(self, receiver_app):
        self.receiver_app = receiver_app

    def get_supported_extensions(self, ann_id):
        filename = os.path.join(self.receiver_app.static_folder, self.receiver_app.config['EXTENSIONS_FILE_NAME'])
        with open(filename) as extensions_raw:
            ext_json = json.loads(extensions_raw.read())
            return get_value_by_key_sequence(ext_json, [ann_id])

    def get_ann_properties(self, ann_id):
        filename = os.path.join(self.receiver_app.static_folder, self.receiver_app.config['PROPERTIES_FILE_NAME'])
        with open(filename) as properties_raw:
            ext_json = json.loads(properties_raw.read())
            return get_value_by_key_sequence(ext_json, [ann_id])

    def get_upload_data_path(self, ann_id):
        path = os.path.join(self.receiver_app.config['NEURAL_NETWORKS_PATH'], ann_id, 'data')
        return path
