__author__ = 'rencui'
import numpy
import json
from textstat.textstat import textstat
import utilities
from sklearn.feature_extraction.text import *
from sklearn import svm
from tokenizer import simpleTokenize
import logging
from scipy.sparse import hstack, csr_matrix
from sklearn.externals import joblib
import pickle

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


# vectorMode 1: tfidf, 2: binaryCount
# featureMode 0: semantic only, 1: vector only, 2: both
def modelTrainer(groupSize, groupTitle, vectorMode, featureMode):
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')

    print groupTitle
    for group in range(groupSize):
        print 'group: ' + str(group)
        happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
        posFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.pos', 'r')
        negFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.neg', 'r')
        posParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.pos', 'r')
        negParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.neg', 'r')
        posHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.pos', 'r')
        negHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.neg', 'r')

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

        print 'loading...'

        for line in posFile:
            seg = line.strip().split(' :: ')
            text = seg[3]
            username = seg[7].split(';')
            time.append(hourMapper(seg[2]))
            day = seg[1]
            score = float(seg[0])
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
            usernames.append(username)
            days.append(dayMapper[day])
            contents.append(text)
            scores.append(score)
            labels.append(0)

        if vectorMode == 1:
            vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english', binary='True')
            vectorMatrix = vectorizer.fit_transform(contents)
            corpus = vectorizer.vocabulary_
            corpusFile = open('adData/analysis/groups/' + groupTitle + '/model/unigram_' + str(group) + '.corpus', 'wb')
            pickle.dump(corpus, corpusFile)
            corpusFile.close()

        for line in posParseLengthFile:
            parseLength.append(int(line.strip(' :: ')[0]))
        for line in negParseLengthFile:
            parseLength.append(int(line.strip(' :: ')[0]))
        for line in posHeadCountFile:
            headCount.append(int(line.strip(' :: ')[0]))
        for line in negHeadCountFile:
            headCount.append(int(line.strip(' :: ')[0]))
        posHeadCountFile.close()
        negHeadCountFile.close()
        posParseLengthFile.close()
        negParseLengthFile.close()
        posFile.close()
        negFile.close()


        for index, content in enumerate(contents):
            temp = []
            twLen = len(simpleTokenize(content))
            posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
            readScore = textstat.coleman_liau_index(content)

            temp.append(content.count('urrl'))
            temp.append(content.count('hhttg'))
            temp.append(content.count('ussernm'))
            temp.append(twLen)
            temp.append(posProb)
            temp.append(readScore)
            temp.append(parseLength[index])
            temp.append(headCount[index])
            temp.append(days[index])
            temp.append(time[index])

            mentionFlag = 0
            mentionFollowers = 0
            for user in usernames[index]:
                if user in mentionMapper:
                    if mentionMapper[user][0] == 1:
                        mentionFlag = 1
                    mentionFollowers += mentionMapper[user][1]
            temp.append(mentionFlag)
            temp.append(mentionFollowers)

            semanticFeatures.append(numpy.array(temp))
            classes.append(labels[index])

        if featureMode == 0:
            features = csr_matrix(numpy.array(semanticFeatures))
        elif featureMode == 1:
            features = vectorMatrix
        else:
            features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeatures))), format='csr')

        model = svm.SVC(probability=True)
        model.fit(features, classes)

        joblib.dump(model, 'adData/analysis/groups/' + groupTitle + '/model/svm' + str(group) + '_'+str(vectorMode)+'_'+str(featureMode)+'.pkl')

