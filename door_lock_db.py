# door_lock_db.py

from pathlib import Path
from dotenv import load_dotenv
import os
import requests
import json
from base64 import b64encode, b64decode
# from PIL import Image

# Explicitly providing path to '.env'
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

DB_API_KEY = os.getenv('DB_API_KEY')

DB_BASE_URI = 'https://doorlock-be53.restdb.io'
db_rest_uri = f'{DB_BASE_URI}/rest'
db_media_uri = f'{DB_BASE_URI}/media'
ACCESS_LIST_COLLECTION = '/accesslist'
ACCESS_LOG_COLLECTION = '/accesslog'

base_uri = db_rest_uri
media_uri = db_media_uri
db_api_key = DB_API_KEY
access_list_collection = ACCESS_LIST_COLLECTION
access_log_collection = ACCESS_LOG_COLLECTION
headers = {
    'content-type': "application/json",
    'x-apikey': db_api_key,
    'cache-control': "no-cache"
}

class _DoorLockDB:

    global base_uri
    global db_api_key
    global access_list_collection
    global access_log_collection
    global headers

    def __str__(self):
        return 'Helper Class for Door Lock DB Operations'

    def get_to_db(self, endpoint='/', query=None, headers=headers):
        print(f'The endpoing: {endpoint}')
        print(f'The headers: {headers}')
        print(f'The query that is being sent: {query} (type: {type(query)}')

        if endpoint == 'alist':
            url = f'{base_uri}{access_list_collection}'
        elif endpoint == 'alog':
            url = f'{base_uri}{access_log_collection}'
        else:
            url = f'{base_uri}{endpoint}'

        if query != None:
            payload = json.dumps(query)
            # print(query)
            url += f'?q={payload}'
        else:
            pass

        print(f'Final URL: {url}')
        # print(f'Final data payload: {payload}')

        response = requests.request('GET', url, headers=headers)
        return response.json()

    def post_new_doc(self, endpoint='/', payload='json dumps', headers=headers):

        if endpoint == 'alist':
            url = f'{base_uri}{access_list_collection}'
        elif endpoint == 'alog':
            url = f'{base_uri}{access_log_collection}'
        else:
            url = f'{base_uri}{endpoint}'
        
        payload = json.dumps(payload)
        
        response = requests.request('POST', url, data=payload, headers=headers)
        return response.json()
    
    def update_doc(self, endpoint, object_id, payload):
        print(f'The endpoing: {endpoint}')
        print(f'The object ID being modified: {object_id}')
        print(f'The data that is being replaced: {payload} (type: {type(payload)}')
        if endpoint == 'alist':
            url = f'{base_uri}{access_list_collection}'
        elif endpoint == 'alog':
            url = f'{base_uri}{access_log_collection}'
        else:
            url = f'{base_uri}{endpoint}'

        url += f'/{object_id}'
        payload = json.dumps(payload)
        print(f'Final URL: {url}')
        print(f'Final data payload: {payload}')

        response = requests.request("PATCH", url, data=payload, headers=headers)
        return response.json()

    def get_image(self, endpoint, image_id):
        if endpoint == 'm':
            url = f'{media_uri}'
        else:
            url = f'{base_uri}{endpoint}'
        url += f'/{image_id}'
        response = requests.request('GET', url, headers)
        return response
    
    def upload_headshot_image(self, endpoint, binary_hex_json, headers=headers):
        binary_hex = json.loads(binary_hex_json)
        image_from_hex = bytes.fromhex(binary_hex)
        # img_decoded = b64decode(binary_str)
        # img = Image.frombytes(img_decoded)
        # binary_blob = img
        if endpoint == 'm':
            url = f'{media_uri}'
        else:
            url = f'{base_uri}{endpoint}'
        
        files = {'file': image_from_hex}
        response = requests.request("POST", url, files=files, headers=headers)
        return response.json()
        
# https://doorlock-be53.restdb.io/media/5d66dbd49ce4772e000063b9

_instance = None

def DoorLockDB():
    global _instance
    if _instance is None:
        _instance = _DoorLockDB()
    return _instance