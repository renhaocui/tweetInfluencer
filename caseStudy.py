__author__ = 'rencui'
from afinn import Afinn
from sklearn.externals import joblib
import numpy
import json
from textstat.textstat import textstat
from nltk.stem.porter import *
from tokenizer import simpleTokenize
import logging
from scipy.sparse import hstack, csr_matrix
from sklearn import svm

stemmer = PorterStemmer()
logging.basicConfig()


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


def longestLength(input):
    outputLength = 0
    for key, value in input.items():
        length = 0
        if value != '-1' and value != '_':
            length += 1
            if value == '0':
                if length > outputLength:
                    outputLength = length
                continue
            nextNode = value
            while nextNode != '-1' and nextNode != '_' and nextNode != '0':
                length += 1
                nextNode = input[nextNode]
        if length > outputLength:
            outputLength = length
    return outputLength


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


def outputHeads(input):
    output = ''
    for key, value in input.items():
        if value[1] == 0:
            output += value[0] + '/' + value[2] + ' '
    return output.strip()


def run(group, groupTitle, outputFile='result.output'):
    resultFile = open(outputFile, 'a')
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')

    print groupTitle
    resultFile.write(groupTitle + '\n')
    print 'group: ' + str(group)
    resultFile.write('group: ' + str(group) + '\n')
    afinn = Afinn()
    posFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.pos', 'r')
    negFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.neg', 'r')
    posPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.pos', 'r')
    negPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.neg', 'r')

    ids = []
    contents = []
    scores = []
    labels = []
    parseLength = []
    headCount = []
    usernames = []
    POScounts = []

    print 'loading...'

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
        contents.append(text)
        scores.append(score)
        labels.append(1)

    for line in negFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
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

    semanticFeatures_train = []
    semanticFeatures_test = []
    classes_train = []
    classes_test = []
    index_test = []
    for index, content in enumerate(contents):
        temp = []
        words = simpleTokenize(content)
        twLen = float(len(words))
        sentiScore = afinn.score(stemContent(content))
        readScore = textstat.coleman_liau_index(content)

        temp.append(twLen)

        if content.count('URRL') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('HHTTG') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('USSERNM') > 0:
            temp.append(1)
        else:
            temp.append(0)

        temp.append(sentiScore / twLen)
        temp.append(readScore)
        temp.append(parseLength[index] / twLen)
        temp.append(headCount[index] / twLen)
        temp += POScounts[index]
        if content.count('!') > 0:
            temp.append(1)
        else:
            temp.append(0)
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

        if index % 5 == 0:
            semanticFeatures_test.append(numpy.array(temp))
            classes_test.append(labels[index])
            index_test.append(index)
        else:
            semanticFeatures_train.append(numpy.array(temp))
            classes_train.append(labels[index])

    feature_train = csr_matrix(numpy.array(semanticFeatures_train))
    feature_test = csr_matrix(numpy.array(semanticFeatures_test))

    resultFile.flush()

    model = svm.SVC()
    model.fit(feature_train, classes_train)
    predictions = model.predict(feature_test)

    if len(predictions) != len(classes_test):
        print 'inference error!'

    for index, label in enumerate(predictions):
        if label == 0 and classes_test[index] == 1:
            print ids[index_test[index]]
            print contents[index_test[index]]
    resultFile.flush()

    resultFile.write('\n')
    resultFile.flush()

    resultFile.close()


