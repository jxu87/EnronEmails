#!/usr/bin/python

import nltk
import nltkpreprocessor
import pickle
import re
import sys

# initialize featureList and stopWords
featureList = []
stopWords = []

def printUsage():
    print "featurevector.py <rawEmailFile> <featureVectorOutputFile>"
    print "featurevector.py <labeledEmailFile>"

def updateStopWordList():
    global stopWords
    stopWords = nltk.corpus.stopwords.words('english')
    # append any other stop words
    # stopWords.append('word')

def getFeatureVector(email):
    global stopWords
    excludeTags = ['NNP', 'NNPS', 'PRP', 'PRP$']
    featureVector = []

    # split email into words
    words = email.split()
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
    wordTags = nltk.pos_tag(featureVector)
    featureVector = [word[0] for word in wordTags if word[1] not in excludeTags]

    return featureVector

def getFeatures(email):
    global featureList
    features = {}

    emailWords = set(email)
    for word in featureList:
        features['contains(%s)' % word] = (word in emailWords)

    return features

def processRawEmails(inputFile, outputFile):
    fr = open(inputFile, 'rU')
    fw = open(outputFile, 'w')

    featureList = []

    # read the emails and process one by one
    line = fr.readline()
    while line:
        processedEmail = nltkpreprocessor.processEmail(line)
        featureVector = getFeatureVector(processedEmail)
        featureList.extend(featureVector)
        line = fr.readline()

    # write feature list to output file
    featureList = list(set(featureList))
    for feature in featureList:
        fw.write("{}\n".format(feature))

    # close file handles
    fr.close()
    fw.close()

def processLabeledEmails(inputFile):
    global featureList
    emailSentiments = []

    fr = open(inputFile, 'rU')
    line = fr.readline()
    while line:
        emailItems = line.split('\t')
        emailLine = emailItems[0]
        sentiment = emailItems[1].rstrip()

        processedEmail = nltkpreprocessor.processEmail(emailLine)
        featureVector = getFeatureVector(processedEmail)
        emailSentiments.append((featureVector, sentiment))
        featureList.extend(featureVector)

        line = fr.readline()

    # close file handle
    fr.close()

    # remove dupes from featureList
    featureList = list(set(featureList))

    # generate training set
    emailTrainingSet = nltk.classify.util.apply_features(getFeatures, emailSentiments)

    # train the classifier
    classifier = nltk.NaiveBayesClassifier.train(emailTrainingSet)

    # save the classifier
    classifierPickle = open('email_classifier.pickle', 'wb')
    pickle.dump(classifier, classifierPickle)
    classifierPickle.close()

    return classifier

def testClassifier(classifier):
    testEmails = ['last questions',
                  'contact tyrion lannister in corporate for bankruptcy questions',
                  'family - they hope for some money from you',
                  'URL=mailto:ceo@enron.com as the last contact',
                  'winterfell is in westeros or essos?']

    for testEmail in testEmails:
        processedEmail = nltkpreprocessor.processEmail(testEmail)
        featureVector = getFeatureVector(processedEmail)
        features = getFeatures(featureVector)
        emailSentiment = classifier.classify(features)

        trueFeatures = []
        for key, value in features.iteritems():
            if value is True:
                trueFeatures.append(key)

        print "     testEmail: {}".format(testEmail)
        print "processedEmail: {}".format(processedEmail)
        print " featureVector: {}".format(featureVector)
        print "  trueFeatures: {}".format(trueFeatures)
        print "emailSentiment: {}".format(emailSentiment)
        print "\n"

    classifier.show_most_informative_features(10)

def main(argv):
    inputFile = argv[1]

    # update the global stopWords list
    updateStopWordList()

    if (len(sys.argv) == 2):
        # running with labeled emails
        classifier = processLabeledEmails(inputFile)

        # test classifier
        testClassifier(classifier)
    else:
        # running with raw emails
        outputFile = argv[2]
        processRawEmails(inputFile, outputFile)

if __name__ == "__main__":
    if (len(sys.argv) != 2 and len(sys.argv) != 3):
        printUsage()
    else:
        main(sys.argv)
