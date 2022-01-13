import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import base64


def load_image(image_file):
    return Image.open(image_file)


def send_request(bytes_data):
    response = requests.post("https://postman-echo.com/post", data=bytes_data)
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
        response = requests.post("https://e7rmlkcdr0.execute-api.us-east-2.amazonaws.com/default/getGemstone", data=img_b64)
        
        json_response = response.json()

        st.header('Classification')

        st.metric(label="Name", value=json_response["_id"])
        st.metric(label="Chemical Formula", value=json_response["chemical_formula"])

        
        st.subheader('Similar images')
        
     

if __name__ == "__main__":
    main()