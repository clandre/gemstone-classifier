# -*- coding: utf-8 -*-

"""
Script used to update list of images at database after manipulation direct on S3

"""

import yaml

import boto3
from pymongo import MongoClient

def read_images(credentials: dict) -> dict:
    """
    Function to read image from S3

    Parameters
    ----------

        credentials: dict
            credentials to connect no database

    Returns
    -------
        gemstone (dict): Gemstone name and images

    """

    s3 = boto3.resource("s3", 
                        aws_access_key_id = credentials['S3']['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key = credentials['S3']['AWS_SECRET_ACCESS_KEY']
                    )
    bucket = s3.Bucket(credentials['S3']['BUCKET'])

    gemstone_images = {}

    for bucket_object in bucket.objects.all():
        try:
            filename = bucket_object.key.strip()
            if filename.startswith("images/") and not(filename.endswith(".json")):
                if len(filename.split('/')) == 3:
                    _, gemstone, name = filename.split('/')
                    
                    # Check if is a file
                    if name != '':
                        if gemstone in gemstone_images.keys():
                            gemstone_images[gemstone].append(filename)
                        else:
                            gemstone_images[gemstone] = [filename]

        except Exception as e:
            print("Can't download file: " + filename)
            print(e)
            
    return gemstone_images

def update_image_list(credentials: dict, gemstone_images: dict) -> None:
    """
    Function to update gemstone record

    Parameters
    ----------

        credentials: dict
            credentials to connect no database
        gemstone_images: dict
            gemstone name and images

    Returns
    -------
        None
    """
    
    client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(credentials['DATABASE']['USERNAME'], credentials['DATABASE']['PASSWORD'], credentials['DATABASE']['HOST'], credentials['DATABASE']['DB']))

    db = client["gemstone-classifier"]
    gemstone = db["gemstone"]
        
    for key, value in gemstone_images.items():
        print("Updating images of " + key)
        gemstone.update_one({"_id": key}, {"$set": {"Images": value}})


def main():
    with open("../utils/config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)                        
        except yaml.YAMLError as exc:
            print(exc)

    gemstone_images = read_images(config)
    update_image_list(config, gemstone_images)


if __name__ == "__main__":
    main()