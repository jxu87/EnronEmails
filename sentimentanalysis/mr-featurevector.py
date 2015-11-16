import nltk
import re
from mrjob.job import MRJob

class MRFeatureVector(MRJob):

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

        def getFeatureVector(email):
            # initialize stopWords
            stopWords = nltk.corpus.stopwords.words('english')

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

        # process input to get feature vector
        processedEmail = processEmail(line)
        featureVector = getFeatureVector(processedEmail)

        # return the feature vector
        for feature in featureVector:
            yield (feature.lower(), 1)

    def reducer(self, key, values):
        yield key, sum(values)

if __name__ == '__main__':
    MRFeatureVector.run()
