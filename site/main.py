import os
import sys
from importlib import reload
import random

import streamlit as st
from PIL import Image
import requests
import base64
import json

import os.path as osp
sys.path.append(osp.dirname(os.getcwd()))
reload(sys)


def load_image(image_file):
    return Image.open(image_file)


def send_request(url, bytes_data, headers):
    response = requests.post(url, data=json.dumps(bytes_data), headers=headers).json()
    return response

def main():

    st.title('Gemstone Classifier')

    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        show_file = st.empty()

        # Convert to base64 representation
        img_b64 = base64.b64encode(bytes_data)
        
        # Show image uploaded
        _, col2, _ = st.columns(3)
        with col2:
            st.write("Image preview")
            st.image(uploaded_file)

    # Make request to model
    button = st.button("Classify")

    if uploaded_file is not None and button == True:
        
        # Response from model via api
        gemstone_predict = None
        gemstone_predict = random.choice(["Agate", "Alexandrite", "Almandine", "Amazonite", "Amber"])

        payload_dict = {"gemstone": gemstone_predict}
        headers_dict = {'Content-Type':'application/json', 'Authorization': os.environ.get("AUTH_TOKEN")}

        # Retreieve information from gemstone api
        response = send_request("https://ellrby6m1a.execute-api.us-east-2.amazonaws.com/getGemstone", payload_dict, headers_dict)

        if response["status"] != 200:
            st.error("Critical failure, contact system admin.")
        else:
            data = response["data"]

            st.header('Classification')

            st.metric(label="Name", value=data["_id"])
            
            st.markdown('<div class="css-1rh8hwn e16fv1kl1">' + 'Chemical Formula' + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="css-1xarl3l e16fv1kl2">' + data["chemical_formula"] + '</div>', unsafe_allow_html=True)
            
            st.subheader('Similar images')        
     

if __name__ == "__main__":
    main()