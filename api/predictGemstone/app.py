import json
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model

def read_model():
    """
    Function to read model at local file system

        Returns
        -------
            model, gemstone_enc (keras.model, dict): Keras model and categorycal encoding of gemstone
    """

    model = load_model("model.h5")
    with open("gemstone_enc.json", "r") as f:
        gemstone_enc = json.loads(f.read())

    return (model, gemstone_enc)

def process_image(image):
    """
    Function to process image

        Parameters
        ----------
            image:
                Image to be processed

        Returns
        -------
            image (np.array): Image processed
    """    


    img_w = img_h = 300

    # Resize images
    image = cv2.resize(image, (img_w, img_h))
    # Convert image from default BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return np.array([image])


# Read model
model, gemstone_enc = read_model()

def handler(event, context):
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