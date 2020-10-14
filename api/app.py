import importlib
import os

import requests
from flask import Flask, jsonify, request
from utils.config_utils import ConfigManager

app = Flask(__name__)
app.config.from_pyfile('api_config.cfg')
config_provider = ConfigManager(app)
module_data_path = './neuromodules/data/'


@app.route('/<ann_id>/extensions', methods=['GET'])
def get_supported_extensions(ann_id):
    extensions = config_provider.get_supported_extensions(ann_id)
    return jsonify(extensions)


@app.route('/<module>/<ann_id>/data', methods=['POST'])
def upload_data(module, ann_id):
    if 'file' not in request.files:
        message = {
            'status': requests.codes.bad_request,
            'message': 'No file provided',
        }
        response = jsonify(message)
        return response

    file = request.files['file']
    path = config_provider.get_upload_data_path(module, ann_id)
    file.save(os.path.join(path, file.filename))

    message = {
        'status': requests.codes.ok
    }

    return jsonify(message)


@app.route('/<ann_id>', methods=['GET'])
def properties(ann_id):
    properties_string = config_provider.get_ann_properties(ann_id)

    return jsonify(properties_string)


@app.route('/<ann_id>', methods=['POST'])
def process(ann_id):
    path = config_provider.get_upload_data_path(ann_id)
    filename = os.path.join(path, request.json['filename'])

    ann_realization = importlib.import_module(f'neuromodules.{ann_id}.ann_app')
    ann_app = ann_realization.AnnApp()
    processed_data = ann_app.process(filename)

    return jsonify(processed_data)


if __name__ == '__main__':
    app.run()
