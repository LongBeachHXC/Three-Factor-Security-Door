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


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client=boto3.client('rekognition')

maxResults=2
collectionId='Forrest Weinberg'

def createRekCollection(collectionId):
    response=client.create_collection(CollectionId=collectionId)
    return response

def listRekCollection(maxResults):
    response=client.list_collections(MaxResults=maxResults)
    while True:
        collections = response['CollectionIds']
        
        for collection in collections:
            return collection
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response=client.list_collections(NextToken=nextToken,MaxResults=maxResults)
        
        else:
            break

def describeRekCollection(collectionId):
    collection_obj = {}
    try:
        response=client.describe_collection(CollectionId=collectionId)
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
    statusCode = ''
    response = ''
    try:
        response=client.delete_collection(CollectionId=collectionId)
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

def addFaceToCollection(collectionId, image_url, externalImageId, maxFaces=1, qualityFilter='AUTO', detectionAttributes = ['ALL'])


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