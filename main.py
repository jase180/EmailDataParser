#  This script loops through a directory named 'ABC' inside script directory.
#  'ABC' directory includes only .txt files that are emails including a request and info generated from mainframe
#  Specific information is to be parsed from each .txt file, stored in a list of lists, and written to a csv as out

import csv
import re
import os

#  This function takes in .txt date that looks something like "FEB 2/2023" to excel readable date
def convertDate(date_string):

    date_parts = date_string.split()
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    month = months.index(date_parts[0]) + 1 # + 1 to adjust back to correct month since index starts at 0
    
    day, year = date_parts[1].split('/')
    
    return f"{month}/{day}/{year}"

# function that uses regex to look for line written by human, therefore regex case insensitive in case of error
# Line always starts with same phrase.
# Puts all matched lines into a list, and returns first match only since it would be latest of email correspondence
def findroute(txt):
    matched_lines = []
    linenum = -1
    pattern = "(?i)Route|routing|route"
    for line in txt:
        linenum += 1
        if re.search(pattern, line) is not None:  # If pattern search finds a match,
            matched_lines.append((linenum, line.rstrip('\n')))

    match = matched_lines[0][1].split()  # [0] to only take first match in entire txt
    route = ' '.join(match[2:])
    return route

# function that uses regex to look for lines starting with 'GREATEST ..." within mainframe generated text
# Line always starts with same phrase.
# Puts all matched lines into a list, returns maximum of floats found
def findmaxrtg(txt):
    matched_lines = []  # for debugging if req'd
    ratings = []  # ls of all found max ratings
    linenum = -1
    pattern = 'GREATEST RATING IS'
    for line in txt:
        linenum += 1  # count lines
        if re.search(pattern, line) is not None:  # If pattern found in line, strip line and append lists
            matched_lines.append(linenum)
            linels = line.split()
            number = linels[3]
            ratings.append(number)

    # Find and return greatest rating in rating ls
    greatest = 0
    for n in ratings:
        if float(n) > greatest:
            greatest = float(n)

    return greatest

# function that uses regex to look for lines containing keyword within mainframe generated text
# multiple information to be parsed is around search line.  only first match is required since it would be latest
# Puts all required information into a list and returns list

def findAxles(txt):
    matched_lines = []
    linenum = -1
    pattern = re.compile('AXLES')
    for line in txt:
        linenum += 1
        if pattern.search(line) is not None:  # If pattern search finds a match,
            for nextLine in txt[linenum+1:linenum+11]:
                if '286,000' in nextLine:
                    matched_lines.append(linenum)
    matchLine = matched_lines[0] # isolate the newest one
    axles = txt[matchLine].split()[3]
    return axles

def findWeight(txt):
    matched_lines = []
    linenum = -1
    pattern = re.compile('GROSS WEIGHT')
    for line in txt:
        linenum += 1
        if pattern.search(line) is not None:  # If pattern search finds a match,
            for nextLine in txt[linenum+1:linenum+11]:
                if '286,000' in nextLine:
                    matched_lines.append(linenum)
    matchLine = matched_lines[0] # isolate the newest one
    weight = txt[matchLine].split()[4]
    return weight 

def findDate(txt):
    matched_lines = []
    linenum = -1
    pattern = re.compile('CLASSIFICATION')
    for line in txt:
        linenum += 1
        if pattern.search(line) is not None:  # If pattern search finds a match,
            matched_lines.append(linenum)        
    matchLine = matched_lines[0] # isolate the newest one
    
    date_out = ' '.join(txt[matchLine].split()[4:6])
    
    date_out = convertDate(date_out)
    

    return date_out

def findRequestCarLine(txt):
    matched_lines = []
    linenum = -1
    pattern = re.compile('CLASSIFICATION')
    for line in txt:
        linenum += 1
        if pattern.search(line) is not None:  # If pattern search finds a match,
            matched_lines.append(linenum)        
    matchLine = matched_lines[0] # isolate the newest one
    RequestCarLine = matchLine + 2
    return RequestCarLine

def findCar(txt):
    RequestCarLine = findRequestCarLine(txt)
    car_out = ' '.join(txt[RequestCarLine].split()[0:2])
    return car_out

def findRequest(txt):

    pattern = r"[LP]\d{5}"

    RequestCarLine = findRequestCarLine(txt)
    matchList = re.findall(pattern,txt[RequestCarLine])
    request_out = matchList[0]
    return request_out

def matchSentDate(request,dic):
    date_sent = ''
    if request in dic.keys():
        date_sent = dic[request]
        return date_sent
    return date_sent

def makeSentDict():  
    dic = {}
    pattern = r'([PL].{5})'

    with open('DateSent.csv', 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            match = re.search(pattern, row[0])
            if match:
                dic[match.group(1)] = row[1]
    return dic
            


# MAIN DRIVER
out_list = []  # generate output list to write to csv file

dictSents = makeSentDict()

# loop through directory containing required txts.  Each loop generates a list called ls and adds all find functions
# into list.  
for file in os.listdir('HAL'):
    with open(os.path.join('HAL', file), 'r') as f:
        print("starting " + file)
        txt = []  # read text into a list
        for line in f:
            txt.append(line)

        ls = []
        ls.append(findDate(txt))
        ls.append('') # empty column tos plit
        ls.append(findroute(txt))
        ls.append(findCar(txt))       
        ls.append(findAxles(txt))     
        ls.append(findWeight(txt))  
        ls.append(findmaxrtg(txt))     
        ls.append('')
        ls.append(findRequest(txt))             

        ls.append(matchSentDate(ls[-1],dictSents)) 

        out_list.append(ls)

        print(file + " completed")

# write to csv file
with open('output.csv', 'w', newline='', encoding='UTF8') as f:
    writer = csv.writer(f)
    for ls in out_list:
        writer.writerow(ls)

print("Parse completed")