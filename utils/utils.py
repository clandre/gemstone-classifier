import os

import yaml
import boto3
from botocore.exceptions import ClientError
from pymongo import MongoClient


def create_dir(path: str):
    # Create dir if not exits

    return os.makedirs(path, exist_ok=True)


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def upload_file(credentials: dict, file_name:str , object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client(
        's3',
        aws_access_key_id = credentials['S3']['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key = credentials['S3']['AWS_SECRET_ACCESS_KEY']
    )

    try:
        response = s3_client.upload_file(file_name, credentials['S3']['BUCKET'], object_name)
    except ClientError as e:
        return False
    return True


def insert_gemstone(credentials: dict, collection:str, identifier:str, document: dict):
    
    client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(credentials['DATABASE']['USERNAME'], credentials['DATABASE']['PASSWORD'], credentials['DATABASE']['HOST'], credentials['DATABASE']['DB']))

    db = client["gemstone-classifier"]
    gemstone = db[collection]
    updated = gemstone.update_one({"_id": identifier}, {"$set": document}, upsert = True)

    if updated:
        return True
    else:
        return False