def infer(modelTitle, modelGroup, vectorMode, featureMode, inferData, inferParseLength, inferHeadCount):
    print 'loading...'
    # load model files
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    model = joblib.load('adData/analysis/groups/' + modelTitle + '/model/svm' + str(modelGroup) + '_'+str(vectorMode)+'_'+str(featureMode)+'.pkl')
    corpusFile = open('adData/analysis/groups/' + modelTitle + '/model/unigram_' + str(modelGroup) + '.corpus', 'rb')
    corpus = pickle.load(corpusFile)
    corpusFile.close()
    happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')

    # load inference data
    posFile = open(inferData + '.pos', 'r')
    negFile = open(inferData + '.neg', 'r')
    posParseLengthFile = open(inferParseLength + '.pos', 'r')
    negParseLengthFile = open(inferParseLength + '.neg', 'r')
    posHeadCountFile = open(inferHeadCount + '.pos', 'r')
    negHeadCountFile = open(inferHeadCount + '.neg', 'r')

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

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        time.append(hourMapper(seg[2]))
        day = seg[1]
        score = float(seg[0])
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
        usernames.append(username)
        days.append(dayMapper[day])
        contents.append(text)
        scores.append(score)
        labels.append(0)

    if vectorMode == 1:
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english', binary='True', vocabulary=corpus)
        vectorMatrix = vectorizer.fit_transform(contents)

    for line in posParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in negParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in posHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    for line in negHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    posHeadCountFile.close()
    negHeadCountFile.close()
    posParseLengthFile.close()
    negParseLengthFile.close()
    posFile.close()
    negFile.close()

    for index, content in enumerate(contents):
        temp = []
        twLen = len(simpleTokenize(content))
        posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
        readScore = textstat.coleman_liau_index(content)

        temp.append(content.count('urrl'))
        temp.append(content.count('hhttg'))
        temp.append(content.count('ussernm'))
        temp.append(twLen)
        temp.append(posProb)
        temp.append(readScore)
        temp.append(parseLength[index])
        temp.append(headCount[index])
        temp.append(days[index])
        temp.append(time[index])

        mentionFlag = 0
        mentionFollowers = 0
        for user in usernames[index]:
            if user in mentionMapper:
                if mentionMapper[user][0] == 1:
                    mentionFlag = 1
                mentionFollowers += mentionMapper[user][1]
        temp.append(mentionFlag)
        temp.append(mentionFollowers)

        semanticFeatures.append(numpy.array(temp))
        classes.append(labels[index])

    if featureMode == 0:
        features = csr_matrix(numpy.array(semanticFeatures))
    elif featureMode == 1:
        features = vectorMatrix
    else:
        features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeatures))), format='csr')

    # infer
    print 'inference...'
    predictions = model.predict(features)

    correctCount = 0.0
    totalCount = 0.0
    if len(predictions) != len(classes):
        print 'inference error!'

    for index, label in enumerate(predictions):
        if label == 1:
            if classes[index] == 1:
                correctCount += 1
            totalCount += 1
    if totalCount == 0:
        precision = 0
    else:
        precision = correctCount / totalCount
    recall = correctCount / classes.count(1)
    f1Score = 2 * recall * precision / (recall + precision)

    return predictions, precision, recall, f1Score

def infer2(modelTitle, modelGroup, vectorMode, featureMode, inferData):
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    model = joblib.load('adData/analysis/groups/' + modelTitle + '/model/svm' + str(modelGroup) + '_'+str(vectorMode)+'_'+str(featureMode)+'.pkl')
    corpusFile = open('adData/analysis/groups/' + modelTitle + '/model/unigram_' + str(modelGroup) + '.corpus', 'rb')
    corpus = pickle.load(corpusFile)
    corpusFile.close()
    happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')

    # load inference data
    content = inferData['content']
    score = inferData['score']
    day = inferData['day']
    time = inferData['time']
    label = inferData['label']
    parseLength = inferData['parseLength']
    headCount = inferData['headCount']
    username = inferData['usernames']
    semanticFeature = []

    if vectorMode == 1:
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english', binary='True', vocabulary=corpus)
        vectorMatrix = vectorizer.fit_transform([content])

    temp = []
    twLen = len(simpleTokenize(content))
    posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
    readScore = textstat.coleman_liau_index(content)

    temp.append(content.count('urrl'))
    temp.append(content.count('hhttg'))
    temp.append(content.count('ussernm'))
    temp.append(twLen)
    temp.append(posProb)
    temp.append(readScore)
    temp.append(parseLength)
    temp.append(headCount)
    temp.append(day)
    temp.append(time)

    mentionFlag = 0
    mentionFollowers = 0
    for user in username:
        if user in mentionMapper:
            if mentionMapper[user][0] == 1:
                mentionFlag = 1
            mentionFollowers += mentionMapper[user][1]
    temp.append(mentionFlag)
    temp.append(mentionFollowers)

    semanticFeature.append(numpy.array(temp))

    if featureMode == 0:
        features = csr_matrix(numpy.array(semanticFeature))
    elif featureMode == 1:
        features = vectorMatrix
    else:
        features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeature))), format='csr')

    # infer
    prediction = model.predict(features)
    score = model.decision_function(features)

    return prediction[0], str(score)[1:-1]

def infer3(modelTitle, modelGroup, vectorMode, featureMode, inferData):
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    model = joblib.load('adData/analysis/groups/' + modelTitle + '/model/svm' + str(modelGroup) + '_'+str(vectorMode)+'_'+str(featureMode)+'.pkl')
    corpusFile = open('adData/analysis/groups/' + modelTitle + '/model/unigram_' + str(modelGroup) + '.corpus', 'rb')
    corpus = pickle.load(corpusFile)
    corpusFile.close()
    happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')

    # load inference data
    content = inferData['content']
    day = inferData['day']
    time = inferData['time']
    parseLength = inferData['parseLength']
    headCount = inferData['headCount']
    username = inferData['usernames']
    semanticFeature = []

    if vectorMode == 1:
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english', binary='True', vocabulary=corpus)
        vectorMatrix = vectorizer.fit_transform([content])

    temp = []
    twLen = len(simpleTokenize(content))
    posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
    readScore = textstat.coleman_liau_index(content)

    temp.append(content.count('urrl'))
    temp.append(content.count('hhttg'))
    temp.append(content.count('ussernm'))
    temp.append(twLen)
    temp.append(posProb)
    temp.append(readScore)
    temp.append(parseLength)
    temp.append(headCount)
    temp.append(day)
    temp.append(time)

    mentionFlag = 0
    mentionFollowers = 0
    for user in username:
        if user in mentionMapper:
            if mentionMapper[user][0] == 1:
                mentionFlag = 1
            mentionFollowers += mentionMapper[user][1]
    temp.append(mentionFlag)
    temp.append(mentionFollowers)

    semanticFeature.append(numpy.array(temp))

    if featureMode == 0:
        features = csr_matrix(numpy.array(semanticFeature))
    elif featureMode == 1:
        features = vectorMatrix
    else:
        features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeature))), format='csr')

    # infer
    prediction = model.predict(features)
    score = model.decision_function(features)
    #print model.classes_
    return prediction[0], score

