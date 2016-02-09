import numpy
import json
from textstat.textstat import textstat
import utilities
from sklearn.feature_extraction.text import *
from sknn.mlp import Classifier, Layer
from sklearn import cross_validation
from tokenizer import simpleTokenize
import logging
from scipy.sparse import hstack, csr_matrix

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
def run(groupSize, groupTitle, vectorMode, featureMode, outputFile='result.output'):
    resultFile = open(outputFile, 'a')
    mentionMapper = mapMention('adData/analysis/ranked/mention.json')

    print groupTitle
    resultFile.write(groupTitle + '\n')
    for group in range(groupSize):
        print 'group: ' + str(group)
        resultFile.write('group: ' + str(group) + '\n')
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
            resultFile.write('tfidf \n')
            vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
            vectorMatrix = vectorizer.fit_transform(contents)
        elif vectorMode == 2:
            resultFile.write('binary count \n')
            vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english',
                                         binary='True')
            vectorMatrix = vectorizer.fit_transform(contents)
            print vectorMatrix.shape
        else:
            resultFile.write('no vector features \n')

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
            # numpy.append(temp, content.count('emmoj'))
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
            resultFile.write('semantic features only \n')
            features = csr_matrix(numpy.array(semanticFeatures))
        elif featureMode == 1:
            resultFile.write('vector features only \n')
            features = vectorMatrix
        else:
            resultFile.write('both features \n')
            features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeatures))), format='csr')


        # initialize the MLP
        model = Classifier(layers=[Layer("Sigmoid", units=100), Layer("Softmax")], learning_rate=0.02, n_iter=25)

        precisionSum = 0.0
        recallSum = 0.0
        accuracySum = 0.0
        resultFile.flush()
        print 'running 5-fold CV...'
        for i in range(5):
            print 'case ' + str(i)
            feature_train, feature_test, label_train, label_test = cross_validation.train_test_split(features.todense(), classes, test_size=0.2, random_state=0)

            X_train = numpy.array(feature_train)
            Y_train = numpy.array(label_train)
            X_test = numpy.array(feature_test)
            Y_test = numpy.array(label_test)

            model.fit(X_train, Y_train)
            predictions = model.predict(X_test)

            correctCount = 0.0
            totalCount = 0.0
            if len(predictions) != len(label_test):
                print 'inference error!'
                resultFile.write('inferece error!\n')
            for index, label in enumerate(predictions):
                if label == 1:
                    if label_test[index] == 1:
                        correctCount += 1
                    totalCount += 1
            if totalCount == 0:
                precision = 0
            else:
                precision = correctCount / totalCount
            recall = correctCount / label_test.count(1)
            accuracy = model.score(X_test, Y_test)

            precisionSum += precision
            recallSum += recall
            accuracySum += accuracy
            resultFile.flush()

        outputPrecision = precisionSum / 5
        outputRecall = recallSum / 5
        outputAccuracy = accuracySum / 5
        if (outputRecall + outputPrecision) == 0:
            outputF1 = 0.0
        else:
            outputF1 = 2 * outputRecall * outputPrecision / (outputRecall + outputPrecision)

        print outputPrecision
        print outputRecall
        print outputAccuracy
        print outputF1
        print ''
        resultFile.write(str(outputPrecision) + '\n')
        resultFile.write(str(outputRecall) + '\n')
        resultFile.write(str(outputAccuracy) + '\n')
        resultFile.write(str(outputF1) + '\n')
        resultFile.write('\n')
        resultFile.flush()

    resultFile.close()


# vectorMode 1: tfidf, 2: binaryCount
# featureMode 0: semantic only, 1: vector only, 2: both
outputFilename = 'results/MLP_unigram.result'

'''
run(3, 'brandGroup', 0, 0, outputFile=outputFilename)
run(3, 'subBrandGroup', 0, 0, outputFile=outputFilename)
run(5, 'topicGroup', 0, 0, outputFile=outputFilename)
run(5, 'simGroup', 0, 0, outputFile=outputFilename)
run(1, 'totalGroup', 0, 0, outputFile=outputFilename)

run(3, 'brandGroup', 2, 1, outputFile=outputFilename)
run(3, 'subBrandGroup', 2, 1, outputFile=outputFilename)
run(5, 'topicGroup', 2, 1, outputFile=outputFilename)
run(5, 'simGroup', 2, 1, outputFile=outputFilename)
run(1, 'totalGroup', 2, 1, outputFile=outputFilename)
'''
run(3, 'brandGroup', 2, 2, outputFile=outputFilename)
run(3, 'subBrandGroup', 2, 2, outputFile=outputFilename)
run(5, 'topicGroup', 2, 2, outputFile=outputFilename)
run(5, 'simGroup', 2, 2, outputFile=outputFilename)
#run(1, 'totalGroup', 2, 2, outputFile=outputFilename)