def run2(group, groupTitle, outputFile='result.output'):
    resultFile = open(outputFile, 'a')
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    tempListFile = open('results/temp.list', 'r')
    excludeList = []
    for line in tempListFile:
        excludeList.append(line.strip())

    print groupTitle
    resultFile.write(groupTitle + '\n')
    print 'group: ' + str(group)
    resultFile.write('group: ' + str(group) + '\n')
    afinn = Afinn()
    posFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.pos', 'r')
    negFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.neg', 'r')
    posPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.pos', 'r')
    negPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.neg', 'r')

    ids = []
    contents = []
    scores = []
    labels = []
    parseLength = []
    headCount = []
    usernames = []
    POScounts = []

    print 'loading...'

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
        contents.append(text)
        scores.append(score)
        labels.append(1)

    for line in negFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
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

    semanticFeatures_train = []
    semanticFeatures_test = []
    classes_train = []
    classes_test = []
    index_test = []
    for index, content in enumerate(contents):
        temp = []
        words = simpleTokenize(content)
        twLen = float(len(words))
        sentiScore = afinn.score(stemContent(content))
        readScore = textstat.coleman_liau_index(content)

        temp.append(twLen)

        if content.count('URRL') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('HHTTG') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('USSERNM') > 0:
            temp.append(1)
        else:
            temp.append(0)

        temp.append(sentiScore / twLen)
        temp.append(readScore)
        temp.append(parseLength[index] / twLen)
        temp.append(headCount[index] / twLen)
        temp += POScounts[index]
        if content.count('!') > 0:
            temp.append(1)
        else:
            temp.append(0)
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

        if index % 5 == 0:
            semanticFeatures_test.append(numpy.array(temp))
            classes_test.append(labels[index])
            index_test.append(index)
        else:
            semanticFeatures_train.append(numpy.array(temp))
            classes_train.append(labels[index])

    feature_train = csr_matrix(numpy.array(semanticFeatures_train))
    feature_test = csr_matrix(numpy.array(semanticFeatures_test))

    resultFile.flush()

    model = svm.SVC()
    model.fit(feature_train, classes_train)
    # joblib.dump(model, 'results/full.pkl')
    # model = joblib.load('results/full.pkl')
    predictions = model.predict(feature_test)

    if len(predictions) != len(classes_test):
        print 'inference error!'

    for index, label in enumerate(predictions):
        # tempListFile.write(ids[index_test[index]]+'\n')
        if label == 1 and classes_test[index] == 1:
            print ids[index_test[index]]
            print contents[index_test[index]]
    resultFile.flush()

    resultFile.write('\n')
    resultFile.flush()
    tempListFile.close()

    resultFile.close()


def run3():
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    tempListFile = open('results/temp.list', 'r')
    excludeList = []
    for line in tempListFile:
        excludeList.append(line.strip())
    groupTitle = 'totalGroup'
    group = 0
    afinn = Afinn()
    posFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.pos', 'r')
    negFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.neg', 'r')
    posPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.pos', 'r')
    negPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.neg', 'r')

    ids = []
    contents = []
    scores = []
    labels = []
    parseLength = []
    headCount = []
    usernames = []
    POScounts = []

    print 'loading...'

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
        contents.append(text)
        scores.append(score)
        labels.append(1)

    for line in negFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
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

    semanticFeatures_train = []
    semanticFeatures_test = []
    classes_train = []
    classes_test = []
    index_test = []
    for index, content in enumerate(contents):
        temp = []
        words = simpleTokenize(content)
        twLen = float(len(words))
        sentiScore = afinn.score(stemContent(content))
        readScore = textstat.coleman_liau_index(content)

        temp.append(twLen)

        if content.count('URRL') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('HHTTG') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('USSERNM') > 0:
            temp.append(1)
        else:
            temp.append(0)

        temp.append(sentiScore / twLen)
        temp.append(readScore)
        temp.append(parseLength[index] / twLen)
        temp.append(headCount[index] / twLen)
        temp += POScounts[index]
        if content.count('!') > 0:
            temp.append(1)
        else:
            temp.append(0)
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

        if ids[index] not in excludeList:
            semanticFeatures_train.append(numpy.array(temp))
            classes_train.append(labels[index])
        else:
            semanticFeatures_test.append(numpy.array(temp))
            classes_test.append(labels[index])
            print ids[index] + '\t' + contents[index] + '\t' + str(usernames[index])

    feature_train = csr_matrix(numpy.array(semanticFeatures_train))
    feature_test = csr_matrix(numpy.array(semanticFeatures_test))

    model = svm.SVC()
    model.fit(feature_train, classes_train)
    # joblib.dump(model, 'results/full.pkl')
    # model = joblib.load('results/full.pkl')
    predictions = model.predict(feature_test)
    score = model.decision_function(feature_test)
    print classes_test
    print predictions
    print score

    tempListFile.close()


