import subprocess
import operator
from sklearn.feature_extraction.text import *
from sklearn import cluster
import shutil

__author__ = 'rencui'


def analysisByDay():
    posDayCount = {}
    negDayCount = {}
    posFile = open('dataset/experiment/ranked/total.pos', 'r')
    negFile = open('dataset/experiment/ranked/total.neg', 'r')
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

    posInputFile = open('dataset/experiment/ranked/total.pos', 'r')
    negInputFile = open('dataset/experiment/ranked/total.neg', 'r')
    posParseLengthFile = open('dataset/experiment/parser/parserLength.pos', 'r')
    negParseLengthFile = open('dataset/experiment/parser/parserLength.neg', 'r')
    posHeadCountFile = open('dataset/experiment/parser/parserHeadCount.pos', 'r')
    negHeadCountFile = open('dataset/experiment/parser/parserHeadCount.neg', 'r')
    posPOSCountFile = open('dataset/experiment/parser/parserPOSCount.pos', 'r')
    negPOSCountFile = open('dataset/experiment/parser/parserPOSCount.neg', 'r')

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
        tempPosFile = open('dataset/experiment/groups/' + groupTitle + '/group_' + str(index) + '.pos', 'w')
        tempNegFile = open('dataset/experiment/groups/' + groupTitle + '/group_' + str(index) + '.neg', 'w')
        countFileList.append('dataset/experiment/groups/' + groupTitle + '/group_' + str(index) + '.pos')
        countFileList.append('dataset/experiment/groups/' + groupTitle + '/group_' + str(index) + '.neg')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('dataset/experiment/groups/' + groupTitle + '/parserLength_' + str(index) + '.pos',
                                      'w')
        tempNegParseLengthFile = open('dataset/experiment/groups/' + groupTitle + '/parserLength_' + str(index) + '.neg',
                                      'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('dataset/experiment/groups/' + groupTitle + '/parserHeadCount_' + str(index) + '.pos',
                                    'w')
        tempNegParseHeadFile = open('dataset/experiment/groups/' + groupTitle + '/parserHeadCount_' + str(index) + '.neg',
                                    'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)
        tempPosPOSCountFile = open('dataset/experiment/groups/' + groupTitle + '/parserPOSCount_' + str(index) + '.pos', 'w')
        tempNegPOSCountFile = open('dataset/experiment/groups/' + groupTitle + '/parserPOSCount_' + str(index) + '.neg', 'w')
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
    print 'Brand Group sizes: '+str(fileLineCount(countFileList))


def topicGrouper(groupSize):
    print 'topic grouping...'
    data = []
    # punctuations = set(string.punctuation)
    posFile = open('dataset/experiment/ranked/total.pos', 'r')
    negFile = open('dataset/experiment/ranked/total.neg', 'r')
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

    posInputFile = open('dataset/experiment/ranked/total.pos', 'r')
    negInputFile = open('dataset/experiment/ranked/total.neg', 'r')
    posParseLengthFile = open('dataset/experiment/parser/parserLength.pos', 'r')
    negParseLengthFile = open('dataset/experiment/parser/parserLength.neg', 'r')
    posHeadCountFile = open('dataset/experiment/parser/parserHeadCount.pos', 'r')
    negHeadCountFile = open('dataset/experiment/parser/parserHeadCount.neg', 'r')
    posPOSCountFile = open('dataset/experiment/parser/parserPOSCount.pos', 'r')
    negPOSCountFile = open('dataset/experiment/parser/parserPOSCount.neg', 'r')

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
        tempPosFile = open('dataset/experiment/groups/topicGroup/group_' + str(index) + '.pos', 'w')
        tempNegFile = open('dataset/experiment/groups/topicGroup/group_' + str(index) + '.neg', 'w')
        countFileList.append('dataset/experiment/groups/topicGroup/group_' + str(index) + '.pos')
        countFileList.append('dataset/experiment/groups/topicGroup/group_' + str(index) + '.neg')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('dataset/experiment/groups/topicGroup/parserLength_' + str(index) + '.pos', 'w')
        tempNegParseLengthFile = open('dataset/experiment/groups/topicGroup/parserLength_' + str(index) + '.neg', 'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('dataset/experiment/groups/topicGroup/parserHeadCount_' + str(index) + '.pos', 'w')
        tempNegParseHeadFile = open('dataset/experiment/groups/topicGroup/parserHeadCount_' + str(index) + '.neg', 'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)
        tempPosPOSCountFile = open('dataset/experiment/groups/topicGroup/parserPOSCount_' + str(index) + '.pos', 'w')
        tempNegPOSCountFile = open('dataset/experiment/groups/topicGroup/parserPOSCount_' + str(index) + '.neg', 'w')
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
    print 'Topic Group size: '+str(fileLineCount(countFileList))


def similarityGrouper(groupSize):
    print 'similarity grouping...'
    tweets = []
    ids = []
    idMapper = {}
    posInputFile = open('dataset/experiment/ranked/total.pos', 'r')
    negInputFile = open('dataset/experiment/ranked/total.neg', 'r')

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

    posInputFile = open('dataset/experiment/ranked/total.pos', 'r')
    negInputFile = open('dataset/experiment/ranked/total.neg', 'r')
    posParseLengthFile = open('dataset/experiment/parser/parserLength.pos', 'r')
    negParseLengthFile = open('dataset/experiment/parser/parserLength.neg', 'r')
    posHeadCountFile = open('dataset/experiment/parser/parserHeadCount.pos', 'r')
    negHeadCountFile = open('dataset/experiment/parser/parserHeadCount.neg', 'r')
    posPOSCountFile = open('dataset/experiment/parser/parserPOSCount.pos', 'r')
    negPOSCountFile = open('dataset/experiment/parser/parserPOSCount.neg', 'r')

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
        tempPosFile = open('dataset/experiment/groups/simGroup/group_' + str(index) + '.pos', 'w')
        tempNegFile = open('dataset/experiment/groups/simGroup/group_' + str(index) + '.neg', 'w')
        countFileList.append('dataset/experiment/groups/simGroup/group_' + str(index) + '.pos')
        countFileList.append('dataset/experiment/groups/simGroup/group_' + str(index) + '.neg')
        posOutputFileList.append(tempPosFile)
        negOutputFileList.append(tempNegFile)
        tempPosParseLengthFile = open('dataset/experiment/groups/simGroup/parserLength_' + str(index) + '.pos', 'w')
        tempNegParseLengthFile = open('dataset/experiment/groups/simGroup/parserLength_' + str(index) + '.neg', 'w')
        posParseLengthFileList.append(tempPosParseLengthFile)
        negParseLengthFileList.append(tempNegParseLengthFile)
        tempPosParseHeadFile = open('dataset/experiment/groups/simGroup/parserHeadCount_' + str(index) + '.pos', 'w')
        tempNegParseHeadFile = open('dataset/experiment/groups/simGroup/parserHeadCount_' + str(index) + '.neg', 'w')
        posParseHeadFileList.append(tempPosParseHeadFile)
        negParseHeadFileList.append(tempNegParseHeadFile)
        tempPosPOSCountFile = open('dataset/experiment/groups/simGroup/parserPOSCount_' + str(index) + '.pos', 'w')
        tempNegPOSCountFile = open('dataset/experiment/groups/simGroup/parserPOSCount_' + str(index) + '.neg', 'w')
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
    print 'Similarity Group sizes: '+str(fileLineCount(countFileList))

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
    shutil.copy2('dataset/experiment/ranked/total.pos', 'dataset/experiment/groups/totalGroup/group_0.pos')
    shutil.copy2('dataset/experiment/ranked/total.neg', 'dataset/experiment/groups/totalGroup/group_0.neg')
    shutil.copy2('dataset/experiment/parser/parserHeadCount.pos', 'dataset/experiment/groups/totalGroup/parserHeadCount_0.pos')
    shutil.copy2('dataset/experiment/parser/parserHeadCount.neg', 'dataset/experiment/groups/totalGroup/parserHeadCount_0.neg')
    shutil.copy2('dataset/experiment/parser/parserLength.pos', 'dataset/experiment/groups/totalGroup/parserLength_0.pos')
    shutil.copy2('dataset/experiment/parser/parserLength.neg', 'dataset/experiment/groups/totalGroup/parserLength_0.neg')
    shutil.copy2('dataset/experiment/parser/parserPOSCount.pos', 'dataset/experiment/groups/totalGroup/parserPOSCount_0.pos')
    shutil.copy2('dataset/experiment/parser/parserPOSCount.neg', 'dataset/experiment/groups/totalGroup/parserPOSCount_0.neg')
    print 'Total Group size: '+str(fileLineCount(['dataset/experiment/groups/totalGroup/group_0.pos', 'dataset/experiment/groups/totalGroup/group_0.neg']))

def similarityGrouper2(groupSize):
    tweets = []
    ids = []
    idMapper = {}
    posInputFile = open('dataset/experiment/groups/simGroup2/group2.pos', 'r')
    negInputFile = open('dataset/experiment/groups/simGroup2/group2.neg', 'r')

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

    posInputFile = open('dataset/experiment/groups/simGroup2/group2.pos', 'r')
    negInputFile = open('dataset/experiment/groups/simGroup2/group2.neg', 'r')
    posParseLengthFile = open('dataset/experiment/groups/simGroup2/parserLength2.pos', 'r')
    negParseLengthFile = open('dataset/experiment/groups/simGroup2/parserLength2.neg', 'r')
    posHeadCountFile = open('dataset/experiment/groups/simGroup2/parserHeadCount2.pos', 'r')
    negHeadCountFile = open('dataset/experiment/groups/simGroup2/parserHeadCount2.neg', 'r')

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
        tempPosFile = open('dataset/experiment/groups/simGroup_3/group' + str(index) + '.pos', 'w')
        tempNegFile = open('dataset/experiment/groups/simGroup_3/group' + str(index) + '.neg', 'w')
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

    posDetailFile = open('dataset/experiment/groups/simGroup3/details.pos', 'w')
    negDetailFile = open('dataset/experiment/groups/simGroup3/details.neg', 'w')
    for id, value in posDetailData.items():
        posDetailFile.write(id+'\t'+str(value[0])+'\t'+value[1]+'\t'+value[2]+'\t'+value[3]+'\t'+value[4]+'\t'+value[6]+'\t'+value[7]+'\n')
    for id, value in negDetailData.items():
        negDetailFile.write(id+'\t'+str(value[0])+'\t'+value[1]+'\t'+value[2]+'\t'+value[3]+'\t'+value[4]+'\t'+value[6]+'\t'+value[7]+'\n')
    posDetailFile.close()
    negDetailFile.close()

if __name__ == '__main__':
    totalGrouper()
    #brandGrouper('subBrandGroup', 3)
    #brandGrouper('brandGroup', 3)
    #topicGrouper(5)
    #similarityGrouper(5)