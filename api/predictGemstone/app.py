import json
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import boto3
import os
from tensorflow import keras

def read_model():
    s3 = boto3.resource("s3", 
                    aws_access_key_id = os.environ.get("ACCESS_KEY_ID"),
                    aws_secret_access_key = os.environ.get("SECRET_ACCESS_KEY")
                    )
    bucket = s3.Bucket(os.environ.get("BUCKET"))
    try:
        bucket.download_file("model/model.h5", "/tmp/model.h5")
        bucket.download_file("model/gemstone_enc.json", "/tmp/gemstone_enc.json")
    except Exception as e:
        print("Failed to load model")
        print(e)

    with open("/tmp/gemstone_enc.json", "r") as f:
        gemstone_enc = json.load(f)

    model = keras.models.load_model("/tmp/model.h5")
        
    return (model, gemstone_enc)

def process_image(image):
    img_w = img_h = 330

    # Resize images
    image = cv2.resize(image, (img_w, img_h))
    # Convert image from default BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return np.array([image])


model, gemstone_enc = read_model()

def handler(event, context):

    body = json.loads(event["body"])
    image = body["image"]
    
    jpg_original = base64.b64decode(image)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image = Image.open(BytesIO(base64.b64decode(image)))
    image = cv2.imdecode(jpg_as_np, flags=1)

    # Process image
    image = process_image(image)

    # Predict gemstone
    predict = model.predict(image)
    index_predict = np.argmax(predict[0])

    response = {
        "headers": {
            "Content-Type": "application/json"
            },
        "statusCode": 200,
        "data": {
            "gemstone": str(gemstone_enc[str(index_predict)]),
            "probability": str(predict[0][index_predict])
        }
    }

    return json.dumps(response)