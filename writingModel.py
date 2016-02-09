import glob
import os
import shutil

__author__ = 'rencui'
import subprocess
from tokenizer import simpleTokenize
import utilities
from readcalc import readcalc
import json
import re

happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')


def shrinkPuncuation(input):
    input = re.sub('\.+', '.', input)
    input = re.sub(',+', ',', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('=+', '=', input)
    input = re.sub('-+', '-', input)
    input = re.sub('_+', '_', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('@+', '@', input)
    input = re.sub('&+', '&', input)
    input = re.sub('#+', '#', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('\*+', '*', input)
    return input


def removeUsername(input):
    users = re.findall(r'@(\w+)', input)
    if len(users) != 0:
        for user in users:
            input = input.replace(user, '<USERNAME>')
            input = input.replace('@: ', '')
    return input


def tokenizeLinks(input):
    urls = re.findall("(?P<url>https?://[^\s]+)", input)
    if len(urls) != 0:
        for url in urls:
            input = input.replace(url, ' <URL> ')
    return input


def normalizeText(input):
    input = input.replace('\r', '')
    input = input.replace('\n', '')
    input = tokenizeLinks(input)
    input = shrinkPuncuation(input)
    return input


def genTopicFeatures():
    outputFeatures = []
    print 'Running LDA modelling...'
    for cacheFile in glob.glob('data\\data.csv.term-counts.cache*'):
        os.remove(cacheFile)
    if os.path.exists('TMT Cache'):
        shutil.rmtree('TMT Cache')
    subprocess.check_output('java -jar data/tmt-0.4.0.jar data/script.scala', shell=True)
    distFile = open('TMT Cache\\document-topic-distributions.csv', 'r')
    topicIndex = []
    for line in distFile:
        item = line.strip().split(',')
        topicIndex.append(int(item[0]))
        outputFeatures.append(item[1:])
    distFile.close()
    return outputFeatures, topicIndex


def genPOSFeatures():
    print 'running Twitter POS tagger...'
    contentFile = open('data\\commercialData.content', 'r')
    POSinputFile = open('data\\POSinput', 'w')
    for line in contentFile:
        POSinputFile.write(normalizeText(line.strip()) + '\n')
    contentFile.close()
    POSinputFile.close()
    outputFeatures = []
    POStags = {'^': 0, 'G': 0, 'A': 0, 'N': 0, ',': 0, 'D': 0, 'P': 0, 'U': 0, 'O': 0, 'V': 0, 'L': 0, '!': 0, 'R': 0,
               '&': 0,
               'T': 0, '$': 0, 'Z': 0, '~': 0, 'X': 0, 'E': 0, 'S': 0, '#': 0, 'Y': 0, '@': 0}
    subprocess.check_output(
        'java -XX:ParallelGCThreads=5 -Xmx950m -jar posTagger/ark-tweet-nlp-0.3.2.jar --input-format text --output-format conll data/POSinput > data/POSoutput',
        shell=True)
    posFile = open('data\\POSoutput', 'r')
    for line in posFile:
        item = line.strip()
        if len(item) > 0:
            seg = item.split('\t')
            POStags[seg[1]] += 1
        else:
            outputFeatures.append(POStags)
            POStags = {'^': 0, 'G': 0, 'A': 0, 'N': 0, ',': 0, 'D': 0, 'P': 0, 'U': 0, 'O': 0, 'V': 0, 'L': 0, '!': 0,
                       'R': 0, '&': 0,
                       'T': 0, '$': 0, 'Z': 0, '~': 0, 'X': 0, 'E': 0, 'S': 0, '#': 0, 'Y': 0, '@': 0}
    posFile.close()
    return outputFeatures

# readin data
print 'reading in data...'
inputFile = open('data\\commercialPost.tweet', 'r')
tweetData = []
for line in inputFile:
    data = json.loads(line.strip())
    content = normalizeText(data['text']).replace('\u2026', '')
    temp = []
    for tag in data['entities']['hashtags']:
        temp.append(tag['text'])
    hashTags = temp
    retweetCount = data['retweet_count']
    favoriteCount = data['favorite_count']
    followerCount = data['user']['followers_count']
    postCount = data['user']['statuses_count']
    friendCount = data['user']['friends_count']
    favoriteTotalCount = data['user']['favourites_count']

    tempDict = {}
    tempDict['content'] = content
    tempDict['hashTags'] = hashTags
    tempDict['retweetCount'] = retweetCount
    tempDict['favoriteCount'] = favoriteCount
    tempDict['followerCount'] = followerCount
    tempDict['postCount'] = postCount
    tempDict['friendCount'] = friendCount
    tempDict['favoriteTotalCount'] = favoriteTotalCount

    tweetData.append(tempDict)
inputFile.close()

# generate features
print 'generating features...'
LDAfile = open('data\\data.csv', 'w')
sentiFeatures = []
readabilityFeatures = []
lengthFeatures = []
retweetLabels = []
favoriteLabels = []
reachLabels = []
for tweet in tweetData:
    content = tweet['content']
    words = simpleTokenize(content)
    if tweet['retweetCount'] < 1:
        retweetLabels.append(0)
    else:
        retweetLabels.append(1)
    if tweet['favoriteCount'] < 1:
        favoriteLabels.append(0)
    else:
        favoriteLabels.append(1)

    # sentiment feature
    tweet_happy_prob, tweet_sad_prob = utilities.classifySentiment(words, happy_log_probs, sad_log_probs)
    sentiFeatures.append(tweet_happy_prob)

    # readability feature
    readabilityFeatures.append(readcalc.ReadCalc(content).get_smog_index())

    # length feature
    lengthFeatures.append(len(words))

    # LDA input file
    LDAfile.write('"'+content.encode('utf-8').replace('"', "'")+'"'+'\n')

LDAfile.close()

# POS Features
posFeatures = genPOSFeatures()

# topic Features
(topicFeatures, topicIndex) = genTopicFeatures()

## generate weka file
outputFile = open('data\\output.arff', 'w')
outputFile.write('@RELATION rewteet\n\n')

for i in range(5):
    outputFile.write('@ATTRIBUTE topic'+str(i)+' numeric\n')
for i in range(24):
    outputFile.write('@ATTRIBUTE pos'+str(i)+' numeric\n')
outputFile.write('@ATTRIBUTE readability numeric\n')
outputFile.write('@ATTRIBUTE sentiment numeric\n')
outputFile.write('@ATTRIBUTE length numeric\n')
outputFile.write('@ATTRIBUTE class {0,1}\n\n')
outputFile.write('@DATA\n')

for i in range(len(retweetLabels)):
    if i in topicIndex:
        out = ''
        for feature in topicFeatures[i]:
            out += str(feature) + ','
        for feature in posFeatures[i].values():
            out += str(feature) + ','
        out += str(readabilityFeatures[i]) + ','
        out += str(sentiFeatures[i]) + ','
        out += str(lengthFeatures[i]) + ','
        out += str(favoriteLabels[i])
        outputFile.write(out+'\n')
outputFile.close()

print 'DONE'