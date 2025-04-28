"""
json utils for data persistence
"""

import os
import json
import logging
from flask import current_app


def load_json(file_name):
    """
    load data from a json file

    args: file_name (str) -- name of json file to load

    returns: list -- data from json file as A LIST OF DICTS
    """
    try:
        data_folder = current_app.config['DATA_FOLDER']
    except RuntimeError:
        # not in flask context, use default
        data_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

    file_path = os.path.join(data_folder, file_name)

    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # create empty file if it doesn't exist
            with open(file_path, 'w') as f:
                f.write('[]')
            return []
    except json.JSONDecodeError:
        logging.error(f"error decoding json from {file_path}")
        return []


def save_json(file_name, data):
    """
    save data to a json file

    args:
        file_name (str): name of the json file to save to
        data (list): data to save as a list of dictionaries

    returns: bool -- true if save was successful, false otherwise
    """
    try:
        data_folder = current_app.config['DATA_FOLDER']
    except RuntimeError:
        # not in flask context, use default
        data_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

    file_path = os.path.join(data_folder, file_name)

    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"error saving json to {file_path}: {str(e)}")
        return False