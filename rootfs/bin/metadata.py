#!/usr/bin/env python3
import requests
import logging
import os
import sys
import json
import argparse

headers = {
    'Content-Type': 'application/json'
}

basic_auth = ('', os.environ.get('AUTH_TOKEN'))

LOGGING_LEVEL = logging.INFO
if os.environ.get('DEBUG'):
    LOGGING_LEVEL = logging.DEBUG

def env_payload():
    return {
        'kubeRef': os.environ.get('POD_NAME'),
        'source': os.environ.get('GIT_SOURCE'),
        'gitBranch': os.environ.get('GIT_BRANCH'),
        'headCommit': {
            'id': os.environ.get('COMMIT'),
            'author': os.environ.get('COMMIT_AUTHOR'),
            'message': os.environ.get('COMMIT_MSG'),
            'avatar-url': os.environ.get('GIT_AUTHOR_AVATAR'),
            'compare': os.environ.get('GIT_COMPARE'),
            'url': os.environ.get('GIT_COMMIT_URL')
        }
    }

def clear_release_payload():
    return {
        'kubeRef': os.environ.get('POD_NAME'),
        'source': os.environ.get('GIT_SOURCE')
    }

def update_release_metadata(url, payload):
    response = requests.put(url, json=payload, headers=headers, auth=basic_auth)
    return is_success(response)

def create_release(url, payload):
    return requests.post(url, json=payload, headers=headers, auth=basic_auth)

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

def echo_title(msg):
    set_logging_title()
    logging.info(msg)
    set_logging_normal()

def is_success(response):
    echo_normal('Status Code={}, API Response={}'.format(
        response.status_code,
        response.text
    ))
    # Don't mind if the release already exists (409)
    return response.status_code in (200, 201, 204, 409)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['update', 'create'], required=True)
    parser.add_argument('--field', action='append')
    parser.add_argument('--git-api-url', required=True)
    args = parser.parse_args()

    if LOGGING_LEVEL == logging.DEBUG:
        echo_title('Printing environment data')
        for key, value in env_payload().items():
            echo_normal('{}: {}'.format(key, json.dumps(value)))
    
    if args.action == 'update':
        payload = {}
        if not args.field:
            echo_normal('Missing "--field=key=value" argument')
            sys.exit(1)
        for attr in args.field:
            key, value = attr.split('=', 1)
            payload[key] = value
        if not update_release_metadata(args.git_api_url, payload):
            sys.exit(1)
    elif args.action == 'create':
        echo_title('Creating new release ...')
        resp = create_release(args.git_api_url, env_payload())
        if resp.status_code == 409:
            echo_normal('The release already exists, updating ...')
            payload = clear_release_payload()
            commit_id = os.environ.get('COMMIT') or ''
            url = '{}/{}'.format(args.git_api_url, commit_id)
            if not update_release_metadata(url, payload):
                sys.exit(1)
        else:
            if not is_success(resp):
                sys.exit(1)
