import os 
import glob 
import argparse
import re
from difflib import SequenceMatcher

# Function to calculate the similarity score of two strings
def similarity_score(a, b):
    return SequenceMatcher(None, a, b).ratio()

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--test", required=True,
                help="the file containing the test result")
ap.add_argument("-r", "--reference", required=True,
                help="the reference file containing the true result")
args = vars(ap.parse_args())

main_dir = os.getcwd()

# Get file number from the input string 
def getFileNum(text):
    text = text.split(',')[0]
    text = text.split('.')[0]
    text = re.sub('[^0-9]+','', text)
    return int(text)

lines = [] 
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
    for process_file in file:
        num_img += 1 
        file_num = getFileNum(process_file)
        process_file = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in process_file.split(',')]
        reference_file = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in lines[file_num-1].split(',')]
        print('\t', "|-------------------------------|")
        print('\t','Processing image ' + process_file[0])
        # ID Processing 
        id_acc += similarity_score(str(process_file[1]),str(reference_file[1]))
        if(str(process_file[1]) == str(reference_file[1])):
            id_correct += 1 
            print("Correct ID")
        print('\t The ID score: "{}"'.format(round(similarity_score(str(process_file[1]),str(reference_file[1])),4)))
        # Name Processing 
        name_acc += similarity_score(str(process_file[2]),str(reference_file[2]))
        print('\t The Name score: "{}"'.format(round(similarity_score(str(process_file[2]),str(reference_file[2])),4)))
        if(str(process_file[2]) == str(reference_file[2])):
            name_correct += 1 
            print("Correct Name")
        # DOB processing
        process_file[3] = process_file[3].replace('\n','')
        reference_file[3] = reference_file[3].replace('\n','')
        dob_acc += similarity_score(str(process_file[3]),str(reference_file[3]))                
        if(str(process_file[3]) == str(reference_file[3])):
            dob_correct += 1 
            print("Correct DOB")
        print('\t The DOB score: "{}"'.format(round(similarity_score(str(process_file[3]),str(reference_file[3])),4)))

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
    
