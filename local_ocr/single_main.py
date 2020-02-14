## Author: Tran Quang Huy
## single_main.py: Process single image
## multiple_main.py: Process a folder of images 


# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json

################################################################################################################
############################# Section 1: Initiate the command line interface ###################################
################################################################################################################

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
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

##############################################################################################################
###################### Section 2: Load the image -- Preprocess it -- Write it to disk ########################
##############################################################################################################

# load the example image and convert it to grayscale
orig_image = cv2.imread(args["image"])
orig_image = cv2.resize(orig_image,(1000,652))
imgY,imgX = orig_image.shape[:2]
print(orig_image.shape[:2])
id_image =  orig_image[int(round(imgY * 0.15)):int(round(imgY * 0.40)),:,:]
print(id_image.shape)
image = orig_image[int(round(imgY * 0.38)):imgY,int(round(imgX * 0.44)):imgX,:]
print(image.shape)
id_image_gray = cv2.cvtColor(id_image,cv2.COLOR_BGR2GRAY)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    id_image_gray = cv2.threshold(id_image_gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocess"] == "adaptive":
    gray = cv2.adaptiveThreshold(id_image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
'''
What we would like to do is to add some additional preprocessing steps as in most cases, you may need to scale your 
image to a larger size to recognize small characters. 
In this case, INTER_CUBIC generally performs better than other alternatives, though it’s also slower than others.

If you’d like to trade off some of your image quality for faster performance, 
you may want to try INTER_LINEAR for enlarging images.
'''
if args["preprocess"] == "linear":
    gray = cv2.resize(id_image_gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    id_image_gray = cv2.resize(id_image_gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

elif args["preprocess"] == "cubic":
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

if args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)
    id_image_gray = cv2.medianBlur(id_image_gray, 3)

elif args["preprocess"] == "bilateral":
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    id_image_gray = cv2.bilateralFilter(id_image_gray, 9, 75, 75)

elif args["preprocess"] == "gauss":
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    id_image_gray = cv2.GaussianBlur(id_image_gray, (5,5), 0)

# write the grayscale image to disk as a temporary file so we can
# apply OCR to it
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)
file_id_image = "output.png"
cv2.imwrite(file_id_image,id_image_gray)

'''
A blurring method may be applied. We apply a median blur when the --preprocess flag is set to blur. 
Applying a median blur can help reduce salt and pepper noise, again making it easier for Tesseract 
to correctly OCR the image.

After pre-processing the image, we use  os.getpid to derive a temporary image filename based on the process ID 
of our Python script.

The final step before using pytesseract for OCR is to write the pre-processed image, gray, 
to disk saving it with the filename  from above
'''

##############################################################################################################
######################################## Section 3: Running PyTesseract ######################################
##############################################################################################################


# load the image as a PIL/Pillow image, apply OCR, and then delete
# the temporary file
name_dob_text = pytesseract.image_to_string(gray)
os.remove(filename)
id_text = pytesseract.image_to_string(id_image_gray)
os.remove(file_id_image)

# show the output images
cv2.imshow("Image", image)
cv2.imshow("Part 1 Output", id_image_gray)
cv2.imshow("Part 2 Output",gray)
cv2.waitKey(0)

# # writing extracted data into a text file
# text_output = open('outputbase.txt', 'w', encoding='utf-8')
# text_output.write(text)
# text_output.close()

# file = open('outputbase.txt', 'r', encoding='utf-8')
# text = file.read()
# print(text)

############################################################################################################
###################################### Section 4: Extract relevant information #############################
############################################################################################################

# Initializing data variable
name = None
dob = None
card_id = None 
text0 = []

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


id_regex = re.compile(r'[A-Za-z0-9]+')
text0 = list(filter(id_regex.search,process_text(id_text)))
print(text0)
text0 = list(filter(lambda x: countNumbers(x) >= 10, text0))
text1 = list(filter(id_regex.search, process_text(name_dob_text)))
print(text1)
text1 = list(filter(lambda x: countUpperCase(x) >= 5 or countNumbers(x) >= 6, text1))
if len(text1) >= 1:
    if countLowerCase(text1[0]) >= 1 or countNumbers(text1[0]) >= 1:
        text1.pop(0)
 
print(text0)  # Contains all the relevant extracted text in form of a list 
print(text1)


## Process the id text 
try:
    # Extract the card id
    if len(text0) >= 1: 
        card_id = text0[0]
        if card_id.find(':') == -1 and card_id.find('.') == -1:
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

print(card_id)
# Making tuples of data
data = {}
data['Card ID'] = card_id
data['Name'] = name
data['Date of Birth'] = dob
print(data)

###############################################################################################################
######################################### Section 6: Write Data to JSONs ######################################
###############################################################################################################

# # Writing data into JSON
# try:
#     to_unicode = unicode
# except NameError:
#     to_unicode = str

# # Write JSON file
# with io.open('data.json', 'w', encoding='utf-8') as outfile:
#     str_ = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
#     outfile.write(to_unicode(str_))

# # Read JSON file
# with open('data.json', encoding = 'utf-8') as data_file:
#     data_loaded = json.load(data_file)

# # print(data == data_loaded)

# # Reading data back JSON(give correct path where JSON is stored)
# with open('data.json', 'r', encoding= 'utf-8') as f:
#     ndata = json.load(f)

print(data)

print('\t', "|+++++++++++++++++++++++++++++++|")
print('\t', '|', '\t', data['Name'])
print('\t', "|-------------------------------|")
print('\t', '|', '\t', data['Date of Birth'])
print('\t', "|-------------------------------|")
print('\t', '|', '\t', data['Card ID'])
print('\t', "|+++++++++++++++++++++++++++++++|")