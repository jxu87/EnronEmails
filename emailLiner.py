import os
import re
import sys

def main(argv):
	filenameRE = re.compile(".*-.*.txt")
	attachmentRE = re.compile("^Attachment: .*")
	dateRE = re.compile("^Date: .*")

	if not os.path.exists(argv[1] + "processedEmails"):
				os.makedirs(argv[1] + "processedEmails")

	for filename in os.listdir(argv[1]):
		if filenameRE.match(filename):
			processedFile = open(argv[1] + "processedEmails/p_" + filename, 'w')
			textFile = open(argv[1] + filename, 'r')
			for line in textFile:
				if attachmentRE.match(line):
					continue
				if dateRE.match(line):
					processedFile.write("\n"+re.sub("\r\n|\n", " ", line))
				else:
					processedFile.write(re.sub("\r\n|\n", " ", line))
			textFile.close()
			processedFile.close()


   
if __name__ == "__main__":
	main(sys.argv)
