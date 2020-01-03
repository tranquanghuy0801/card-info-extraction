import os 
import glob 
import pandas as pd
import logging 
import argparse
import re
from difflib import SequenceMatcher

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--test", required=True,
                help="the file containing the test result")
ap.add_argument("-r", "--reference", required=True,
                help="the reference file containing the true result")
ap.add_argument("-l","--logs",required=True,
                help="The name of logs file containing the log result")
ap.add_argument("-c","--csv",required=True,
                help="The name of csv file containing the comparison result")   
args = vars(ap.parse_args())

main_dir = os.getcwd()

# create logger with 'spam_application'
logger = logging.getLogger('scan_card')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(args['logs'])
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Function to calculate the similarity score of two strings
def similarity_score(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Get file number from the input string 
def getFileNum(text):
    text = text.split(',')[0]
    text = text.split('.')[0]
    text = re.sub('[^0-9]+','', text)
    return int(text)

lines = [] # Save the lines from the test file 

list_id_acc = []
list_name_acc = [] 
list_dob_acc = [] 

# Similarity scores 
id_acc = 0 
name_acc = 0
dob_acc = 0 

# Count correct extractions 
id_correct = 0
name_correct = 0
dob_correct = 0 

# count number of images
num_img = 0 

# Put all lines in test file into a list "lines"
with open(main_dir + "/" + args["test"], "r") as file:
    l = file.read().splitlines()
    l.sort(key=getFileNum, reverse = False)
    lines = l 

# Main run 
with open(main_dir + "/" + args["reference"],"r") as file:
    for reference_file in file:

        num_img += 1 
        file_num = getFileNum(reference_file)
        reference_file = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in reference_file.split(',')]
        process_file = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in lines[file_num-1].split(',')]
        logger.debug('\nProcessing ' + process_file[0])
        print('\t', "|-------------------------------|")
        print('\t','Processing image ' + process_file[0])

        # ID Processing 
        logger.debug("\nPredicted ID: " + str(process_file[1]) + "\tTrue ID: " + str(reference_file[1]))        
        id_sim_score = similarity_score(str(process_file[1]),str(reference_file[1]))
        id_acc += id_sim_score
        if(str(process_file[1]) == str(reference_file[1])):
            id_correct += 1 
            list_id_acc.append(1)
            print("Correct ID")
            logger.debug("Similarity: " + str(id_sim_score) + "  -  Correct ID")
        else:
            list_id_acc.append(0)
            logger.debug("Similarity: " + str(id_sim_score) + "  -  Wrong ID")
        print('\t The ID score: "{}"'.format(round(id_sim_score,4)))

        # Name Processing 
        logger.debug("Predicted Name: " + str(process_file[2]) + "\tTrue Name: " + str(reference_file[2]))   
        name_sim_score = similarity_score(str(process_file[2]),str(reference_file[2]))
        name_acc += name_sim_score
        print('\t The Name score: "{}"'.format(round(name_sim_score,4)))
        if(str(process_file[2]) == str(reference_file[2])):
            name_correct += 1 
            list_name_acc.append(1)
            print("Correct Name")
            logger.debug("Similarity: " + str(name_sim_score) + "  -  Correct Name")
        else:
            list_name_acc.append(0)
            logger.debug("Similarity: " + str(name_sim_score) + "  -  Wrong Name")

        # DOB processing
        logger.debug("Predicted DOB: " + str(process_file[3]) + "\tTrue DOB: " + str(reference_file[3]))  
        process_file[3] = process_file[3].replace('\n','')
        reference_file[3] = reference_file[3].replace('\n','')
        dob_sim_score = similarity_score(str(process_file[3]),str(reference_file[3]))
        dob_acc += dob_sim_score           
        if(str(process_file[3]) == str(reference_file[3])):
            dob_correct += 1 
            list_dob_acc.append(1)
            print("Correct DOB")
            logger.debug("Similarity: " + str(dob_sim_score) + "  -  Correct DOB")
        else:
            list_dob_acc.append(0)
            logger.debug("Similarity: " + str(dob_sim_score) + "  -  Wrong DOB")
        print('\t The DOB score: "{}"'.format(round(dob_sim_score,4)))


print('\n\t\n','The statistics displays below:')
print('\n\t','The ID accuracy: ' + str(round(id_acc/num_img * 100,3)) + ' %')
print('\t', "|-------------------------------|")
print('\t','The Name accuracy: ' + str(round(name_acc/num_img * 100,3)) + ' %')
print('\t', "|-------------------------------|")
print('\t','The DOB accuracy: ' + str(round(dob_acc/num_img * 100,3)) + ' %')
print('\t', "|-------------------------------|")
print('\t','The ID correct: ' + str(id_correct) + '/' + str(num_img))
print('\t', "|-------------------------------|")       
print('\t','The Name correct: ' + str(name_correct) + '/' + str(num_img))
print('\t', "|-------------------------------|") 
print('\t','The DOB correct: ' + str(dob_correct) + '/' + str(num_img))
print('\t', "|-------------------------------|") 

logger.debug("\nThe statistics displays below:")
logger.debug('\nThe ID accuracy: ' + str(round(id_acc/num_img * 100,3)) + ' %')
logger.debug('\nThe Name accuracy: ' + str(round(name_acc/num_img * 100,3)) + ' %')
logger.debug('\nThe DOB accuracy: ' + str(round(dob_acc/num_img * 100,3)) + ' %')
logger.debug('\nThe ID correct: ' + str(id_correct) + '/' + str(num_img))
logger.debug('\nThe Name correct: ' + str(name_correct) + '/' + str(num_img))
logger.debug('\nThe DOB correct: ' + str(dob_correct) + '/' + str(num_img))

# Create DataFrame to save file as CSV 
df = pd.DataFrame({'Image': list(range(1,num_img+1)),'Name': list_name_acc,'ID': list_id_acc,'DOB': list_dob_acc})
df.to_csv(args['csv'],index=False)
    
