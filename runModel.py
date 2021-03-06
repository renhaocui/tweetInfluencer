__author__ = 'rencui'
from afinn import Afinn
import subprocess
import numpy
import utilities
from textstat.textstat import textstat
from sklearn.feature_extraction.text import *
from nltk.stem.porter import *
from sklearn.model_selection import train_test_split
from tokenizer import simpleTokenize
from scipy.sparse import hstack, csr_matrix
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
import sklearn.metrics
from sklearn.ensemble import AdaBoostClassifier
from sklearn.naive_bayes import MultinomialNB
import sys
from sklearn.model_selection import KFold

reload(sys)
sys.setdefaultencoding('utf-8')

dayMapper = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}

stemmer = PorterStemmer()


def stemContent(input):
    words = simpleTokenize(input)
    out = ''
    for word in words:
        temp = stemmer.stem(word.encode('utf-8').decode('utf-8'))
        out += temp + ' '
    return out.strip()


# vectorMode 1: tfidf, 2: binaryCount
# featureMode 0: semantic only, 1: vector only, 2: both
def runModel(groupSize, groupTitle, vectorMode, featureMode, trainMode, ablationIndex):
    outputFile = 'results/'+groupTitle+'_'+trainMode+'.result'
    resultFile = open(outputFile, 'a')
    mentionMapper = utilities.mapMention('dataset/experiment/mention.json')

    print groupTitle
    print trainMode
    resultFile.write(groupTitle + '\n')
    for group in range(groupSize):
        print 'group: ' + str(group)
        resultFile.write('group: ' + str(group) + '\n')
        # happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
        afinn = Afinn()
        posFile = open('dataset/experiment/groups/' + groupTitle + '/group_' + str(group) + '.pos', 'r')
        negFile = open('dataset/experiment/groups/' + groupTitle + '/group_' + str(group) + '.neg', 'r')
        posParseLengthFile = open('dataset/experiment/groups/' + groupTitle + '/parserLength_' + str(group) + '.pos', 'r')
        negParseLengthFile = open('dataset/experiment/groups/' + groupTitle + '/parserLength_' + str(group) + '.neg', 'r')
        posHeadCountFile = open('dataset/experiment/groups/' + groupTitle + '/parserHeadCount_' + str(group) + '.pos', 'r')
        negHeadCountFile = open('dataset/experiment/groups/' + groupTitle + '/parserHeadCount_' + str(group) + '.neg', 'r')
        posPOSCountFile = open('dataset/experiment/groups/' + groupTitle + '/parserPOSCount_' + str(group) + '.pos', 'r')
        negPOSCountFile = open('dataset/experiment/groups/' + groupTitle + '/parserPOSCount_' + str(group) + '.neg', 'r')

        ids = []
        contents = []
        scores = []
        days = []
        time = []
        authorStatusCount = []
        authorFavoriteCount = []
        authorListedCount = []
        authorIntervals = []
        labels = []
        parseLength = []
        headCount = []
        usernames = []
        additionalFeatures = []
        classes = []
        POScounts = []
        followers = []

        print 'loading data...'
        for line in posFile:
            seg = line.strip().split(' :: ')
            text = seg[3]
            username = seg[7].split(';')
            time.append(utilities.hourMapper(int(seg[2])))
            day = seg[1]
            score = float(seg[0])
            ids.append(seg[5])
            authorStatusCount.append(float(seg[8]))
            authorFavoriteCount.append(float(seg[9]))
            authorListedCount.append(float(seg[10]))
            authorIntervals.append(float(seg[11]))
            usernames.append(username)
            followers.append(float(seg[12]))
            days.append(dayMapper[day])
            contents.append(text)
            scores.append(score)
            labels.append(1)

        for line in negFile:
            seg = line.strip().split(' :: ')
            text = seg[3]
            username = seg[7].split(';')
            time.append(utilities.hourMapper(int(seg[2])))
            day = seg[1]
            score = float(seg[0])
            ids.append(seg[5])
            authorStatusCount.append(float(seg[8]))
            authorFavoriteCount.append(float(seg[9]))
            authorListedCount.append(float(seg[10]))
            authorIntervals.append(float(seg[11]))
            usernames.append(username)
            followers.append(float(seg[12]))
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
            sentiScore = afinn.score(content)
            # posProb, negProb = utilities.classifySentiment(words, happy_log_probs, sad_log_probs)
            readScore = textstat.coleman_liau_index(content)

            if ablationIndex != 0:
                temp.append(sentiScore / twLen)
            if ablationIndex != 1:
                temp.append(twLen)
                temp.append(readScore)
                temp.append(parseLength[index] / twLen)
                temp.append(headCount[index] / twLen)
            if ablationIndex != 2:
                temp.append(authorStatusCount[index]/authorIntervals[index])
                temp.append(authorFavoriteCount[index]/authorStatusCount[index])
                temp.append(authorListedCount[index]/followers[index])
            if ablationIndex != 3:
                temp.append(days[index])
                temp.append(time[index])
            if ablationIndex != 4:
                if any(char.isdigit() for char in content):
                    temp.append(1)
                else:
                    temp.append(0)
            if ablationIndex != 5:
                temp += POScounts[index]
            if ablationIndex != 6:
                # temp.append(content.count('URRL'))
                if content.count('http://URL') > 0:
                    temp.append(1)
                else:
                    temp.append(0)
                # temp.append(content.count('HHTTG'))
                if content.count('#HTG') > 0:
                    temp.append(1)
                else:
                    temp.append(0)
                # temp.append(content.count('USSERNM'))
                if content.count('@URNM') > 0:
                    temp.append(1)
                else:
                    temp.append(0)
            if ablationIndex != 7:
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
            if ablationIndex != 8:
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

            additionalFeatures.append(numpy.array(temp))
            classes.append(labels[index])

        if featureMode == 0:
            resultFile.write('semantic features only \n')
            features = csr_matrix(numpy.array(additionalFeatures))
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
            features = hstack((csr_matrix(numpy.array(additionalFeatures)), csr_matrix(numpy.array(embedFeatures))), format='csr')
        else:
            resultFile.write('vector and semantic features \n')
            features = hstack((vectorMatrix, csr_matrix(numpy.array(additionalFeatures))), format='csr')
        resultFile.write('Ablation Index: '+str(ablationIndex)+'\n')
        precisionSum = 0.0
        recallSum = 0.0
        f1Sum = 0.0
        accuracySum = 0.0
        aucSum = 0.0
        resultFile.flush()
        print 'running 5-fold CV...'

        roundNum = 0
        kf = KFold(n_splits=5, shuffle=True)
        for train_indices, test_indices in kf.split(classes):
        #for i in range(5):
            #print 'case ' + str(i)
            print 'Round: ' + str(roundNum)
            #feature_train, feature_test, label_train, label_test = train_test_split(features, classes, test_size=0.2, random_state=0)
            feature_train, feature_test = features[train_indices], features[test_indices]
            label_train = []
            label_test = []
            for train_index in train_indices:
                label_train.append(classes[train_index])
            for test_index in test_indices:
                label_test.append(classes[test_index])
            roundNum += 1
            print label_test
            if trainMode == 'MaxEnt':
                model = LogisticRegression()
            elif trainMode == 'NaiveBayes':
                model = MultinomialNB()
            elif trainMode == 'RF':
                model = ExtraTreesClassifier(n_estimators=50, random_state=0)
            elif trainMode == 'Ada':
                model = AdaBoostClassifier()
            elif trainMode == 'MLP':
                model = MLPClassifier(activation='logistic', solver='sgd', learning_rate_init=0.02, learning_rate='constant', batch_size=100)
            else:
                model = svm.SVC()

            model.fit(feature_train, label_train)
            predictions = model.predict(feature_test)

            if len(predictions) != len(label_test):
                print 'inference error!'
                resultFile.write('inferece error!\n')

            accuracy = model.score(feature_test, label_test)
            precision = sklearn.metrics.precision_score(label_test, predictions)
            recall = sklearn.metrics.recall_score(label_test, predictions)
            f1 = sklearn.metrics.f1_score(label_test, predictions)
            auc = sklearn.metrics.roc_auc_score(label_test, predictions)
            aucSum += auc
            precisionSum += precision
            recallSum += recall
            f1Sum += f1
            accuracySum += accuracy
            resultFile.flush()
            # print confusion_matrix(label_test, predictions)

        outputPrecision = precisionSum / 5
        outputRecall = recallSum / 5
        outputAccuracy = accuracySum / 5
        outputF1 = f1Sum / 5
        outputAUC = aucSum / 5
        '''
        if (outputRecall + outputPrecision) == 0:
            outputF1 = 0.0
        else:
            outputF1 = 2 * outputRecall * outputPrecision / (outputRecall + outputPrecision)
        '''
        print outputPrecision
        print outputRecall
        print outputF1
        print outputAUC
        print outputAccuracy
        print ''
        resultFile.write(str(outputPrecision) + '\n')
        resultFile.write(str(outputRecall) + '\n')
        resultFile.write(str(outputF1) + '\n')
        resultFile.write(str(outputAUC) + '\n')
        resultFile.write(str(outputAccuracy) + '\n')
        resultFile.write('\n')
        resultFile.flush()

    resultFile.close()


if __name__ == "__main__":
    # vectorMode 1: tfidf, 2: binaryCount, 3:LDA dist
    # featureMode 0: content only, 1: ngram only, 2: embedding only, 3: embedding and semantic, 4: content and ngram
    runModel(1, 'totalGroup', 4, 0, 'SVM', 100)
    #runModel(1, 'totalGroup', 4, 4, 'SVM', 100)
    #for index in range(9):
        #runModel(1, 'totalGroup', 2, 0, 'SVM', index)
        #runModel(1, 'totalGroup', 2, 4, 'SVM', 100)