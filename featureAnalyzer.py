__author__ = 'rencui'
from afinn import Afinn
import numpy
import json
from textstat.textstat import textstat
from nltk.stem.porter import *
from tokenizer import simpleTokenize
import logging
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt
import matplotlib as mat
from sklearn.ensemble import ExtraTreesClassifier

stemmer = PorterStemmer()
logging.basicConfig()
dayMapper = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}


def hourMapper(hour):
    input = int(hour)
    if 0 <= input < 6:
        output = 0
    elif 6 <= input < 12:
        output = 1
    elif 12 <= input < 18:
        output = 2
    else:
        output = 3
    return output


def mapMention(inputFile):
    mentionFile = open(inputFile, 'r')
    outputMapper = {}
    for line in mentionFile:
        mention = json.loads(line.strip())
        if mention['verified'] == 'true':
            verify = 1
        else:
            verify = 0
        outputMapper[mention['screen_name']] = (verify, mention['followers_count'])
    mentionFile.close()
    return outputMapper


def stemContent(input):
    words = simpleTokenize(input)
    out = ''
    for word in words:
        temp = stemmer.stem(word)
    out += temp + ' '
    return out.strip()


def POSRatio(inputList):
    out = []
    temp = []
    for item in inputList:
        temp.append(float(item))
    if sum(temp) == 0:
        out = [0.0, 0.0, 0.0]
    else:
        for item in temp:
            out.append(item / sum(temp))
    return out


mentionMapper = mapMention('adData/analysis/ranked/mention.json')
featureList = ['Length', 'URL', 'Hashtag', 'Username', 'Sentiment', 'Readability',
               'ParseDepth', 'HeadCount', 'POS_N', 'POS_V', 'POS_A', '!', '?',
               'Verified', 'FollowerCount']

# happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
afinn = Afinn()
posFile = open('adData/analysis/groups/totalGroup/group0.pos', 'r')
negFile = open('adData/analysis/groups/totalGroup/group0.neg', 'r')
posParseLengthFile = open('adData/analysis/groups/totalGroup/parserLength0.pos', 'r')
negParseLengthFile = open('adData/analysis/groups/totalGroup/parserLength0.neg', 'r')
posHeadCountFile = open('adData/analysis/groups/totalGroup/parserHeadCount0.pos', 'r')
negHeadCountFile = open('adData/analysis/groups/totalGroup/parserHeadCount0.neg', 'r')
posPOSCountFile = open('adData/analysis/groups/totalGroup/parserPOSCount0.pos', 'r')
negPOSCountFile = open('adData/analysis/groups/totalGroup/parserPOSCount0.neg', 'r')

ids = []
contents = []
scores = []
days = []
time = []
labels = []
parseLength = []
headCount = []
usernames = []
semanticFeatures = []
classes = []
POScounts = []

print 'loading...'

for line in posFile:
    seg = line.strip().split(' :: ')
    text = seg[3]
    username = seg[7].split(';')
    time.append(hourMapper(seg[2]))
    day = seg[1]
    score = float(seg[0])
    ids.append(seg[5])
    usernames.append(username)
    days.append(dayMapper[day])
    contents.append(text)
    scores.append(score)
    labels.append(1)

for line in negFile:
    seg = line.strip().split(' :: ')
    text = seg[3]
    username = seg[7].split(';')
    time.append(hourMapper(seg[2]))
    day = seg[1]
    score = float(seg[0])
    ids.append(seg[5])
    usernames.append(username)
    days.append(dayMapper[day])
    contents.append(text)
    scores.append(score)
    labels.append(0)

    for line in posParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in negParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in posHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    for line in negHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    for line in posPOSCountFile:
        POScounts.append(POSRatio(line.strip().split(' :: ')[0].split(' ')))
    for line in negPOSCountFile:
        POScounts.append(POSRatio(line.strip().split(' :: ')[0].split(' ')))


posHeadCountFile.close()
negHeadCountFile.close()
posParseLengthFile.close()
negParseLengthFile.close()
posPOSCountFile.close()
negPOSCountFile.close()
posFile.close()
negFile.close()
print len(contents)

for index, content in enumerate(contents):
    temp = []
    words = simpleTokenize(content)
    twLen = float(len(words))
    sentiScore = afinn.score(stemContent(content))
    # posProb, negProb = utilities.classifySentiment(words, happy_log_probs, sad_log_probs)
    readScore = textstat.coleman_liau_index(content)

    temp.append(twLen)

    # temp.append(content.count('URRL'))
    if content.count('URRL') > 0:
        temp.append(1)
    else:
        temp.append(0)
    # temp.append(content.count('HHTTG'))
    if content.count('HHTTG') > 0:
        temp.append(1)
    else:
        temp.append(0)
    # temp.append(content.count('USSERNM'))
    if content.count('USSERNM') > 0:
        temp.append(1)
    else:
        temp.append(0)

    temp.append(sentiScore / twLen)
    temp.append(readScore)
    temp.append(parseLength[index] / twLen)
    temp.append(headCount[index] / twLen)
    # temp.append(days[index])
    # temp.append(time[index])
    temp += POScounts[index]
    # temp.append(content.count('!'))
    if content.count('!') > 0:
        temp.append(1)
    else:
        temp.append(0)
    # temp.append(content.count('?'))
    if content.count('?') > 0:
        temp.append(1)
    else:
        temp.append(0)

    mentionFlag = 0
    mentionFollowers = 0
    userCount = 0.0
    for user in usernames[index]:
        if user in mentionMapper:
            userCount += 1
            if mentionMapper[user][0] == 1:
                mentionFlag = 1
            mentionFollowers += mentionMapper[user][1]
    temp.append(mentionFlag)

    if userCount == 0:
        temp.append(0.0)
    else:
        temp.append(mentionFollowers / userCount)

    semanticFeatures.append(numpy.array(temp))
    classes.append(labels[index])

features = csr_matrix(numpy.array(semanticFeatures))

# Build a forest and compute the feature importances
forest = ExtraTreesClassifier(n_estimators=50,
                              random_state=0)

forest.fit(features, classes)
importances = forest.feature_importances_
std = numpy.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
indices = numpy.argsort(importances)[::-1]

labelList = []
for index in indices:
    labelList.append(featureList[index])

# Print the feature ranking
print("Feature ranking:")
for f in range(features.shape[1]):
    print(labelList[f] + '\t' + str(importances[indices[f]]))


# Plot the feature importances of the forest
font = {'family': 'normal', 'size': 12}

mat.rc('font', **font)

plt.figure()
plt.title("Feature Importances")
plt.bar(range(features.shape[1]), importances[indices],
        color="r", yerr=std[indices], align="center")
plt.xticks(range(features.shape[1]), labelList)
plt.xlim([-1, features.shape[1]])
plt.show()


print 'Feature List: 1. Length; 2.URL; 3.Hashtag; 4.Username; 5.Sentiment; 6.Readability; 7.ParseDepth; 8.HeadCount; 9.POS_N; 10.POS_V; 11.POS_A; 12.!; 13.?; 14.Verified; 15.FollowerCount'

