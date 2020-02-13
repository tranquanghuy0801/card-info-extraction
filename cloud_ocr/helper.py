import cv2
from google.cloud import vision
import os
import re
import numpy as np
from urllib.request import urlopen

# Save Google OCR credentials into environment
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'harrytext-ocr.json'
client = vision.ImageAnnotatorClient()

remove_words = ["DKHK", "NO", "TP", "A", "KI", "ĐKHK", "P",
                "Q", "KP", "VNM", "P.", "N°", "NAMESE", "VIETNAMESE","HỌ","HỘ"]
common_words = ["CONG", "HOA", "XA", "HOI",
                "CHU", "NGHIA", "VIET", "NAM", "HO", "CHIEU", "GIAY CHUNG", "MINH", "NHAN", "DAN"]
name_lines = ["Ho", "Họ", "tên", "ten"]

# # Output folder to save cropped images having only name
save_folder = "data/crop_name"

# count the total numbers from the input string
def countNumbers(inputString):
    return sum(c.isdigit() for c in inputString)

# Count upperCase from input string
def countUpperCase(inputString):
    return sum(1 for c in inputString if c.isupper())

# Count number of lowercase from input string
def countLowerCase(inputString):
    return sum(1 for c in inputString if c.islower())

# Return image with url
def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    # download the image, convert it to a NumPy array
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")

    # convert into CV2 format and resize the image
    image = cv2.imdecode(image, readFlag)
    image = cv2.resize(image, (800, 650))

    return image

# Return image with local input path
def read_local_image(input_path):
    image = cv2.imread(input_path)
    image = cv2.resize(image, (800, 650))
    return image

# Return texts with coordinates from Google API
def getTextGoogleOCR(image, language):
    success, encoded_image = cv2.imencode('.jpg', image)
    content = encoded_image.tobytes()

    image = vision.types.Image(content=content)

    image_context = vision.types.ImageContext(language_hints=[language])

    response = client.text_detection(
        image=image,
        image_context=image_context
    )
    texts = response.text_annotations

    return texts

# Cropped the input image (input_image) based list of coordinates (coord_list)  
def cropped_image(coord_list, input_image):
    start_point = eval(coord_list[list(coord_list.keys())[0]][0])
    print(start_point)
    end_point = eval(coord_list[list(coord_list.keys())[-1]][2])
    print(end_point)
    img_crop_name = input_image[list(start_point)[
        1]-10:list(end_point)[1]+10, list(start_point)[0]-10:list(end_point)[0]+15, :]
    return img_crop_name

# return filtered upper_words dict
def filter_dict(upper_words, thresh):
    try:
        # Sort the uppercase words based on distance to thresh
        upper_words = sorted(upper_words.items(), key=lambda k: abs(
            int(round(thresh))-int(re.findall(r'\b\d+\b', k[1][0])[1])), reverse=False)
        print(upper_words)
        if len(upper_words) > 0:
            # Filter uppercase words with y distance less than 18px
            num_ref = int(re.findall(r'\b\d+\b', upper_words[0][1][1])[1])
            upper_words = {v[0]: v[1] for v in upper_words if abs(
                num_ref - int(re.findall(r'\b\d+\b', v[1][1])[1])) <= 18}

        upper_words = dict((sorted(upper_words.items(), key=lambda k: int(
            re.findall(r'\b\d+\b', k[1][0])[0]))))
    except:
        pass
    return upper_words

# Extract the part of image having only name
def extract_img_name(input_image, upper_words, thresh):
    img_crop_name = None
    try:
        upper_words = filter_dict(input_image, upper_words, thresh)
        print(upper_words)
        img_crop_name = cropped_image(upper_words, input_image)

    except:
        pass
    return img_crop_name

# Save the cropped image having name only
def save_cropped_name(image, input_path, num_choice):

    if image is not None:
        if int(num_choice) == 1 or int(num_choice) == 3:
            print(save_folder + '/crop_output.jpg')
            cv2.imwrite(save_folder + '/crop_output.jpg', image)
        elif int(num_choice) == 2:
            print(save_folder + '/crop_' + input_path.split('/')[-1])
            cv2.imwrite(save_folder + '/crop_' +
                        input_path.split('/')[-1], image)