def evaluator(modelTitle, modelGroup, testTitle, testGroup, vectorMode, featureMode):
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    print 'group: ' + str(testGroup)
    model = joblib.load('adData/analysis/groups/' + modelTitle + '/model/svm' + str(modelGroup) + '_'+str(vectorMode)+'_'+str(featureMode)+'.pkl')
    corpusFile = open('adData/analysis/groups/' + modelTitle + '/model/unigram_' + str(modelGroup) + '.corpus', 'rb')
    corpus = pickle.load(corpusFile)
    corpusFile.close()

    happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
    posFile = open('adData/analysis/groups/' + testTitle + '/group' + str(testGroup) + '.pos', 'r')
    negFile = open('adData/analysis/groups/' + testTitle + '/group' + str(testGroup) + '.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/' + testTitle + '/parserLength' + str(testGroup) + '.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/' + testTitle + '/parserLength' + str(testGroup) + '.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/' + testTitle + '/parserHeadCount' + str(testGroup) + '.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/' + testTitle + '/parserHeadCount' + str(testGroup) + '.neg', 'r')

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

    print 'loading...'

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        time.append(hourMapper(seg[2]))
        day = seg[1]
        score = float(seg[0])
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
        usernames.append(username)
        days.append(dayMapper[day])
        contents.append(text)
        scores.append(score)
        labels.append(0)

    if vectorMode == 1:
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english', binary='True', vocabulary=corpus)
        vectorMatrix = vectorizer.fit_transform(contents)

    for line in posParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in negParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in posHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    for line in negHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    posHeadCountFile.close()
    negHeadCountFile.close()
    posParseLengthFile.close()
    negParseLengthFile.close()
    posFile.close()
    negFile.close()


    for index, content in enumerate(contents):
        temp = []
        twLen = len(simpleTokenize(content))
        posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
        readScore = textstat.coleman_liau_index(content)

        temp.append(content.count('urrl'))
        temp.append(content.count('hhttg'))
        temp.append(content.count('ussernm'))
        temp.append(twLen)
        temp.append(posProb)
        temp.append(readScore)
        temp.append(parseLength[index])
        temp.append(headCount[index])
        temp.append(days[index])
        temp.append(time[index])

        mentionFlag = 0
        mentionFollowers = 0
        for user in usernames[index]:
            if user in mentionMapper:
                if mentionMapper[user][0] == 1:
                    mentionFlag = 1
                mentionFollowers += mentionMapper[user][1]
        temp.append(mentionFlag)
        temp.append(mentionFollowers)

        semanticFeatures.append(numpy.array(temp))
        classes.append(labels[index])

    if featureMode == 0:
        features = csr_matrix(numpy.array(semanticFeatures))
    elif featureMode == 1:
        features = vectorMatrix
    else:
        features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeatures))), format='csr')

    predictions = model.predict(features)

    correctCount = 0.0
    totalCount = 0.0
    if len(predictions) != len(classes):
        print 'inference error!'

    for index, label in enumerate(predictions):
        if label == 1:
            if classes[index] == 1:
                correctCount += 1
            totalCount += 1
    if totalCount == 0:
        precision = 0
    else:
        precision = correctCount / totalCount
    recall = correctCount / classes.count(1)

    print precision
    print recall
    print 2 * recall * precision / (recall + precision)



# vectorMode 1: binaryCount, 0: none
# featureMode 0: semantic only, 1: vector only, 2: both
'''
modelTrainer(3, 'brandGroup', 0, 0)
modelTrainer(3, 'subBrandGroup', 0, 0)
modelTrainer(5, 'topicGroup', 0, 0)
modelTrainer(5, 'simGroup', 0, 0)
modelTrainer(1, 'totalGroup', 0, 0)

modelTrainer(3, 'brandGroup', 1, 2)
modelTrainer(3, 'subBrandGroup', 1, 2)
modelTrainer(5, 'topicGroup', 1, 2)
modelTrainer(5, 'simGroup', 1, 2)
modelTrainer(1, 'totalGroup', 1, 2)
'''

#modelTitle, modelGroup, testTitle, testGroup, vectorMode, featureMode
#evaluator('simGroup', 0, 'simGroup', 4, 1, 2)
#evaluator('simGroup', 1, 'simGroup', 4, 1, 2)
#evaluator('simGroup', 2, 'simGroup', 4, 1, 2)
#evaluator('simGroup', 3, 'simGroup', 4, 1, 2)
#evaluator('simGroup', 4, 'simGroup', 4, 1, 2)