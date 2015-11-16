import os
import re
import sys
import zipfile
import shutil

#this script accepts an argument consisting of a directory.
#It finds all the files in that directory that match the
#Enron filename format and extracts them to folders that
#match the name of the person who wrote the emails.

def main(argv):
	keptFiles = []
	#The format for the xml, text-only emails
	keptRE = re.compile("edrm-enron-v2_.*-.*_xml\.zip")
	
	#the base directory given at the cli
	baseDir = argv[1]
	#the place to put the totals
	destinationDir = argv[2]
	
	#make a directory to store the catted emails
	if not os.path.exists(destinationDir + "totals"):
			os.makedirs(destinationDir + "totals")
	
	#find the zip files that match the format
	for filename in os.listdir(baseDir):
		if (keptRE.match(filename)):
			keptFiles.append(filename)
			print filename
			
	for filename in keptFiles:
		#for error checking, print the filename
		print filename
		#define it as a zip file
		try:
			z = zipfile.ZipFile(baseDir + filename, 'r')
		except zipfile.BadZipfile as e:
			print e
			continue
		#pull out the abbreviated name of the emailer
		shortname = re.match("edrm-enron-v2_(.*-.*)_xml\.zip", filename).group(1)
		#make a folder just for them
		if not os.path.exists(baseDir + "/" + shortname):
			os.makedirs(baseDir + "/" + shortname)
		#unzip the file contents to their individual folder
		z.extractall(baseDir + "/" + shortname)
		#stage some memory for holding the catted emails
		totalText = ""
		#the email unzip into a couple of different folder, one of which stores
		#only the text of the email.  I think I've seen folders with more than one text
		#folder, so go through them one by one and if they match the name format
		#of the text-only folders, use that folder
		for lineEntry in os.listdir(baseDir + "/" + shortname):
			#Check for that format I mentioned
			if (re.match("text_.*", lineEntry)):
				#store the directory to make more readable code
				textDirectory = baseDir + "/" + shortname + "/" + lineEntry
				#go through each text file
				for textFile in os.listdir(textDirectory):
					#read it
					emailText = open(textDirectory + "/" + textFile, 'r')
					#cat it with the total
					totalText = totalText + emailText.read()
					#close it
					emailText.close()
		#make a file for the catted emails
		individualTotal = open(destinationDir + "totals/" + shortname + ".txt", 'w')
		#save the catted total there
		individualTotal.write(totalText)
		#and close it
		individualTotal.close() 
		
		#delete their special folder since it's not needed anymore
		#if we leave it we'll take up a ton of space (presumably)
		#with everyone's unzipped emails
		shutil.rmtree(baseDir + "/" + shortname)
		
		
		
	
if __name__ == "__main__": 
    main(sys.argv) 
