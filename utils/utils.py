# -*- coding: utf-8 -*-

import os
import yaml

import boto3
from botocore.exceptions import ClientError
from pymongo import MongoClient


def create_dir(path: str):
    # Create dir if not exits

    return os.makedirs(path, exist_ok=True)


def read_yaml(file_path):
    """
    Function to load yaml configuration file

    Parameters
    ----------

        file_path: str
            File path

    Returns
    ------
        None
    """

    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def upload_file(credentials: dict, file_name:str , object_name=None):
    """
    Upload a file to an S3 bucket

    Parameters
    -----------

        file_name: str
            File to upload
        bucket: str
            Bucket to upload to
        object_name: str
            S3 object name. If not specified then file_name is used

        Returns
        --------
            True if file was uploaded, else False
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
    """
    Function to insert a new gemstone

    Parameters
    ----------

        credentials: dict
            credentials to connect no database
        collection: str
            Collection name
        identifier: str
            Record id
        document: dict
            Document to be inserted
    
        Returns
        -------
            True if record was inserted, else False
    """
    
    client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(credentials['DATABASE']['USERNAME'], credentials['DATABASE']['PASSWORD'], credentials['DATABASE']['HOST'], credentials['DATABASE']['DB']))

    db = client["gemstone-classifier"]
    gemstone = db[collection]
    updated = gemstone.update_one({"_id": identifier}, {"$set": document}, upsert = True)

    if updated:
        return True
    else:
        return False

def update_gemstone_images(credentials: dict, collection:str, identifier:str, images: list):
    """
    Function to update images list of a gemstone

    Parameters
    ----------

        credentials: dict
            credentials to connect no database
        collection: str
            Collection name
        identifier: str
            Record id
        images: list
            List of images
    
        Returns
        -------
            True if record was updated, else False
    """


    client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(credentials['DATABASE']['USERNAME'], credentials['DATABASE']['PASSWORD'], credentials['DATABASE']['HOST'], credentials['DATABASE']['DB']))

    db = client["gemstone-classifier"]
    gemstone = db[collection]

    updated = gemstone.update_one({"_id": identifier}, {"$push": {"Images": images}}, upsert = True)

    if updated:
        return True
    else:
        return False

def get_gemstone(gemstone_name: str):
    """
    Get gemstone

    Parameters
    ----------

        gemstone_name: str
            Gemstone name
    
        Returns
        -------
            gemstone (dict): Gemstone record
    """

    
    with open("..//utils//config.yaml", "r") as stream:
        try:
            credentials = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(credentials['DATABASE']['USERNAME'], credentials['DATABASE']['PASSWORD'], credentials['DATABASE']['HOST'], credentials['DATABASE']['DB']))

    db = client["gemstone-classifier"]

    collection = "gemstone"
    gemstone = db[collection]

    return gemstone.find_one({"_id": gemstone_name})


def retrieve_coordinates_from_countries(credentials):
    """
    Function to discover coordinates from country and update gemstone record

    Parameters
    -----------

        credentials: dict
            credentials to connect no database

        Returns
        --------
            None
    """

    client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(credentials['DATABASE']['USERNAME'], credentials['DATABASE']['PASSWORD'], credentials['DATABASE']['HOST'], credentials['DATABASE']['DB']))

    db = client["gemstone-classifier"]
    countries = db["countries"]
    gemstone = db["gemstone"]

    # Iterate countries and search for gemstones that were encountered there
    countries_list = countries.find()

    for country in countries_list:
        # Get gemstone by country
        gemstone_list = gemstone.find({"source": {"$regex": country["name"], "$options": "i" }})

        # Update gemtone localities
        for gem in gemstone_list:
            gemstone.update_one({"_id": gem["_id"]}, {"$push": {"localities": {"latitude": country["latitude"], "longitude": country["longitude"]}}})