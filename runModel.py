__author__ = 'rencui'
from afinn import Afinn
import subprocess
import numpy
import utilities
from textstat.textstat import textstat
from sklearn.feature_extraction.text import *
from nltk.stem.porter import *
from sklearn import cross_validation
from tokenizer import simpleTokenize
from scipy.sparse import hstack, csr_matrix
from sklearn import svm
# from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
# from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import AdaBoostClassifier

dayMapper = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}

stemmer = PorterStemmer()


def stemContent(input):
    words = simpleTokenize(input)
    out = ''
    for word in words:
        temp = stemmer.stem(word)
        out += temp + ' '
    return out.strip()


# vectorMode 1: tfidf, 2: binaryCount
# featureMode 0: semantic only, 1: vector only, 2: both
def runModel(groupSize, groupTitle, vectorMode, featureMode, trainMode, outputFile='result.output'):
    resultFile = open(outputFile, 'a')
    mentionMapper = utilities.mapMention('adData/analysis/ranked/mention.json')

    print groupTitle
    resultFile.write(groupTitle + '\n')
    for group in range(groupSize):
        print 'group: ' + str(group)
        resultFile.write('group: ' + str(group) + '\n')
        # happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
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
            time.append(utilities.hourMapper(seg[2]))
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
            time.append(utilities.hourMapper(seg[2]))
            day = seg[1]
            score = float(seg[0])
            ids.append(seg[5])
            usernames.append(username)
            days.append(dayMapper[day])
            contents.append(text)
            scores.append(score)
            labels.append(0)

        distMapper = {}

        if vectorMode == 1:
            resultFile.write('tfidf \n')
            vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 5), min_df=2, stop_words='english')
            vectorMatrix = vectorizer.fit_transform(contents)
        elif vectorMode == 2:
            resultFile.write('binary count \n')
            vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 5), min_df=2, stop_words='english',
                                         binary='True')
            vectorMatrix = vectorizer.fit_transform(contents)
        elif vectorMode == 3:
            listFile = open('LDA/LDAinput.list', 'r')
            idMapper = {}
            for index, line in enumerate(listFile):
                idMapper[index] = line.strip()
            subprocess.check_output('java -Xmx1024m -jar LDA/tmt-0.4.0.jar LDA/assign2.scala', shell=True)
            distFile = open('LDA/TMTSnapshots/document-topic-distributions.csv', 'r')
            for line in distFile:
                seg = line.strip().split(',')
                outList = []
                for item in seg[1:]:
                    outList.append(float(item))
                distMapper[idMapper[int(seg[0])]] = outList
            distFile.close()
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
        for line in posPOSCountFile:
            POScounts.append(utilities.POSRatio(line.strip().split(' :: ')[0].split(' ')))
        for line in negPOSCountFile:
            POScounts.append(utilities.POSRatio(line.strip().split(' :: ')[0].split(' ')))

        posHeadCountFile.close()
        negHeadCountFile.close()
        posParseLengthFile.close()
        negParseLengthFile.close()
        posPOSCountFile.close()
        negPOSCountFile.close()
        posFile.close()
        negFile.close()

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

        if featureMode == 0:
            resultFile.write('semantic features only \n')
            features = csr_matrix(numpy.array(semanticFeatures))
        elif featureMode == 1:
            resultFile.write('vector features only \n')
            features = vectorMatrix
        elif featureMode == 2:
            resultFile.write('embedding features only \n')
            embedFeatures = []
            for id in ids:
                embedFeatures.append(numpy.array(distMapper[id]))
            features = csr_matrix(numpy.array(embedFeatures))
        elif featureMode == 3:
            resultFile.write('embedding and semantic features only \n')
            embedFeatures = []
            for id in ids:
                embedFeatures.append(numpy.array(distMapper[id]))
            features = hstack((csr_matrix(numpy.array(semanticFeatures)), csr_matrix(numpy.array(embedFeatures))), format='csr')
        else:
            resultFile.write('vector and semantic features \n')
            features = hstack((vectorMatrix, csr_matrix(numpy.array(semanticFeatures))), format='csr')

        precisionSum = 0.0
        recallSum = 0.0
        accuracySum = 0.0
        aucSum = 0.0
        resultFile.flush()
        print 'running 5-fold CV...'
        for i in range(5):
            print 'case ' + str(i)
            feature_train, feature_test, label_train, label_test = cross_validation.train_test_split(features, classes, test_size=0.2, random_state=0)

            if trainMode == 'MaxEnt':
                # this requires scikit-learn 0.18
                # model = MLPClassifier(algorithm='sgd', activation='logistic', learning_rate_init=0.02, learning_rate='constant', batch_size=10)
                model = LogisticRegression()
            elif trainMode == 'RF':
                model = ExtraTreesClassifier(n_estimators=50, random_state=0)
            elif trainMode == 'Ada':
                model = AdaBoostClassifier()
            else:
                model = svm.SVC()

            model.fit(feature_train, label_train)
            predictions = model.predict(feature_test)

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
            accuracy = model.score(feature_test, label_test)

            auc = roc_auc_score(label_test, predictions)
            aucSum += auc
            # print confusion_matrix(label_test, predictions)

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
        print aucSum / 5
        print ''
        resultFile.write(str(outputPrecision) + '\n')
        resultFile.write(str(outputRecall) + '\n')
        resultFile.write(str(outputAccuracy) + '\n')
        resultFile.write(str(outputF1) + '\n')
        resultFile.write('\n')
        resultFile.flush()

    resultFile.close()


if __name__ == "__main__":
    # vectorMode 1: tfidf, 2: binaryCount, 3:LDA dist
    # featureMode 0: content only, 1: ngram only, 2: embedding only, 3: embedding and semantic, 4: content and ngram
    outputFilename = 'results/temp.result'

    runModel(1, 'totalGroup', 0, 0, 'MLP', outputFile=outputFilename)
    runModel(1, 'totalGroup', 2, 1, 'MLP', outputFile=outputFilename)
    runModel(1, 'totalGroup', 0, 0, 'RF', outputFile=outputFilename)
    runModel(1, 'totalGroup', 0, 0, 'SVM', outputFile=outputFilename)
    runModel(1, 'totalGroup', 2, 4, 'SVM', outputFile=outputFilename)

    '''
    #run(3, 'brandGroup', 0, 0, 'SVM', outputFile=outputFilename)
    #run(3, 'subBrandGroup', 0, 0, 'SVM',outputFile=outputFilename)
    #run(5, 'topicGroup', 0, 0, 'SVM', outputFile=outputFilename)
    #run(5, 'simGroup', 0, 0, 'SVM', outputFile=outputFilename)
    #run(1, 'totalGroup', 0, 0, 'RF', outputFile=outputFilename)

    #run(3, 'brandGroup', 2, 1, outputFile=outputFilename)
    #run(3, 'subBrandGroup', 2, 1, outputFile=outputFilename)
    #run(5, 'topicGroup', 2, 1, outputFile=outputFilename)
    #run(5, 'simGroup', 2, 1, outputFile=outputFilename)
    run(1, 'totalGroup', 2, 1, outputFile=outputFilename)

    run(3, 'brandGroup', 2, 4, outputFile=outputFilename)
    run(3, 'subBrandGroup', 2, 4, outputFile=outputFilename)
    run(5, 'topicGroup', 2, 4, outputFile=outputFilename)
    run(5, 'simGroup', 2, 4, outputFile=outputFilename)
    run(1, 'totalGroup', 2, 4, outputFile=outputFilename)
    '''