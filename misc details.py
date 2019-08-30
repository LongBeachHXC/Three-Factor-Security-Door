

db.get_to_db('alist','Forrest Weinberg')

import zlib
from PIL import Image
from door_lock_db import DoorLockDB
db = DoorLockDB()
from base64 import b64encode, b64decode
import sys
import json

image = open("Professional Headshot (Cropped).jpg", 'rb')
read_image = image.read()
image_hex = read_image.hex()
image_json = json.dumps(image_hex)
db.upload_headshot_image('m', image_json)

im = Image.open("Professional Headshot (Cropped).jpg")

img_bytes = im.tobytes()

response = db.upload_headshot_image('--m', img_bytes)

b64_image = b64encode(im.tobytes())
b64_str_image = str(b64_image)
b64_json = json.dumps(b64_str_image)
(width, height) = (200, 200)

# im_resized = im.resize((width, height))
im.thumbnail(200)

im.save('im_resized.jpg', quality=95, optimize=True)

resized_im = Image.open('im_resized.jpg')
b64_resized_image = b64encode(resized_im.tobytes())
b64_str_resized_image = str(b64_resized_image)

print(f'Here is a comparison of the the size:\nOriginal: {sys.getsizeof(b64_str_image)}\nNew File: {sys.getsizeof(b64_str_resized_image)}')

with open('Professional Headshot (Cropped).jpg', 'rb') as image:
    im = image.read()

compressed_image = zlib.compress(im, 9)

b64_image = b64encode(im2.tobytes())
b64_str = str(b64_image)
b64_json = json.dumps(str(_))

im.save('working_image.png', format='PNG')

db.post_new_doc('https://doorlock-be53.restdb.io/media', b64_json)
db.post_new_doc('https://doorlock-be53.restdb.io/media', b64_str)


import requests
latest_file = './image.jpeg'
headers = {'x-apikey': '{MY_API_KEY_HERE}'}
url = "https://{MYDATABASE_NAME_HERE}.restdb.io/media"
files = {'file': open(latest_file, 'rb')}
r = requests.post(url, files=files, headers=headers)
print(r.status_code, r.text)


sys.getsizeof(im_base64)

'5d6701b79ce4772e00006715'

db.update_doc('alist','5d6701b79ce4772e00006715', {'image':'5d66dbd49ce4772e000063b9'})
db.get_to_db('alist')