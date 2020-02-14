# Author: Tran Quang Huy
# single_main.py: Process single image
# multiple_main.py: Process a folder of images

# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import glob
import io
import json

################################################################################################################
############################# Section 1: Initiate the command line interface ###################################
################################################################################################################

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
                help="the input folder containing images for OCR")
ap.add_argument("-t", "--text", required=True,
                help="the text file to save the result")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing to be done, choose from blur, linear, cubic or bilateral")
args = vars(ap.parse_args())

'''
Our command line arguments are parsed. We have two command line arguments:

--image : The path to the image we’re sending through the OCR system.
--preprocess : The preprocessing method. This switch is optional and for this tutorial and can accept the following
                parameters to be passed (refer sections to know more:
                - blur
                - adaptive
                - linear
                - cubic
                - gauss
                - bilateral
                - thresh (meadian threshold - default)

---------------------------  Use Blur when the image has noise/grain/incident light etc. --------------------------
'''


def preprocess_img(method, image_path):
    # load the example image and convert it to grayscale
    orig_image = cv2.imread(image_path)
    orig_image = cv2.resize(orig_image,(1000,652))
    imgY,imgX = orig_image.shape[:2]
    id_image =  orig_image[int(round(imgY * 0.15)):int(round(imgY * 0.40)),:,:]
    image = orig_image[int(round(imgY * 0.38)):imgY,int(round(imgX * 0.44)):imgX,:]
    id_image_gray = cv2.cvtColor(id_image,cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if method == "thresh":
        gray = cv2.threshold(gray, 0, 255,
                            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        id_image_gray = cv2.threshold(id_image_gray, 0, 255,
                            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    elif method == "adaptive":
        gray = cv2.adaptiveThreshold(id_image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    '''
    What we would like to do is to add some additional preprocessing steps as in most cases, you may need to scale your 
    image to a larger size to recognize small characters. 
    In this case, INTER_CUBIC generally performs better than other alternatives, though it’s also slower than others.

    If you’d like to trade off some of your image quality for faster performance, 
    you may want to try INTER_LINEAR for enlarging images.
    '''
    
    if method == "linear":
        gray = cv2.resize(id_image_gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        id_image_gray = cv2.resize(id_image_gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    elif method == "cubic":
        gray = cv2.resize(id_image_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        id_image_gray = cv2.resize(id_image_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # make a check to see if blurring should be done to remove noise, first is default median blurring

    '''
    1. Gaussian Blurring works in a similar fashion to Averaging, but it uses Gaussian kernel, 
    instead of a normalized box filter, for convolution. Here, the dimensions of the kernel and standard deviations 
    in both directions can be determined independently. 
    Gaussian blurring is very useful for removing — guess what? — 
    gaussian noise from the image. On the contrary, gaussian blurring does not preserve the edges in the input.

    2. In Median Blurring the central element in the kernel area is replaced with the median of all the pixels under the 
    kernel. Particularly, this outperforms other blurring methods in removing salt-and-pepper noise in the images.

    Median blurring is a non-linear filter. Unlike linear filters, median blurring replaces the pixel values 
    with the median value available in the neighborhood values. So, median blurring preserves edges 
    as the median value must be the value of one of neighboring pixels

    3. Speaking of keeping edges sharp, bilateral filtering is quite useful for removing the noise without 
    smoothing the edges. Similar to gaussian blurring, bilateral filtering also uses a gaussian filter 
    to find the gaussian weighted average in the neighborhood. However, it also takes pixel difference into 
    account while blurring the nearby pixels.

    Thus, it ensures only those pixels with similar intensity to the central pixel are blurred, 
    whereas the pixels with distinct pixel values are not blurred. In doing so, the edges that have larger 
    intensity variation, so-called edges, are preserved.
    '''

    if method == "blur":
        gray = cv2.medianBlur(gray, 3)
        id_image_gray = cv2.medianBlur(id_image_gray, 3)

    elif method == "bilateral":
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        id_image_gray = cv2.bilateralFilter(id_image_gray, 9, 75, 75)

    elif method == "gauss":
        gray = cv2.GaussianBlur(gray, (5,5), 0)
        id_image_gray = cv2.GaussianBlur(id_image_gray, (5,5), 0)

    return id_image_gray, gray 

##############################################################################################################
###################### Section 2: Load the image -- Preprocess it -- Write it to disk ########################
##############################################################################################################

input_folder = os.getcwd() + "/" + args["input"]
input_txt = args["text"]

def process_text(text):
    list_text = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        list_text.append(s)
    return list_text 

def countNumbers(inputString):
    return sum(c.isdigit() for c in inputString)

def countUpperCase(inputString):
    return sum(1 for c in inputString if c.isupper())

def countLowerCase(inputString):
    return sum(1 for c in inputString if c.islower())

def get_info(id_image_gray,gray):
    # Initializing data variable
    name = None
    dob = None
    card_id = None 
    text0 = []
    text1= []

    name_dob_text = pytesseract.image_to_string(gray)
    id_text = pytesseract.image_to_string(id_image_gray)

    ## Filter the text 
    id_regex = re.compile(r'[A-Za-z0-9]+')
    text0 = list(filter(id_regex.search,process_text(id_text)))
    text0 = list(filter(lambda x: countNumbers(x) >= 10, text0))
    text1 = list(filter(id_regex.search, process_text(name_dob_text)))
    text1 = list(filter(lambda x: countUpperCase(x) >= 5 or countNumbers(x) >= 6, text1))
    # if len(text1) >= 1:
    #     if countLowerCase(text1[0]) >= 1 or countNumbers(text1[0]) >= 1:
    #         text1.pop(0)

    ## Process the id text 
    try:
       # Extract the card id
        if len(text0) >= 1: 
            card_id = text0[0]
            if card_id.find(':') == -1 and card_id.find('.') == -1:
                card_id = card_id.split(' ')[1]
                card_id = re.sub('[^0-9]+','', card_id)
            elif card_id.find(':') != -1:
                card_id = card_id.split(':')[1]
                card_id = re.sub('[^0-9]+','', card_id)
            elif card_id.find('.') != -1:
                card_id = card_id.split('.')[1]
                card_id = re.sub('[^0-9]+','', card_id)

        # Extract the card name 
        if len(text1) >= 2:
            name = text1[0]
            name = re.sub('[^A-Za-z]',' ',name)
            name = name.rstrip()
            name = name.lstrip()

        # Extract the DOB
        if len(text1) >= 2:
            dob = text1[1]
            if dob.find(':') == -1 and dob.find('.') == -1:
                dob = re.sub('[^0-9/]+','', dob)
            elif dob.find(':') != -1:
                dob = dob.split(':')[1]
                dob = re.sub('[^0-9/]+','', dob)
            elif dob.find('.') != -1:
                dob = dob.split('.')[1]
                dob = re.sub('[^0-9/]+','', dob)

    except:
        pass
    return card_id,name,dob

f = open(args["text"],"w")
for filename in glob.glob(os.path.join(input_folder,'*.jpg')):
    id_image_gray, gray = preprocess_img(args["preprocess"],filename)
    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    card_id,name,dob = get_info(id_image_gray,gray)
    filename = filename.replace(input_folder + "/",'')
    output = filename + ',' + str(card_id) + ',' + str(name) + ',' + str(dob) + '\n' 
    f.write(output)

f.close()
print("The OCR process completed. See the output file to view the result")




