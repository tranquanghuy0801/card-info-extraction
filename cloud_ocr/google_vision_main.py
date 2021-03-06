from unidecode import unidecode
from cloud_ocr.helper import *
import io
from urllib.request import urlopen
from datetime import datetime
import numpy as np
import argparse
import os
import cv2
import re
import glob

passport_letters = ["C","B","N","c","n","b"]

# get name from image having name only
def getName(image):
    if image is not None:
        text = getTextGoogleOCR(image, "vi")[0].description.split('/n')[0]
        name = unidecode(text.replace("HỌ","").replace("Họ",""))
        name = re.sub('[^A-Za-z0-9]+', ' ', name)
        name = name.rstrip().lstrip()
        name = ' '.join(word for word in name.split(
            ' ') if countUpperCase(word) == len(word))
        return name
    else:
        return None

# return DOB list with strings having length 7 or 8: -> [11-11-2012]
def getDOBDirect(text, dob_direct):
    if (countNumbers(text.description) == 8 or countNumbers(text.description) == 7) and (text.description.find('/') != -1 or text.description.find('-') != -1):
        if text.description.find('/') != -1:
            dob_direct.append(re.sub('[^0-9/]+', '', text.description))
        elif text.description.find('-') != -1:
            text.description = text.description.replace('-', '/')
            dob_direct.append(re.sub('[^0-9/]+', '', text.description))
    return dob_direct

# return DOB list having number only for extra processing steps: -> [11-,11-,2012]
def getDOBSeparate(text, dob_separate):
    if countNumbers(text.description) <= 8 and countNumbers(text.description) > 1 and countLowerCase(text.description) == 0 and countUpperCase(text.description) == 0:
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                     for vertex in text.bounding_poly.vertices])
        dob_separate[text.description] = vertices
    return dob_separate


# Extract name, card ID and DOB from each image
def detect_text(num_choice, input_data, save_path=save_folder):
    """Detects text in the file."""

    # Initialize variables
    card_id = None
    name = None
    dob = None
    thresh_dob_pp = None  # Threshold of dob location to extract appropriate words
    thresh_name_pp = None # Threshold of name location to extract appropriate names
    dob_direct = [] # return of function getDOBDirect()
    dob_separate = {} # return of function getDOBSeparate()
    upper_words = {} # save uppercase words with coordinates into upper_words dict

    # Use local image
    if input_data.find('/home') == -1:
        # Use url to read image
        image  = url_to_image(input_data) 
    else:
        # Use local image
        image = read_local_image(input_data)

    # Get all text read by Google OCR
    texts = getTextGoogleOCR(image, "vi")

    print(texts)

    if len(texts) > 0:
        print('Texts:')
        for text in texts:
            # Remove special symbols
            text.description = re.sub(
                '[@_!#$%^&*()<>?\|}{~:.]', ' ', text.description)
            print(text.description)

            if text.description.find("Full") != -1 and num_choice == 3:
                thresh_name_pp = text.bounding_poly.vertices[0].y
            elif text.description in name_lines and (num_choice == 1 or num_choice == 2):
                thresh_name_pp = text.bounding_poly.vertices[0].y

            if text.description.find("Sex") != -1:
                thresh_dob_pp = text.bounding_poly.vertices[0].y

            if thresh_name_pp is None:
                thresh_name_pp = image.shape[0]/2

            # Extract ID
            # Get passport number
            if num_choice == 3:
                if countNumbers(text.description) == 7 and text.description[0] in passport_letters:
                    text.description = text.description.capitalize()
                    card_id = text.description[-8:]
                    card_id = re.sub('[^0-9CBN]+', '', str(card_id))
            # Get ID Card 
            else:
                if countNumbers(text.description) >= 9:
                    if len(str(text.description)) == 9:
                        card_id = text.description[-9:]
                    else:
                        card_id = text.description[-12:]
                card_id = re.sub('[^0-9]+', '', str(card_id))

            # Extract uppercase words and saved in upper_words dict
            if countLowerCase(text.description) == 0 and countNumbers(text.description) == 0 and countUpperCase(text.description) <= 7\
                    and text.description.strip() not in remove_words:
                if re.compile('[@_!#$%^&*()<>?/\|}{~:-]').search(text.description) == None and len(text.description.strip()) > 0:
                    vertices = (['({},{})'.format(vertex.x, vertex.y)
                                 for vertex in text.bounding_poly.vertices])
                    if unidecode(text.description) in common_words:
                        upper_words[text.description] = vertices
                    else:
                        if text.description not in upper_words:
                            upper_words[text.description] = vertices

            # Extract DOB list 
            if num_choice != 3:
                dob_direct = getDOBDirect(text, dob_direct)
            else:
                dob_separate = getDOBSeparate(text, dob_separate)

            if len(dob_direct) == 0:
                dob_separate = getDOBSeparate(text, dob_separate)

            # Print for debugging
            # print('\n"{}"'.format(text.description))
            # vertices = (['({},{})'.format(vertex.x, vertex.y)
            #             for vertex in text.bounding_poly.vertices])

            # print('bounds: {}'.format(','.join(vertices)))

        # Get the final name
        try:
            """
            Extract name using Google OCR for image having name only

            # Get the image having name only
            # img_crop_name = extract_img_name(image, upper_words, thresh_name_pp)

    
            # save_cropped_name(img_crop_name, input_data, num_choice)

            # name = getName(img_crop_name)
            """

            name = ' '.join(element for element in list(filter_dict(upper_words, thresh_name_pp).keys()))
            name = unidecode(name.lstrip().rstrip())
            name = re.sub('[^A-Z]+', ' ', name)

            # set name = None if the name has less than 2 words
            if len(name.split(' ')) <= 1:
                name = None

        except:
            pass

        # Get the final card ID and DOB
        try:
            if len(dob_direct) > 0:
                dob = dob_direct[0]
            else:
                dob = ''.join(element for element in list(filter_dict(dob_separate, thresh_dob_pp).keys()))
                dob = dob.replace('/', '').replace(' ', '')

                # Having similar month and date: (11/2012 -> 11/11/2012) 
                if len(dob) == 6:
                    dob = dob[0:2] + dob 

                # Convert to right format: D/M/Y
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
    num_choice = int(args["choice"])
    outfile = args["output"]

    # Process single ID or passport
    if (num_choice == 1 or num_choice == 2) and not outfile:
        if args["input"].endswith('.jpg') == True:
            card_id, name, dob = detect_text(num_choice, args["input"])
            print('The OCR process is completed')
        else:
            print('Wrong input data')

    # Process a folder of IDs or passports
    elif (num_choice == 1 or num_choice == 2):
        if not outfile:
            print('Missing the output text filename (-o)')
        else:
            f = open(outfile, "w")
            for filename in glob.glob(os.path.join(input_folder, '*.jpg')):
                card_id, name, dob = detect_text(num_choice, filename)
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
#     #construct the argument parse and parse the arguments
#     ap = argparse.ArgumentParser()
#     ap.add_argument("-i", "--input", required=True,
#                     help="the input folder containing images for OCR")
#     ap.add_argument("-o", "--output",
#                     help="the output folder containing json file")
#     ap.add_argument("-c", "--choice", required=True,
#                     help="1: process single ID image, 2: process a folder of ID images, 3: process passport image")
#     args = vars(ap.parse_args())
#     main_run(args)
