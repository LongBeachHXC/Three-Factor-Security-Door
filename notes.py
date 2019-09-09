import sys
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
import json
from random import randint
from evdev import InputDevice
from select import select
from door_lock_db import DoorLockDB
import RPi.GPIO as GPIO
import json
from random import randint
from evdev import InputDevice
from select import select
from door_lock_db import DoorLockDB
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import tempfile


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

rek_client = boto3.client('rekognition')

# kinesisClient = boto3.client('kinesis')

maxResults=2
collectionId='Forrest_Weinberg'

aws_data_holder = []

def createRekCollection(collectionId):
    response=rek_client.create_collection(CollectionId=collectionId)
    return response

def listRekCollection(maxResults):
    response=rek_client.list_collections(MaxResults=maxResults)
    while True:
        collections = response['CollectionIds']
        
        for collection in collections:
            return collection
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response=rek_client.list_collections(NextToken=nextToken,MaxResults=maxResults)
        
        else:
            break

def describeRekCollection(collectionId):
    collection_obj = {}
    try:
        response=rek_client.describe_collection(CollectionId=collectionId)
        collection_obj['collectionArn'] = response['CollectionARN']
        collection_obj['faceCount'] = str(response['FaceCount'])
        collection_obj['faceModelVer'] = response['FaceModelVersion']
        collection_obj['timeStamp'] = str(response['CreationTimestamp'])
        return(collection_obj)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return(f'The collection {collectionId} was not found')
        else:
            error_response = e.response['Error']['Message']
            return(f'Error other than Not Found occured {error_response}')

def deleteRekCollection(collectionId):
    '''
    Function to delete aws rekognition collections. Input parameters is as follows:
        {
            'collectionId': 'string'
        }
    '''
    statusCode = ''
    response = ''
    try:
        response = rek_client.delete_collection(CollectionId=collectionId)
        statusCode=response['StatusCode']
        response = statusCode
        return(response)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            response = f'The collection {collectionId} was not found'
        else:
            error_response = e.response['Error']['Message']
            response = f'Error other than Not Found occured {error_response}'
        statusCode = e.response['ResponseMetadata']['HTTPStatusCode']
        return(response, statusCode)

def addFaceToCollection(collectionId, image_url, externalImageId, maxFaces=1, qualityFilter='AUTO', detectionAttributes = ['ALL']):
        '''
        Function to add images to a collection. Input parameters are as follows:
            {
                'collectionId': 'string',
                'image_url': 'string',
                'externalImageId': 'string',
                'maxFaces': int,
                'qualityFilter': 'string',
                'detectionAttributes': 'string'
            }
        '''

        image = requests.request('GET', image_url)
        image_bytes = image.content
        response = rek_client.index_faces(
            CollectionId=collectionId, 
            Image={'Bytes': image_bytes}, 
            ExternalImageId=externalImageId, 
            MaxFaces=maxFaces, 
            QualityFilter=qualityFilter, 
            DetectionAttributes=detectionAttributes
        )
        return(response)

def listFacesInCollection(collectionId, maxResults=10):
    data_holder = []
    tokens = True
    response = rek_client.list_faces(CollectionId=collectionId, MaxResults=maxResults)
    while tokens:
        faces = response['Faces']
        for face in faces:
            data_holder.append(face)
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = rek_client.list_faces(CollectionId=collectionId, NextToken=nextToken, MaxResults=maxResults)
            data_holder.append(response)
        else:
            tokens = False
    return(data_holder)

def deleteFacesInCollection(collectionId, faceIds):
    data_holder = []
    response = rek_client.delete_faces(CollectionId=collectionId, FaceIds=faceIds)
    deleted_faces = response['DeletedFaces']
    deleted_faces_string = f'Deleted {str(len(deleted_faces))} from {collectionId}'
    for faceId in response['DeletedFaces']:
        data_holder.append(faceId)
    return(deleted_faces_string, data_holder)

base_path = Path('.')

with tempfile.TemporaryDirectory() as tmpdirname:
    with open(base_path.join(tmpdirname), 'project.json'), 'w') as outfile:
        json.dump(projectDetailsJSON, outfile)
    
    for dirname, subdirs, files in os.walk(tmpdirname):
        for filename in files:
            new_archive.write(os.path.join(tmpdirname, filename), filename)


sourceFile = 'Professional Headshot (Cropped).jpg'
targetFile = 'anotherPicOfMe.jpg'

imageSource=open(sourceFile,'rb')
imageTarget=open(targetFile,'rb')

response=client.compare_faces(
    SimilarityThreshold=70,
    SourceImage={
    'Bytes':imageSource.read()
    },
    TargetImage={
        'Bytes':imageTarget.read()
    })

for faceMatch in response['FaceMatches']:
    print(faceMatch)


few_image_id = '5d6ee69f65b8202400003bd0'
few_image_url = 'https://cvtest-f0a7.restdb.io/media/5d6ee69f65b8202400003bd0' 

{
    'StatusCode': 200, 
    'CollectionArn': 'aws:rekognition:us-west-1:457124630871:collection/Forrest_Weinberg', 
    'FaceModelVersion': '4.0', 
    'ResponseMetadata': {
        'RequestId': '6daed936-7661-410c-b933-9ad31f2e2ad8', 
        'HTTPStatusCode': 200, 
        'HTTPHeaders': {
            'content-type': 'application/x-amz-json-1.1', 
            'date': 'Thu, 05 Sep 2019 15:20:32 GMT', 
            'x-amzn-requestid': '6daed936-7661-410c-b933-9ad31f2e2ad8', 
            'content-length': '128', 
            'connection': 'keep-alive'
        }, 
        'RetryAttempts': 0
    }
}