__author__ = 'rencui'
from collections import OrderedDict
import math
from nltk.corpus import stopwords
stopwordList = stopwords.words('english')

posTweetFile = open('adData/analysis/ranked/NERoutput.pos', 'r')
negTweetFile = open('adData/analysis/ranked/NERoutput.neg', 'r')
posTokenFile = open('adData/analysis/ranked/tokenV.pos', 'w')
negTokenFile = open('adData/analysis/ranked/tokenV.neg', 'w')

posTweet = []
negTweet = []

for line in posTweetFile:
    posTweet.append(line.strip())
for line in negTweetFile:
    negTweet.append(line.strip())
posTweetFile.close()
negTweetFile.close()

posWordCorpus = {}
negWordCorpus = {}

for tweet in posTweet:
    words = tweet.split()
    for word in words:
        if word in posWordCorpus:
            posWordCorpus[word] += 1.0
        else:
            posWordCorpus[word] = 1.0

for tweet in negTweet:
    words = tweet.split()
    for word in words:
        if word in negWordCorpus:
            negWordCorpus[word] += 1.0
        else:
            negWordCorpus[word] = 1.0

posWords = OrderedDict(sorted(posWordCorpus.items(), key=lambda kv: kv[1], reverse=True))
negWords = OrderedDict(sorted(negWordCorpus.items(), key=lambda kv: kv[1], reverse=True))

for item in posWords:
    if item not in stopwordList:
        posTokenFile.write(item + ' : '+str(math.log(posWords[item]/len(posTweet)))+'\n')

for item in negWords:
    if item not in stopwordList:
        negTokenFile.write(item + ' : '+str(math.log(negWords[item]/len(negTweet)))+'\n')

posTokenFile.close()
negTokenFile.close()