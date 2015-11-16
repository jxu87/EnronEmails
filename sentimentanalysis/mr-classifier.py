import nltk
import pickle
import re
import os.path
from mrjob.job import MRJob
from mrjob.step import MRStep
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto

class MREmailClassifier(MRJob):

    #def get_helper_files(self):

        #if not os.path.isfile("processed_mr_featurevector.txt"):
            #s3conn = boto.s3.connect_to_region("us-east-1")
            #bucket = s3conn.get_bucket("chrisdailey1-enron")
            #k = Key(bucket)
            #k.key = "/helperfiles/processed_mr_featurevector.txt"
            #k.get_contents_to_filename("processed_mr_featurevector.txt")
        #if not os.path.isfile("email_classifier.pickle"):
            #s3conn = boto.s3.connect_to_region("us-east-1")
            #bucket = s3conn.get_bucket("chrisdailey1-enron")
            #k = Key(bucket)
            #k.key = "/helperfiles/email_classifier.pickle"
            #k.get_contents_to_filename("email_classifier.pickle")

    def mapper(self, _, line):
        def processEmail(email):
            # convert [InternetShortcut] URL=www.* or http://* to PERSONALURL
            email = re.sub('((URL=www\.[^\s]+)|(URL=http://[^\s]+))','PERSONALURL',email)
            # convert [InternetShortcut] URL=mailto to BUSINESSURL
            email = re.sub('URL=mailto:[^\s]+','BUSINESSURL',email)
            # remove email addresses
            email = re.sub('[^\s]+@[^\s]+','',email)
            # remove strings that start with </
            email = re.sub('</[^\s]+','',email)
            # remove numbers
            email = re.sub('\S*\d\S*','', email)
            # remove additional white spaces
            email = re.sub('[\s]+', ' ', email)
            # replace #word with word
            email = re.sub(r'#([^\s]+)', r'\1', email)
            # convert to lower case
            email = email.lower()
            # trim
            email = email.strip('\'"')

            return email

        def getFeatureList():
            # initialize feature list
            featureList = []

            # get features from the feature list file
            featureFile = open('processed_mr_featurevector.txt', 'r')
            feature = featureFile.readline()
            while feature:
                featureList.append(feature.split('\t')[0])
                feature = featureFile.readline()

            # close the feature list file
            featureFile.close()

            return featureList

        def getFeatureVector(email):
            # initialize stopWords
            stopWords = nltk.corpus.stopwords.words('english')

            # list of nltk english stopwords
            # (uncomment to use this instead of above)
            #stopWords = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']

            # split email into words
            words = email.split()

            # initialize feature vector list
            featureVector = []

            for w in words:
                # strip punctuation
                w = w.strip('\'"?,.')

                # check if the word stats with an alphabet
                val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)

                # ignore if it is a stop word or does not start with an alphabet
                if (val is None or w in stopWords):
                    continue
                else:
                    featureVector.append(w.lower())

            # remove proper nouns (NNP, NNPS), personal pronouns (PRP), possessive pronouns (PRP$)
            excludeTags = ['NNP', 'NNPS', 'PRP', 'PRP$']
            wordTags = nltk.pos_tag(featureVector)
            featureVector = [word[0] for word in wordTags if word[1] not in excludeTags]

            return featureVector

        def getFeatures(email):
            # initialize email features
            features = {}

            # initialize unique email elements
            email = set(email)

            # extract features
            for word in getFeatureList():
                features['contains(%s)' % word] = (word in email)

            return features

        # load the classifier
        classifierPickle = open('email_classifier.pickle')
        classifier = pickle.load(classifierPickle)

        # process input to get features
        processedEmail = processEmail(line)
        featureVector = getFeatureVector(processedEmail)
        features = getFeatures(featureVector)

        # classify the input
        sentiment = classifier.classify(features)

        # format the output
        #output = line + "\t" + sentiment
        #output = "{}\t{}".format(line, sentiment)
        yield (sentiment, 1)

    def reducer(self, key, values):
        yield key, sum(values)


    #def steps(self):
        #return [MRStep(mapper_init=self.get_helper_files,
                #mapper=self.mapper,
                #reducer=self.reducer)]



if __name__ == '__main__':
    MREmailClassifier.run()
