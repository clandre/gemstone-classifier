import json
import os
from pymongo import MongoClient

username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
host = os.environ.get('HOST')
db = os.environ.get('DB')
token = os.environ.get("TOKEN")

client = MongoClient("mongodb+srv://{0}:{1}@{2}/{3}?retryWrites=true&w=majority".format(username, password, host, db))


def lambda_handler(event, context):
    """
        Function to handle request

        Parameters
        ----------
            event:
                Request event
            context:
                Additional information from request

        Returns
        -------
            response (dict): Response from request
    """
    
    if event["headers"]["authorization"] == token:
        body = json.loads(event["body"])
        gemstone = body["gemstone"]
        gemstone_data = get_gemstone(gemstone)

        response = {"statusCode": 200, "data": gemstone_data}
    else:
        response = {"statusCode": 401, "data": {}}
        
    response["headers"] = {
            "Content-Type": "application/json"
            }

    return json.dumps(response)
    
def get_gemstone(gemstone_name: str):

    """
    Get gemstone

    Parameters
    ----------

        gemstone_name: str
            Gemstone name
    
        Returns
        -------
            gemstone (dict): Gemstone record if exists
    """

    db = client["gemstone-classifier"]

    collection = "gemstone"
    gemstone_collection = db[collection]
    result = gemstone_collection.find_one({"_id": gemstone_name})
    
    if result is None:
        return json.dumps("{}")
    else:
        return result
    