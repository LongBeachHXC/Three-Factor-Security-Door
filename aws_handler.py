from pathlib import Path
from dotenv import load_dotenv
import os
import boto3

# Explicitly providing path to '.env'
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

class AwsHandler():

    def __init__(self, *args, **kwargs):
        self.rek_client = boto3.client('rekognition')
        

CreateCollection
IndexFaces(SpecifyCollection)
# Allows to search streaming video
CreateStreamProcessor

