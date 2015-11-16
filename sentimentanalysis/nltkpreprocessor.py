#!/usr/bin/python

import string
import re
import sys

def printUsage():
    print "nltkpreprocessor.py <inputEmailFile> <processedEmailFile>"

def processEmail(email):
    #Convert [InternetShortcut] URL=www.* or http://* to PERSONALURL
    email = re.sub('((URL=www\.[^\s]+)|(URL=http://[^\s]+))','PERSONALURL',email)
    #Convert [InternetShortcut] URL=mailto to BUSINESSURL
    email = re.sub('URL=mailto:[^\s]+','BUSINESSURL',email)
    #Remove email addresses
    email = re.sub('[^\s]+@[^\s]+','',email)
    #Remove strings that start with </
    email = re.sub('</[^\s]+','',email)
    #Remove numbers
    email = re.sub('\S*\d\S*','', email)
    #Remove additional white spaces
    email = re.sub('[\s]+', ' ', email)
    #Replace #word with word
    email = re.sub(r'#([^\s]+)', r'\1', email)
    #Convert to lower case
    email = email.lower()
    #trim
    email = email.strip('\'"')

    return email

def main(argv):
    inputFile = argv[1]
    outputFile = argv[2]

    fr = open(inputFile, 'rU')
    fw = open(outputFile, 'w')

    # read the emails and process one by one
    line = fr.readline()
    while line:
        processedEmail = processEmail(line)
        fw.write(processedEmail + '\r\n')
        line = fr.readline()

    # close the file handles
    fr.close()
    fw.close()

if __name__ == "__main__":
    if (len(sys.argv) != 3):
        printUsage()
    else:
        main(sys.argv)
