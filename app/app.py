# Common python package imports.
from flask import Flask, jsonify, request, render_template,Response
import os 
import jsonpickle
import numpy as np 
import cv2 
from cloud_ocr.google_vision_main import detect_text

# Kill the server 
# kill -9 $(lsof -t -i:5000)

list_extensions = [".jpeg",".png",".jpg",".bmp",".PNG",".JPEG",".JPG",".BMP"]

# Initialize the app and set a secret_key.
app = Flask(__name__)


@app.route("/api/info", methods=['POST'])
def getID():
        
    # decode image
    data = request.get_json(force=True) 
    input_path = str(data['data']).replace('\n','').strip()
    ext = os.path.splitext(input_path)[1]
    num_choice = int(str(data['choice']).strip())
    # check the extension of input data 
    if ext in list_extensions and (num_choice == 1 or num_choice == 3):
        # get card_id,name,dob from input image 
        card_id,name,dob = detect_text(num_choice,input_path)

        # build a response dict to send back to client
        response = {'id': card_id,'name': name,'dob': dob}
        return jsonify(response)

    else:
        response = {'id': None,'name': None,'dob': None}
        return jsonify(response)

if __name__ == "__main__":
    # start flask app
    app.run(port='5000',debug=True,host='0.0.0.0')