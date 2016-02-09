import subprocess
import operator
from sklearn.feature_extraction.text import *
from sklearn import cluster
import shutil

__author__ = 'rencui'


def analysisByDay():
    posDayCount = {}
    negDayCount = {}
    posFile = open('adData/analysis/ranked/1/total.pos', 'r')
    negFile = open('adData/analysis/ranked/2/total.neg', 'r')
    for line in posFile:
        data = line.strip().split(' : ')
        day = data[1]
        if day not in posDayCount:
            posDayCount[day] = 1.0
        else:
            posDayCount[day] += 1.0
    posFile.close()

    for line in negFile:
        data = line.strip().split(' : ')
        day = data[1]
        if day not in negDayCount:
            negDayCount[day] = 1.0
        else:
            negDayCount[day] += 1.0
    negFile.close()

    print posDayCount
    print negDayCount


def maxIndex(input, num):
    line = {}
    for index in range(len(input)):
        line[index] = float(input[index])
    sorted_line = sorted(line.iteritems(), key=operator.itemgetter(1), reverse=True)
    output = []
    for i in range(num):
        output.append(sorted_line[i][0])
    return output


def fileLineCount(fileList):
    outputList = []
    for fileName in fileList:
        with open(fileName) as f:
            outputList.append(sum(1 for _ in f))
    return outputList


def brandGrouper(groupTitle, groupSize):
    print 'brand grouping...'
    groupMapper = {}
    idMapper = {}
    groupFile = open(groupTitle + '.list', 'r')
    for index, line in enumerate(groupFile):
        brands = line.strip().split()
        for brand in brands:
            groupMapper[brand] = index
    groupFile.close()

    posInputFile = open('adData/analysis/ranked/1/total.pos', 'r')
    negInputFile = open('adData/analysis/ranked/2/total.neg', 'r')
    posParseLengthFile = open('adData/analysis/ranked/Parser/parserLength.pos', 'r')
    negParseLengthFile = open('adData/analysis/ranked/Parser/parserLength.neg', 'r')
    posHeadCountFile = open('adData/analysis/ranked/Parser/parserHeadCount.pos', 'r')
    negHeadCountFile = open('adData/analysis/ranked/Parser/parserHeadCount.neg', 'r')
    posPOSCountFile = open('adData/analysis/ranked/Parser/parserPOSCount.pos', 'r')
    negPOSCountFile = open('adData/analysis/ranked/Parser/parserPOSCount.neg', 'r')

    posOutputFileList = []
    negOutputFileList = []
    posParseLengthFileList = []
    negParseLengthFileList = []
    posParseHeadFileList = []
    negParseHeadFileList = []
    posPOSCountFileList = []
    negPOSCountFileList = []
    countFileList = []
    for index in range(groupSize):
        tempPosFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(index) + '.pos', 'w')
        tempNegFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(index) + '.neg', 'w')
        countFileList.append('adData/analysis/groups/' + groupTitle + '/group' + str(index) + '.pos')
        countFileList.append('adData/analysis/groups/' + groupTitle + '/group' + str(index) + '.neg')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(index) + '.pos',
                                      'w')
        tempNegParseLengthFile = open('adData/analysis/groups/' + groupTitle + '/parserLength' + str(index) + '.neg',
                                      'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(index) + '.pos',
                                    'w')
        tempNegParseHeadFile = open('adData/analysis/groups/' + groupTitle + '/parserHeadCount' + str(index) + '.neg',
                                    'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)
        tempPosPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(index) + '.pos', 'w')
        tempNegPOSCountFile = open('adData/analysis/groups/' + groupTitle + '/parserPOSCount' + str(index) + '.neg', 'w')
        posPOSCountFileList.append(tempPosPOSCountFile)
        negPOSCountFileList.append(tempNegPOSCountFile)

    for line in posInputFile:
        items = line.strip().split(' :: ')
        if items[4] in groupMapper:
            posOutputFileList[groupMapper[items[4]]].write(line)
        idMapper[items[5]] = items[4]

    for line in negInputFile:
        items = line.strip().split(' :: ')
        if items[4] in groupMapper:
            negOutputFileList[groupMapper[items[4]]].write(line)
        idMapper[items[5]] = items[4]

    for line in posParseLengthFile:
        items = line.strip().split(' :: ')
        if idMapper[items[1]] in groupMapper:
            posParseLengthFileList[groupMapper[idMapper[items[1]]]].write(line)

    for line in negParseLengthFile:
        items = line.strip().split(' :: ')
        if idMapper[items[1]] in groupMapper:
            negParseLengthFileList[groupMapper[idMapper[items[1]]]].write(line)

    for line in posHeadCountFile:
        items = line.strip().split(' :: ')
        if idMapper[items[1]] in groupMapper:
            posParseHeadFileList[groupMapper[idMapper[items[1]]]].write(line)

    for line in negHeadCountFile:
        items = line.strip().split(' :: ')
        if idMapper[items[1]] in groupMapper:
            negParseHeadFileList[groupMapper[idMapper[items[1]]]].write(line)

    for line in posPOSCountFile:
        items = line.strip().split(' :: ')
        if idMapper[items[1]] in groupMapper:
            posPOSCountFileList[groupMapper[idMapper[items[1]]]].write(line)

    for line in negPOSCountFile:
        items = line.strip().split(' :: ')
        if idMapper[items[1]] in groupMapper:
            negPOSCountFileList[groupMapper[idMapper[items[1]]]].write(line)

    for index in range(groupSize):
        posOutputFileList[index].close()
        negOutputFileList[index].close()
        posParseLengthFileList[index].close()
        negParseLengthFileList[index].close()
        posParseHeadFileList[index].close()
        negParseHeadFileList[index].close()
        posPOSCountFileList[index].close()
        negPOSCountFileList[index].close()
    posInputFile.close()
    negInputFile.close()
    posParseLengthFile.close()
    negParseLengthFile.close()
    posHeadCountFile.close()
    negHeadCountFile.close()
    print fileLineCount(countFileList)


