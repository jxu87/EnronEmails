#!/usr/bin/python
import re
import sys
import boto
import zipfile
import os
import shutil
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from boto.utils import get_instance_metadata
from boto.sts import STSConnection


#read from stdin
#expects a line with exactly one filename
#reaches out to a specific S3 bucket and pulls that file
#unzips it
#And analyzes the text emails in it
#then deletes the unzipped files

def main(argv):
	
	s3conn = boto.s3.connect_to_region("us-east-1")
		
	dateRE = re.compile("^Date: .*")
	subjectRE = re.compile("^Subject: .*")
	fromRE = re.compile("^From: .*")
	toRE = re.compile("^To: .*")
	origMessageRE = re.compile("-----Original Message-----")
	emailAddressRE = re.compile("<([^@]+@[^@]+\.[^@]+)>") 
	
	while True:
		s = sys.stdin.readline()
		if not s:
			break

		s = s.strip()
		zipbucket = s3conn.get_bucket("chrisdailey1-enron")
		#print "Got bucket"
		
		k = Key(zipbucket)
		k.key = "/zips/" + s
		#print "Saving"
		k.get_contents_to_filename(s)
		
		#print "Saved"
		try:
			z = zipfile.ZipFile(s, 'r')
		except zipfile.BadZipfile as e:
			#print e
			continue
		
		
		for zipentry in z.namelist():
			##Check for that format I mentioned
			if (re.match("text_.*", zipentry)):
				emailText = z.open(zipentry, 'r')
				for line in emailText.readlines():
					if (fromRE.match(line)):
						if (emailAddressRE.search(line)):
							addy = emailAddressRE.search(line).group(1)
							if (len(addy) < 50):
								print "LongValueSum:" + addy.lower() + "\t" + "1"
				
		z.close()


if __name__ == "__main__": 
    main(sys.argv) 
