#!/usr/bin/env python3
import requests
import logging
import os
import sys
import json
import argparse


basic_auth = ('', os.environ.get('AUTH_TOKEN'))

LOGGING_LEVEL = logging.INFO
if os.environ.get('DEBUG'):
    LOGGING_LEVEL = logging.DEBUG

def remove_root_handlers():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def set_logging_title():
    remove_root_handlers()
    logging.basicConfig(format='-----> %(message)s', level=LOGGING_LEVEL)

def set_logging_normal():
    remove_root_handlers()
    logging.basicConfig(format='       %(message)s', level=LOGGING_LEVEL)

def echo_normal(msg):
    set_logging_normal()
    logging.info(msg)

def echo_debug(msg):
    set_logging_normal()
    logging.debug(msg)

def echo_title(msg):
    set_logging_title()
    logging.info(msg)
    set_logging_normal()

def upload_file(url, file_path):
    ''' Post a Multipart-Encoded File
    '''
    f = open(file_path, 'rb')
    payload = {'file': (os.path.basename(f.name), f)}
    resp = requests.post(url, files=payload, auth=basic_auth)
    f.close()
    return is_success(resp)

def is_success(response):
    if response.status_code in (200, 201, 204):
        echo_debug('Status Code: {} Response: {}'.format(
            response.status_code, response.text
        ))
        return True
    else:
        echo_normal('Status Code: {} Response: {}'.format(
            response.status_code, response.text
        ))
        return False

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--file', required=True)
        parser.add_argument('--git-api-url', required=True)
        args = parser.parse_args()
        echo_title('Uploading {} ...'.format(os.path.basename(args.file)))
        if not upload_file(args.git_api_url, args.file):
            sys.exit(1)
    except Exception as e:
        echo_normal('Failed uploading file: {}'.format(e))
        sys.exit(1)