def topicGrouper(groupSize):
    print 'topic grouping...'
    data = []
    # punctuations = set(string.punctuation)
    posFile = open('adData/analysis/ranked/1/total.pos', 'r')
    negFile = open('adData/analysis/ranked/2/total.neg', 'r')
    csvFile = open('LDA/LDAinput.csv', 'w')
    listFile = open('LDA/LDAinput.list', 'w')
    for line in posFile:
        item = line.strip().split(' :: ')
        data.append([item[3], item[5]])
    for line in negFile:
        item = line.strip().split(' :: ')
        data.append([item[3], item[5]])
    posFile.close()
    negFile.close()
    for tweet in data:
        csvFile.write(tweet[0].replace('"', '\'') + '\n')
        listFile.write(tweet[1] + '\n')
    csvFile.close()
    listFile.close()

    print 'running LDA...'
    subprocess.check_output('java -Xmx1024m -jar LDA/tmt-0.4.0.jar LDA/assign.scala', shell=True)

    distFile = open('LDA/TMTSnapshots/document-topic-distributions.csv', 'r')
    topicOut = {}
    for line in distFile:
        seg = line.strip().split(',')
        if seg[1] != 'NaN':
            topicOutList = maxIndex(seg[1:], 3)
            topicOut[int(seg[0])] = topicOutList
    distFile.close()

    topicMapper = {}
    for index, value in topicOut.items():
        topicMapper[data[index][1]] = value[0]

    posInputFile = open('adData/analysis/ranked/1/total.pos', 'r')
    negInputFile = open('adData/analysis/ranked/2/total.neg', 'r')
    posParseLengthFile = open('adData/analysis/ranked/Parser/parserLength.pos', 'r')
    negParseLengthFile = open('adData/analysis/ranked/Parser/parserLength.neg', 'r')
    posHeadCountFile = open('adData/analysis/ranked/Parser/parserHeadCount.pos', 'r')
    negHeadCountFile = open('adData/analysis/ranked/Parser/parserHeadCount.neg', 'r')
    posPOSCountFile = open('adData/analysis/ranked/Parser/parserPOSCount.pos', 'r')
    negPOSCountFile = open('adData/analysis/ranked/Parser/parserPOSCount.neg', 'r')

    posOutputFileList = []
    negOutputFileList = []
    posParseLengthFileList = []
    negParseLengthFileList = []
    posParseHeadFileList = []
    negParseHeadFileList = []
    posPOSCountFileList = []
    negPOSCountFileList = []
    countFileList = []
    for index in range(groupSize):
        tempPosFile = open('adData/analysis/groups/topicGroup/group' + str(index) + '.pos', 'w')
        tempNegFile = open('adData/analysis/groups/topicGroup/group' + str(index) + '.neg', 'w')
        countFileList.append('adData/analysis/groups/topicGroup/group' + str(index) + '.pos')
        countFileList.append('adData/analysis/groups/topicGroup/group' + str(index) + '.neg')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('adData/analysis/groups/topicGroup/parserLength' + str(index) + '.pos', 'w')
        tempNegParseLengthFile = open('adData/analysis/groups/topicGroup/parserLength' + str(index) + '.neg', 'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('adData/analysis/groups/topicGroup/parserHeadCount' + str(index) + '.pos', 'w')
        tempNegParseHeadFile = open('adData/analysis/groups/topicGroup/parserHeadCount' + str(index) + '.neg', 'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)
        tempPosPOSCountFile = open('adData/analysis/groups/topicGroup/parserPOSCount' + str(index) + '.pos', 'w')
        tempNegPOSCountFile = open('adData/analysis/groups/topicGroup/parserPOSCount' + str(index) + '.neg', 'w')
        posPOSCountFileList.append(tempPosPOSCountFile)
        negPOSCountFileList.append(tempNegPOSCountFile)

    for line in posInputFile:
        items = line.strip().split(' :: ')
        if items[5] in topicMapper:
            posOutputFileList[topicMapper[items[5]]].write(line)

    for line in negInputFile:
        items = line.strip().split(' :: ')
        if items[5] in topicMapper:
            negOutputFileList[topicMapper[items[5]]].write(line)

    for line in posParseLengthFile:
        items = line.strip().split(' :: ')
        if items[1] in topicMapper:
            posParseLengthFileList[topicMapper[items[1]]].write(line)

    for line in negParseLengthFile:
        items = line.strip().split(' :: ')
        if items[1] in topicMapper:
            negParseLengthFileList[topicMapper[items[1]]].write(line)

    for line in posHeadCountFile:
        items = line.strip().split(' :: ')
        if items[1] in topicMapper:
            posParseHeadFileList[topicMapper[items[1]]].write(line)

    for line in negHeadCountFile:
        items = line.strip().split(' :: ')
        if items[1] in topicMapper:
            negParseHeadFileList[topicMapper[items[1]]].write(line)

    for line in posPOSCountFile:
        items = line.strip().split(' :: ')
        if items[1] in topicMapper:
            posPOSCountFileList[topicMapper[items[1]]].write(line)

    for line in negPOSCountFile:
        items = line.strip().split(' :: ')
        if items[1] in topicMapper:
            negPOSCountFileList[topicMapper[items[1]]].write(line)


    for index in range(groupSize):
        posOutputFileList[index].close()
        negOutputFileList[index].close()
        posParseLengthFileList[index].close()
        negParseLengthFileList[index].close()
        posParseHeadFileList[index].close()
        negParseHeadFileList[index].close()
        posPOSCountFileList[index].close()
        negPOSCountFileList[index].close()
    posInputFile.close()
    negInputFile.close()
    posParseLengthFile.close()
    negParseLengthFile.close()
    posHeadCountFile.close()
    negHeadCountFile.close()
    posPOSCountFile.close()
    negPOSCountFile.close()
    print fileLineCount(countFileList)


def similarityGrouper(groupSize):
    print 'similarity grouping...'
    tweets = []
    ids = []
    idMapper = {}
    posInputFile = open('adData/analysis/ranked/1/total.pos', 'r')
    negInputFile = open('adData/analysis/ranked/2/total.neg', 'r')

    for line in posInputFile:
        items = line.strip().split(' :: ')
        tweets.append(items[3])
        ids.append(items[5])
    for line in negInputFile:
        items = line.strip().split(' :: ')
        tweets.append(items[3])
        ids.append(items[5])
    posInputFile.close()
    negInputFile.close()

    #vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=0, stop_words='english')
    vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=1, stop_words='english', binary='True')
    matrix = vectorizer.fit_transform(tweets)
    print len(vectorizer.get_feature_names())

    print 'Running Kmeans...'
    kmeans = cluster.KMeans(n_clusters=groupSize, init='k-means++')
    kmeans.fit(matrix)
    for index, label in enumerate(kmeans.labels_):
        idMapper[ids[index]] = label

    posInputFile = open('adData/analysis/ranked/1/total.pos', 'r')
    negInputFile = open('adData/analysis/ranked/2/total.neg', 'r')
    posParseLengthFile = open('adData/analysis/ranked/Parser/parserLength.pos', 'r')
    negParseLengthFile = open('adData/analysis/ranked/Parser/parserLength.neg', 'r')
    posHeadCountFile = open('adData/analysis/ranked/Parser/parserHeadCount.pos', 'r')
    negHeadCountFile = open('adData/analysis/ranked/Parser/parserHeadCount.neg', 'r')
    posPOSCountFile = open('adData/analysis/ranked/Parser/parserPOSCount.pos', 'r')
    negPOSCountFile = open('adData/analysis/ranked/Parser/parserPOSCount.neg', 'r')

    posOutputFileList = []
    negOutputFileList = []
    posParseLengthFileList = []
    negParseLengthFileList = []
    posParseHeadFileList = []
    negParseHeadFileList = []
    posPOSCountFileList = []
    negPOSCountFileList = []
    # tweetID: [group, brand, performanceScore, day, time, text, parserLength, headCount]
    posDetailData = {}
    negDetailData = {}
    countFileList = []
    for index in range(groupSize):
        tempPosFile = open('adData/analysis/groups/simGroup/group' + str(index) + '.pos', 'w')
        tempNegFile = open('adData/analysis/groups/simGroup/group' + str(index) + '.neg', 'w')
        countFileList.append('adData/analysis/groups/simGroup/group' + str(index) + '.pos')
        countFileList.append('adData/analysis/groups/simGroup/group' + str(index) + '.neg')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('adData/analysis/groups/simGroup/parserLength' + str(index) + '.pos', 'w')
        tempNegParseLengthFile = open('adData/analysis/groups/simGroup/parserLength' + str(index) + '.neg', 'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('adData/analysis/groups/simGroup/parserHeadCount' + str(index) + '.pos', 'w')
        tempNegParseHeadFile = open('adData/analysis/groups/simGroup/parserHeadCount' + str(index) + '.neg', 'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)
        tempPosPOSCountFile = open('adData/analysis/groups/simGroup/parserPOSCount' + str(index) + '.pos', 'w')
        tempNegPOSCountFile = open('adData/analysis/groups/simGroup/parserPOSCount' + str(index) + '.neg', 'w')
        posPOSCountFileList.append(tempPosPOSCountFile)
        negPOSCountFileList.append(tempNegPOSCountFile)

    for line in posInputFile:
        items = line.strip().split(' :: ')
        if items[5] in idMapper:
            posOutputFileList[idMapper[items[5]]].write(line)
            posDetailData[items[5]] = [idMapper[items[5]], items[4], items[0], items[1], items[2], items[3]]

    for line in negInputFile:
        items = line.strip().split(' :: ')
        if items[5] in idMapper:
            negOutputFileList[idMapper[items[5]]].write(line)
            negDetailData[items[5]] = [idMapper[items[5]], items[4], items[0], items[1], items[2], items[3]]

    for line in posParseLengthFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            posParseLengthFileList[idMapper[items[1]]].write(line)
            posDetailData[items[1]].append(items[0])

    for line in negParseLengthFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            negParseLengthFileList[idMapper[items[1]]].write(line)
            negDetailData[items[1]].append(items[0])

    for line in posHeadCountFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            posParseHeadFileList[idMapper[items[1]]].write(line)
            posDetailData[items[1]].append(items[0])

    for line in negHeadCountFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            negParseHeadFileList[idMapper[items[1]]].write(line)
            negDetailData[items[1]].append(items[0])

    for line in posPOSCountFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            posPOSCountFileList[idMapper[items[1]]].write(line)

    for line in negPOSCountFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            negPOSCountFileList[idMapper[items[1]]].write(line)

    for index in range(groupSize):
        posOutputFileList[index].close()
        negOutputFileList[index].close()
        posParseLengthFileList[index].close()
        negParseLengthFileList[index].close()
        posParseHeadFileList[index].close()
        negParseHeadFileList[index].close()
        posPOSCountFileList[index].close()
        negPOSCountFileList[index].close()
    posInputFile.close()
    negInputFile.close()
    posParseLengthFile.close()
    negParseLengthFile.close()
    posHeadCountFile.close()
    negHeadCountFile.close()
    posPOSCountFile.close()
    negPOSCountFile.close()
    print fileLineCount(countFileList)

    '''
    posDetailFile = open('adData/analysis/groups/simGroup/details.pos', 'w')
    negDetailFile = open('adData/analysis/groups/simGroup/details.neg', 'w')
    for id, value in posDetailData.items():
        posDetailFile.write(id+'\t'+str(value[0])+'\t'+value[1]+'\t'+value[2]+'\t'+value[3]+'\t'+value[4]+'\t'+value[6]+'\t'+value[7]+'\n')
    for id, value in negDetailData.items():
        negDetailFile.write(id+'\t'+str(value[0])+'\t'+value[1]+'\t'+value[2]+'\t'+value[3]+'\t'+value[4]+'\t'+value[6]+'\t'+value[7]+'\n')
    posDetailFile.close()
    negDetailFile.close()
    '''


def totalGrouper():
    shutil.copy2('adData/analysis/ranked/1/total.pos', 'adData/analysis/groups/totalGroup/group0.pos')
    shutil.copy2('adData/analysis/ranked/2/total.neg', 'adData/analysis/groups/totalGroup/group0.neg')
    shutil.copy2('adData/analysis/ranked/Parser/parserHeadCount.pos', 'adData/analysis/groups/totalGroup/parserHeadCount0.pos')
    shutil.copy2('adData/analysis/ranked/Parser/parserHeadCount.neg', 'adData/analysis/groups/totalGroup/parserHeadCount0.neg')
    shutil.copy2('adData/analysis/ranked/Parser/parserLength.pos', 'adData/analysis/groups/totalGroup/parserLength0.pos')
    shutil.copy2('adData/analysis/ranked/Parser/parserLength.neg', 'adData/analysis/groups/totalGroup/parserLength0.neg')
    shutil.copy2('adData/analysis/ranked/Parser/parserPOSCount.pos', 'adData/analysis/groups/totalGroup/parserPOSCount0.pos')
    shutil.copy2('adData/analysis/ranked/Parser/parserPOSCount.neg', 'adData/analysis/groups/totalGroup/parserPOSCount0.neg')
    print fileLineCount(['adData/analysis/groups/totalGroup/group0.pos', 'adData/analysis/groups/totalGroup/group0.neg'])

def similarityGrouper2(groupSize):
    tweets = []
    ids = []
    idMapper = {}
    posInputFile = open('adData/analysis/groups/simGroup2/group2.pos', 'r')
    negInputFile = open('adData/analysis/groups/simGroup2/group2.neg', 'r')

    for line in posInputFile:
        items = line.strip().split(' :: ')
        tweets.append(items[3])
        ids.append(items[5])
    for line in negInputFile:
        items = line.strip().split(' :: ')
        tweets.append(items[3])
        ids.append(items[5])
    posInputFile.close()
    negInputFile.close()

    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=0, stop_words='english')
    #vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=0, stop_words='english', binary='True')
    matrix = vectorizer.fit_transform(tweets)
    print len(vectorizer.get_feature_names())


    print 'Running Kmeans...'
    kmeans = cluster.KMeans(n_clusters=groupSize, init='k-means++')
    kmeans.fit(matrix)
    for index, label in enumerate(kmeans.labels_):
        idMapper[ids[index]] = label

    posInputFile = open('adData/analysis/groups/simGroup2/group2.pos', 'r')
    negInputFile = open('adData/analysis/groups/simGroup2/group2.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/simGroup2/parserLength2.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/simGroup2/parserLength2.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/simGroup2/parserHeadCount2.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/simGroup2/parserHeadCount2.neg', 'r')

    posOutputFileList = []
    negOutputFileList = []
    posParseLengthFileList = []
    negParseLengthFileList = []
    posParseHeadFileList = []
    negParseHeadFileList = []
    # tweetID: [group, brand, performanceScore, day, time, text, parserLength, headCount]
    posDetailData = {}
    negDetailData = {}

    for index in range(groupSize):
        tempPosFile = open('adData/analysis/groups/simGroup3/group' + str(index) + '.pos', 'w')
        tempNegFile = open('adData/analysis/groups/simGroup3/group' + str(index) + '.neg', 'w')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('adData/analysis/groups/simGroup3/parserLength' + str(index) + '.pos', 'w')
        tempNegParseLengthFile = open('adData/analysis/groups/simGroup3/parserLength' + str(index) + '.neg', 'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('adData/analysis/groups/simGroup3/parserHeadCount' + str(index) + '.pos', 'w')
        tempNegParseHeadFile = open('adData/analysis/groups/simGroup3/parserHeadCount' + str(index) + '.neg', 'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)

    for line in posInputFile:
        items = line.strip().split(' :: ')
        if items[5] in idMapper:
            posOutputFileList[idMapper[items[5]]].write(line)
            posDetailData[items[5]] = [idMapper[items[5]], items[4], items[0], items[1], items[2], items[3]]

    for line in negInputFile:
        items = line.strip().split(' :: ')
        if items[5] in idMapper:
            negOutputFileList[idMapper[items[5]]].write(line)
            negDetailData[items[5]] = [idMapper[items[5]], items[4], items[0], items[1], items[2], items[3]]

    for line in posParseLengthFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            posParseLengthFileList[idMapper[items[1]]].write(line)
            posDetailData[items[1]].append(items[0])

    for line in negParseLengthFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            negParseLengthFileList[idMapper[items[1]]].write(line)
            negDetailData[items[1]].append(items[0])

    for line in posHeadCountFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            posParseHeadFileList[idMapper[items[1]]].write(line)
            posDetailData[items[1]].append(items[0])

    for line in negHeadCountFile:
        items = line.strip().split(' :: ')
        if items[1] in idMapper:
            negParseHeadFileList[idMapper[items[1]]].write(line)
            negDetailData[items[1]].append(items[0])

    for index in range(groupSize):
        posOutputFileList[index].close()
        negOutputFileList[index].close()
        posParseLengthFileList[index].close()
        negParseLengthFileList[index].close()
        posParseHeadFileList[index].close()
        negParseHeadFileList[index].close()
    posInputFile.close()
    negInputFile.close()
    posParseLengthFile.close()
    negParseLengthFile.close()
    posHeadCountFile.close()
    negHeadCountFile.close()

    posDetailFile = open('adData/analysis/groups/simGroup3/details.pos', 'w')
    negDetailFile = open('adData/analysis/groups/simGroup3/details.neg', 'w')
    for id, value in posDetailData.items():
        posDetailFile.write(id+'\t'+str(value[0])+'\t'+value[1]+'\t'+value[2]+'\t'+value[3]+'\t'+value[4]+'\t'+value[6]+'\t'+value[7]+'\n')
    for id, value in negDetailData.items():
        negDetailFile.write(id+'\t'+str(value[0])+'\t'+value[1]+'\t'+value[2]+'\t'+value[3]+'\t'+value[4]+'\t'+value[6]+'\t'+value[7]+'\n')
    posDetailFile.close()
    negDetailFile.close()


#totalGrouper()
#brandGrouper('subBrandGroup', 3)
#brandGrouper('brandGroup', 3)
#topicGrouper(5)
similarityGrouper(5)