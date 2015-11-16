import os
import re
import sys
import zipfile
import shutil
import random


def main(argv):
	

	emails = []
	
	
	#The format for the xml, text-only emails
	keptRE = re.compile("edrm-enron-v2_.*-.*_xml\.zip")
	
	fieldRE = re.compile("^.+: ")
	endRE = re.compile("\*\*\*\*\*\*\*\*\*\*\*")
	originalRE = re.compile("-----Original Message-----")
	forwardedRE = re.compile("---------------------- Forwarded by")
	
	#the base directory given at the cli
	baseDir = argv[1]
	#the place to put the csv
	destinationDir = argv[2]
	
	#find the zip files that match the format
	startingFiles = os.listdir(baseDir)
	random.shuffle(startingFiles)
	#for i in range(0,100):
	for filename in startingFiles:
		#filename = startingFiles[i]
		if (keptRE.match(filename)):

			print "Matched " + filename
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
			print "Unzipping"
			z.extractall(baseDir + "/" + shortname)
				
			#the email unzips into a couple of different folders, one of which stores
			#only the text of the email.  I think I've seen folders with more than one text
			#folder, so go through them one by one and if they match the name format
			#of the text-only folders, use that folder
			nextFiles = os.listdir(baseDir + "/" + shortname)
			random.shuffle(nextFiles)
			for lineEntry in nextFiles:
				#Check for that format I mentioned
				if (re.match("text_.*", lineEntry)):
					#store the directory to make more readable code
					textDirectory = baseDir + "/" + shortname + "/" + lineEntry
					#go through each text file
					textFiles = os.listdir(textDirectory)
					random.shuffle(textFiles)
					for i in range(0,500):
						if len(textFiles) < i :
							break
						emailBody = ""
						textFile = open(textDirectory + "/" + textFiles[i], 'r')
						print "Chose " + textFiles[i]
						pastFields = False
						for line in textFile:
							if fieldRE.match(line) and not pastFields:
								print "Skipping field: " + line
								continue
							if endRE.match(line) or originalRE.search(line) or forwardedRE.search(line):
								print "Breaking: " + line
								break
							emailBody = emailBody + re.sub("\"", '', line.strip()) + " "
							pastFields = True
						if len(emailBody) > 10000:
							print "Email too long."
							break
						if len(emailBody.strip()) < 10:
							print "Email too short."
							break
						textFile.close()
						print "Writing:\n====\n" + emailBody + "\n====\n"
						resultsFile = open(argv[2]+"/results.csv",'a')
						resultsFile.write("\"" + emailBody + "\"\n")
						resultsFile.close()
						print "Written."
			
			#delete their special folder since it's not needed anymore
			#if we leave it we'll take up a ton of space (presumably)
			#with everyone's unzipped emails
			shutil.rmtree(baseDir + "/" + shortname)
		
		
		
	
if __name__ == "__main__": 
    main(sys.argv) 

