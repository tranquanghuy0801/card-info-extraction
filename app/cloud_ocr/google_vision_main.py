from unidecode import unidecode
from cloud_ocr.helper import (read_local_image, url_to_image, countLowerCase, countNumbers, countUpperCase, getTextGoogleOCR, remove_words, common_words, name_lines,
                    process_upper_words, save_cropped_name, extract_img_name, save_folder)
import io
from urllib.request import urlopen
from datetime import datetime
import numpy as np
import argparse
import os
import cv2
import re
import glob


# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--input", required=True,
#                 help="the input folder containing images for OCR")
# ap.add_argument("-o", "--output",
#                 help="the output folder containing json file")
# ap.add_argument("-c", "--choice", required=True,
#                 help="1: process single ID image, 2: process a folder of ID images, 3: process passport image")
# args = vars(ap.parse_args())

passport_letters = ["C","B","N","c","n","b"]

# Return name in the image
def getName(image):
    if image is not None:
        name = unidecode(getTextGoogleOCR(image, "vi")
                         [0].description.split('/n')[0].replace("HỌ","").replace("Họ",""))
        name = re.sub('[^A-Za-z0-9]+', ' ', name)
        name = name.rstrip().lstrip()
        name = ' '.join(word for word in name.split(
            ' ') if countUpperCase(word) == len(word))
        return name
    else:
        return None


def getDOBDirect(text, num_list):
    if (countNumbers(text.description) == 8 or countNumbers(text.description) == 7) and (text.description.find('/') != -1 or text.description.find('-') != -1):
        if text.description.find('/') != -1:
            num_list.append(re.sub('[^0-9/]+', '', text.description))
        elif text.description.find('-') != -1:
            text.description = text.description.replace('-', '/')
            num_list.append(re.sub('[^0-9/]+', '', text.description))
    return num_list


def getDOBSeparate(text, dob_list):
    if countNumbers(text.description) <= 8 and countNumbers(text.description) > 1 and countLowerCase(text.description) == 0 and countUpperCase(text.description) == 0:
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                     for vertex in text.bounding_poly.vertices])
        dob_list[text.description] = vertices
    return dob_list


# Extract name, card ID and DOB from each image

def detect_text(num_choice, input_data, save_path=save_folder):
    """Detects text in the file."""

    # Initialize variables
    thresh_dob_pp = None
    thresh_name_pp = None
    card_id = None
    name = None
    dob = None
    num_list = []
    dob_list = {}
    upper_list = {}

    # Use local image
    # image = read_local_image(input_data)

    # Use url to read image
    image  = url_to_image(input_data)
    cv2.imwrite('output.png', image)

    # Get all text read by Google OCR
    texts = getTextGoogleOCR(image, "vi")

    if len(texts) > 0:
        print('Texts:')
        for text in texts:
            # Remove special symbols
            text.description = re.sub(
                '[@_!#$%^&*()<>?\|}{~:.]', ' ', text.description)
            print(text.description)
            if text.description.find("Full") != -1 and int(num_choice) == 3:
                thresh_name_pp = text.bounding_poly.vertices[0].y
            elif text.description in name_lines and (int(num_choice) == 1 or int(num_choice) == 2):
                thresh_name_pp = text.bounding_poly.vertices[0].y

            if text.description.find("Sex") != -1:
                thresh_dob_pp = text.bounding_poly.vertices[0].y

            if thresh_name_pp is None:
                thresh_name_pp = image.shape[0]/2

            # Extract ID
            # Get passport number
            if int(num_choice) == 3:
                if countNumbers(text.description) == 7 and text.description[0] in passport_letters:
                    text.description = text.description.capitalize()
                    card_id = text.description[-8:]
                    card_id = re.sub('[^0-9CBN]+', '', str(card_id))
            # Get ID Card / The can cuoc
            else:
                if countNumbers(text.description) >= 9:
                    if len(str(text.description)) == 9:
                        card_id = text.description[-9:]
                    else:
                        card_id = text.description[-12:]
                card_id = re.sub('[^0-9]+', '', str(card_id))

            # Extract name
            if countLowerCase(text.description) == 0 and countNumbers(text.description) == 0 and countUpperCase(text.description) <= 7\
                    and text.description.strip() not in remove_words:
                if re.compile('[@_!#$%^&*()<>?/\|}{~:-]').search(text.description) == None and len(text.description.strip()) > 0:
                    vertices = (['({},{})'.format(vertex.x, vertex.y)
                                 for vertex in text.bounding_poly.vertices])
                    if text.description in common_words:
                        upper_list[text.description] = vertices
                    else:
                        if text.description not in upper_list:
                            upper_list[text.description] = vertices

            # Extract DOB
            if int(num_choice) != 3:
                num_list = getDOBDirect(text, num_list)
            else:
                dob_list = getDOBSeparate(text, dob_list)

            if len(num_list) == 0:
                dob_list = getDOBSeparate(text, dob_list)

            # print('\n"{}"'.format(text.description))
            # vertices = (['({},{})'.format(vertex.x, vertex.y)
            #             for vertex in text.bounding_poly.vertices])

            # print('bounds: {}'.format(','.join(vertices)))

        # Get the final name
        try:
            # Get the image having name only
            # img_crop_name = extract_img_name(
            #     image, upper_list, thresh_name_pp)

            # save_cropped_name(img_crop_name, input_data, num_choice)

            # # Use Google OCR again to get the name only
            # name = getName(img_crop_name)

            name = ' '.join(unidecode(element) for element in list(process_upper_words(
                    upper_list, thresh_name_pp).keys()))
            name = name.lstrip().rstrip()
            name = re.sub('[^A-Z]+', ' ', name)


            # if len(name.split(' ')) <= 1:
            #     name = None
        except:
            pass

        # Get the final card ID and DOB
        try:
            if len(num_list) > 0:
                dob = num_list[0]
            else:
                dob = ''.join(element for element in list(process_upper_words(
                    dob_list, thresh_dob_pp).keys())).replace('/', '')
                dob = dob.replace(' ', '')
                if len(dob) == 6:
                    dob = dob[0:2] + dob 
                dob = datetime.strptime(
                    dob.strip(), '%d%m%Y').strftime('%d/%m/%Y')
        except:
            pass

        # Print the user info
        print('\nThe Card ID is: "{}"'.format(card_id))
        print('\nThe Name is: "{}"'.format(name))
        print('\nThe DOB is: "{}"'.format(dob))
        print(thresh_name_pp)

    return card_id, name, dob


# Main OCR application with arguments
def main_run(args):
    input_folder = os.getcwd() + "/" + args["input"]
    if (int(args["choice"]) == 1 or int(args["choice"]) == 3) and not args["output"]:
        if args["input"].endswith('.jpg') == True:
            card_id, name, dob = detect_text(args["choice"], args["input"])
            print('The OCR process is completed')
        else:
            print('Wrong input data')

    elif int(args["choice"]) == 2 or int(args["choice"]) == 3:
        if not args["output"]:
            print('Missing the output text filename (-o)')
        else:
            f = open(args["output"], "w")
            for filename in glob.glob(os.path.join(input_folder, '*.jpg')):
                card_id, name, dob = detect_text(args["choice"], filename)
                filename = filename.replace(input_folder + "/", '')
                output = filename + ',' + \
                    str(card_id) + ',' + str(name) + ',' + str(dob) + '\n'
                f.write(output)
            f.close()
            print(
                "The OCR process using Google Vision OCR is completed. See the output file to view the result")

    else:
        print("Invalid option to process")


# if __name__ == '__main__':
#     main_run(args)