def trainModel(groupTitle):
    print 'loading...'
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    group = 0
    afinn = Afinn()
    posFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.pos', 'r')
    negFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(group) + '.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(group) + '.neg', 'r')
    posPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.pos', 'r')
    negPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(group) + '.neg', 'r')

    ids = []
    contents = []
    scores = []
    labels = []
    parseLength = []
    headCount = []
    usernames = []
    POScounts = []

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
        contents.append(text)
        scores.append(score)
        labels.append(1)

    for line in negFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
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

    semanticFeatures_train = []
    classes_train = []

    for index, content in enumerate(contents):
        temp = []
        words = simpleTokenize(content)
        twLen = float(len(words))
        sentiScore = afinn.score(stemContent(content))
        readScore = textstat.coleman_liau_index(content)

        temp.append(twLen)

        if content.count('URRL') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('HHTTG') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('USSERNM') > 0:
            temp.append(1)
        else:
            temp.append(0)

        temp.append(sentiScore / twLen)
        temp.append(readScore)
        temp.append(parseLength[index] / twLen)
        temp.append(headCount[index] / twLen)
        temp += POScounts[index]
        if content.count('!') > 0:
            temp.append(1)
        else:
            temp.append(0)
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

        semanticFeatures_train.append(numpy.array(temp))
        classes_train.append(labels[index])

    feature_train = csr_matrix(numpy.array(semanticFeatures_train))

    model = svm.SVC()
    model.fit(feature_train, classes_train)
    joblib.dump(model, 'models/full.pkl')


def extractor():
    inputFile = open('infer/test.predict', 'r')
    tempData = {}
    tempOutput = {}
    posCount = {'N': 0, 'V': 0, 'A': 0}
    lengthOutput = []
    headOutput = []
    posOutput = []

    for line in inputFile:
        if line.strip() != '':
            words = line.strip().split()
            tempData[words[0]] = words[6]
            tempOutput[int(words[0])] = (words[1], int(words[6]), words[4])
            if words[4] in ['N', '^']:
                posCount['N'] += 1
            elif words[4] == 'V':
                posCount['V'] += 1
            elif words[4] in ['A', 'R']:
                posCount['A'] += 1
        else:
            longLen = longestLength(tempData)
            lengthOutput.append(longLen)
            headOutput.append(len(outputHeads(tempOutput).split()))
            posOutput.append((posCount['N'], posCount['V'], posCount['A']))
            tempData = {}
            tempOutput = {}
            posCount = {'N': 0, 'V': 0, 'A': 0}
    inputFile.close()
    return lengthOutput, headOutput, posOutput


def infer():
    print 'loading...'
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')
    afinn = Afinn()
    mentionFile = open('infer/mention.input', 'r')
    inputFile = open('infer/test', 'r')

    contents = []
    usernames = []

    for line in inputFile:
        text = line.strip()
        contents.append(text)

    for i in range(len(contents)):
        usernames.append([])

    for line in mentionFile:
        items = line.strip().split(';')
        if len(items) == 0:
            usernames.append([])
        else:
            usernames.append(items)

    parseLength, headCount, POSoutput = extractor()

    inputFile.close()
    mentionFile.close()

    semanticFeatures_test = []
    for index, content in enumerate(contents):
        temp = []
        words = simpleTokenize(content)
        twLen = float(len(words))
        sentiScore = afinn.score(stemContent(content))
        readScore = textstat.coleman_liau_index(content)
        temp.append(twLen)

        if content.count('URRL') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('HHTTG') > 0:
            temp.append(1)
        else:
            temp.append(0)
        if content.count('USSERNM') > 0:
            temp.append(1)
        else:
            temp.append(0)

        temp.append(sentiScore / twLen)
        temp.append(readScore)
        temp.append(parseLength[index] / twLen)
        temp.append(headCount[index] / twLen)
        temp += POSRatio(POSoutput[index])
        if content.count('!') > 0:
            temp.append(1)
        else:
            temp.append(0)
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

        semanticFeatures_test.append(numpy.array(temp))

    feature_test = csr_matrix(numpy.array(semanticFeatures_test))

    model = joblib.load('models/full.pkl')
    predictions = model.predict(feature_test)
    score = model.decision_function(feature_test)
    #print classes_test
    #print predictions
    #print numpy.count_nonzero(predictions)
    for index, pred in enumerate(predictions):
        #print pred
        print score[index]
    #print score


infer()
# trainModel('totalGroup')
# run3()
# outputFilename = 'results/test.result'
# run2(3, 'simGroup', outputFile=outputFilename)
