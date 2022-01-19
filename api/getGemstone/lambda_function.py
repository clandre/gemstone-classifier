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
    
    if event["headers"]["authorization"] == token:
        body = json.loads(event["body"])
        gemstone = body["gemstone"]
        gemstone_data = get_gemstone(gemstone)

        return {"status": 200, "data": gemstone_data}
    else:
        return {"status": 401, "data": {}}
    
def get_gemstone(gemstone_name: str):

    db = client["gemstone-classifier"]

    collection = "gemstone"
    gemstone_collection = db[collection]
    result = gemstone_collection.find_one({"_id": gemstone_name})
    
    if result is None:
        return json.dumps("{}")
    else:
        return result
    