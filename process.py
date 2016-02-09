__author__ = 'rencui'
import numpy
import json
from textstat.textstat import textstat
import utilities
from sklearn.feature_extraction.text import *
from sklearn import svm
#from sklearn.linear_model import LogisticRegression
#from sknn.mlp import Classifier, Layer
from sklearn import cross_validation
from tokenizer import simpleTokenize
import logging
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

#vectorMode 1: tfidf, 2: binaryCount
#featureMode 0: semantic only, 1: vector only, 2: both
def run(groupSize, groupTitle, vectorMode, featureMode):
    resultFile = open('outputSVM.result', 'a')
    mentionFile = open('adData/analysis/ranked/mention.json', 'r')
    mentionMapper = {}
    for line in mentionFile:
        mention = json.loads(line.strip())
        if mention['verified'] == 'true':
            verify = 1
        else:
            verify = 0
        mentionMapper[mention['screen_name']] = (verify, mention['followers_count'])
    mentionFile.close()

    print groupTitle
    resultFile.write(groupTitle+'\n')
    for group in range(groupSize):
        print 'group: '+str(group)
        resultFile.write('group: '+str(group)+'\n')
        posFile = open('adData/analysis/groups/'+groupTitle+'/group'+str(group)+'.pos', 'r')
        negFile = open('adData/analysis/groups/'+groupTitle+'/group'+str(group)+'.neg', 'r')
        happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
        #LDAFile = open('tmtData/total.csv', 'w')
        posParseLengthFile = open('adData/analysis/groups/'+groupTitle+'/parserLength'+str(group)+'.pos', 'r')
        negParseLengthFile = open('adData/analysis/groups/'+groupTitle+'/parserLength'+str(group)+'.neg', 'r')
        posHeadCountFile = open('adData/analysis/groups/'+groupTitle+'/parserHeadCount'+str(group)+'.pos', 'r')
        negHeadCountFile = open('adData/analysis/groups/'+groupTitle+'/parserHeadCount'+str(group)+'.neg', 'r')

        contents = []
        scores = []
        days = []
        time = []
        labels = []
        parseLength = []
        headCount = []
        usernames = []

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
            #LDAFile.write('"1","' + text.replace('"', "'") + '"\n')
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
            #LDAFile.write('"2","' + text.replace('"', "'") + '"\n')
            labels.append(0)

        if vectorMode == 1:
            resultFile.write('tfidf \n')
            vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
            matrix = vectorizer.fit_transform(contents)
            tweetVector = matrix.toarray()
        elif vectorMode == 2:
            resultFile.write('binary count \n')
            vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english', binary='True')
            matrix = vectorizer.fit_transform(contents)
            tweetVector = matrix.toarray()
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

        '''
        print 'running pos tagger...'
        subprocess.check_output('java -XX:ParallelGCThreads=5 -Xmx950m -jar posTagger/ark-tweet-nlp-0.3.2.jar --input-format text --output-format conll adData/analysis/ranked/1/total.content > pos.taggeroutput', shell=True)
        subprocess.check_output('java -XX:ParallelGCThreads=5 -Xmx950m -jar posTagger/ark-tweet-nlp-0.3.2.jar --input-format text --output-format conll adData/analysis/ranked/2/total.content > neg.taggeroutput', shell=True)

        print 'running topic modelling...'
        topicFeatures, topicIndex = topicModeler.genTopicFeatures()
        if len(topicIndex) != len(contents):
            print 'topic modelling missing tweet'

        posFeature1 = posTagger.posConvert('pos.taggeroutput')
        posFeature2 = posTagger.posConvert('neg.taggeroutput')
        posFeature = posFeature1 + posFeature2
        if len(posFeature) != len(contents):
            print 'pos file missing tweet'
        '''

        features = []
        classes = []

        urlValue = []
        htValue = []
        #emojValue = []
        usnmValue = []
        readValue = []
        twLenValue = []
        sentiValue = []
        sentiValue2 = []

        if featureMode == 0:
            resultFile.write('semantic features only \n')
        elif featureMode == 1:
            resultFile.write('vector features only \n')
        else:
            resultFile.write('both features \n')

        for index, content in enumerate(contents):
            if featureMode == 1:
                temp = tweetVector[index]
            else:
                if featureMode == 0:
                    temp = numpy.array([])
                if featureMode == 2:
                    temp = tweetVector[index]

                twLen = len(simpleTokenize(content))
                posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
                readScore = textstat.coleman_liau_index(content)

                '''
                if posProb < 0.5:
                    sentiScore = 0
                elif posProb < 0.75:
                    sentiScore = 1
                else:
                    sentiScore = 2

                for pos in posFeature[index]:
                    temp.append(pos / twLen)
                for prob in topicFeatures[index]:
                    temp.append(prob)
                '''

                temp = numpy.append(temp, content.count('urrl'))
                temp = numpy.append(temp, content.count('hhttg'))
                #numpy.append(temp, content.count('emmoj'))
                temp = numpy.append(temp, content.count('ussernm'))
                temp = numpy.append(temp, twLen)
                temp = numpy.append(temp, posProb)
                #temp = numpy.append(temp, sentiScore)
                temp = numpy.append(temp, readScore)

                temp = numpy.append(temp, parseLength[index])
                temp = numpy.append(temp, headCount[index])

                temp = numpy.append(temp, days[index])
                temp = numpy.append(temp, time[index])

                mentionFlag = 0
                mentionFollowers = 0
                for user in usernames[index]:
                    if user in mentionMapper:
                        if mentionMapper[user][0] == 1:
                            mentionFlag = 1
                        mentionFollowers += mentionMapper[user][1]
                temp = numpy.append(temp, mentionFlag)
                temp = numpy.append(temp, mentionFollowers)

            features.append(temp)
            classes.append(labels[index])
            '''
            readValue.append(readScore)
            twLenValue.append(twLen)
            sentiValue.append(posProb)
            sentiValue2.append(sentiScore)
            urlValue.append(content.count('urrl'))
            htValue.append(content.count('hhttg'))
            #emojValue.append(content.count('emmoj'))
            usnmValue.append(content.count('ussernm'))
            '''
        '''
        print numpy.corrcoef(readValue, classes)[0, 1]
        print numpy.corrcoef(twLenValue, classes)[0, 1]
        print numpy.corrcoef(sentiValue, classes)[0, 1]
        print numpy.corrcoef(sentiValue2, classes)[0, 1]
        print numpy.corrcoef(urlValue, classes)[0, 1]
        print numpy.corrcoef(htValue, classes)[0, 1]
        #print numpy.corrcoef(emojValue, classes)[0, 1]
        print numpy.corrcoef(usnmValue, classes)[0, 1]
        print numpy.corrcoef(parseLength, classes)[0, 1]
        print numpy.corrcoef(headCount, classes)[0, 1]
        '''
        '''
        # initialize the MLP
        model = Classifier(
            layers=[
                Layer("Sigmoid", units=100),
                Layer("Softmax")],
            learning_rate=0.02,
            n_iter=25)
        '''

        precisionSum = 0.0
        recallSum = 0.0
        accuracySum = 0.0
        resultFile.flush()
        print 'running 5-fold CV...'
        for i in range(5):
            print 'case '+str(i)
            feature_train, feature_test, label_train, label_test = cross_validation.train_test_split(features, classes,
                                                                                                     test_size=0.2,
                                                                                                     random_state=0)
            X_train = numpy.array(feature_train)
            Y_train = numpy.array(label_train)
            X_test = numpy.array(feature_test)
            Y_test = numpy.array(label_test)

            model = svm.SVC()
            #model = LogisticRegression()
            model.fit(X_train, Y_train)
            predictions = model.predict(X_test)

            precisionCount = 0.0
            totalCount = 0.0
            recallCount = 0.0
            if len(predictions) != len(label_test):
                print 'inference error!'
            #print predictions
            #print label_test
            for index, label in enumerate(predictions):
                if label == 1:
                    if label_test[index] == 1:
                        precisionCount += 1
                    totalCount += 1
                if label_test[index] == 1 and label == 1:
                    recallCount += 1
            if totalCount == 0:
                #print predictions
                precision = 0
            else:
                precision = precisionCount / totalCount
            recall = recallCount / label_test.count(1)
            accuracy = model.score(X_test, Y_test)

            precisionSum += precision
            recallSum += recall
            accuracySum += accuracy
            resultFile.flush()

        outputPrecision = precisionSum / 5
        outputRecall = recallSum / 5
        outputAccuracy = accuracySum / 5
        if (outputRecall+outputPrecision) == 0:
            outputF1 = 0.0
        else:
            outputF1 = 2*outputRecall*outputPrecision/(outputRecall+outputPrecision)

        print outputPrecision
        print outputRecall
        print outputAccuracy
        print outputF1
        print ''
        resultFile.write(str(outputPrecision)+'\n')
        resultFile.write(str(outputRecall)+'\n')
        resultFile.write(str(outputAccuracy)+'\n')
        resultFile.write(str(outputF1)+'\n')
        resultFile.write('\n')
        resultFile.flush()

    resultFile.close()

#vectorMode 1: tfidf, 2: binaryCount
#featureMode 0: semantic only, 1: vector only, 2: both
run(3, 'brandGroup', 0, 0)
run(3, 'subBrandGroup', 0, 0)
run(5, 'topicGroup', 0, 0)
run(5, 'simGroup', 0, 0)
run(1, 'totalGroup', 0, 0)