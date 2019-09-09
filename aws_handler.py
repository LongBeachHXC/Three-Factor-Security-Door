from pathlib import Path
from dotenv import load_dotenv
import os
import requests
import boto3
from botocore.exceptions import ClientError

# Explicitly providing path to '.env'
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

class AwsHandler():

    def __init__(self, *args, **kwargs):
        self.rek_client = boto3.client('rekognition')
    
    def createRekCollection(self, collectionId):
        response=self.rek_client.create_collection(CollectionId=collectionId)
        return response

    def listRekCollection(self, maxResults):
        data_holder = []
        response=self.rek_client.list_collections(MaxResults=maxResults)
        while True:
            collections = response['CollectionIds']
            
            for collection in collections:
                data_holder.append(collection)
            if 'NextToken' in response:
                nextToken = response['NextToken']
                response=self.rek_client.list_collections(NextToken=nextToken,MaxResults=maxResults)
            
            else:
                return(data_holder)

    def describeRekCollection(self, collectionId):
        collection_obj = {}
        try:
            response=self.rek_client.describe_collection(CollectionId=collectionId)
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

    def deleteRekCollection(self, collectionId):
        statusCode = ''
        response = ''
        try:
            response=self.rek_client.delete_collection(CollectionId=collectionId)
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
    
    def addFaceToCollection(self, collectionId, image_url, externalImageId, maxFaces=1, qualityFilter='AUTO', detectionAttributes = ['ALL']):
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
        response = self.rek_client.index_faces(
            CollectionId=collectionId, 
            Image={'Bytes': image_bytes}, 
            ExternalImageId=externalImageId, 
            MaxFaces=maxFaces, 
            QualityFilter=qualityFilter, 
            DetectionAttributes=detectionAttributes
        )
        return(response)

    def listFacesInCollection(self, collectionId, maxResults=10):
        data_holder = []
        tokens = True
        response = self.rek_client.list_faces(CollectionId=collectionId, MaxResults=maxResults)
        while tokens:
            faces = response['Faces']
            for face in faces:
                data_holder.append(face)
            if 'NextToken' in response:
                nextToken = response['NextToken']
                response = self.rek_client.list_faces(CollectionId=collectionId, NextToken=nextToken, MaxResults=maxResults)
                data_holder.append(response)
            else:
                tokens = False
        return(data_holder)

    def deleteFacesInCollection(self, collectionId, faceIds):
        data_holder = []
        response = self.rek_client.delete_faces(CollectionId=collectionId, FaceIds=faceIds)
        deleted_faces = response['DeletedFaces']
        deleted_faces_string = f'Deleted {str(len(deleted_faces))} from {collectionId}'
        for faceId in response['DeletedFaces']:
            data_holder.append(faceId)
        return(deleted_faces_string, data_holder)

# CreateCollection
# IndexFaces(SpecifyCollection)
# # Allows to search streaming video
# CreateStreamProcessor

