__author__ = 'renhao.cui'
from scipy import stats
import json
from datetime import datetime
import tweetTextCleaner
import sys

reload(sys)
sys.setdefaultencoding('utf8')
filterTerms = ['iphone 7', 'pikachu', 'pokemon go']

def outlierExtractor():
    print 'extracting outliers...'
    brandList = []
    listFile = open('brand.list', 'r')
    for line in listFile:
        brandList.append(line.strip())
    listFile.close()

    totalOutputFile = open('dataset/experiment/total.data', 'w')
    totalOutLierFile = open('dataset/exceptions/total.outliers', 'w')
    totalDistFile = open('dataset/original/total.dist', 'w')
    outputDistFile = open('dataset/experiment/total.cleandist', 'w')
    totalPosFile = open('dataset/experiment/ranked/total.pos', 'w')
    totalNegFile = open('dataset/experiment/ranked/total.neg', 'w')
    statFile = open('dataset/analysis/stat.total', 'w')
    exceptionFile = open('dataset/exceptions/exceptions.list', 'r')
    expFile = open('dataset/exceptions/exception.list', 'w')
    totalCleanScore = []
    totalCleanData = []
    out = ''
    outClean = ''

    exceptionList = set()
    for line in exceptionFile:
        exceptionList.add(long(line.strip()))
    exceptionFile.close()

    mentionList = set()
    hashtagList = set()

    totalBrandData = {}
    inputFile = open('dataset/ConsolidatedTweets/total.json', 'r')
    for line in inputFile:
        temp = json.loads(line.strip())
        brand = temp['brand']
        if brand not in totalBrandData:
            totalBrandData[brand] = [temp]
        else:
            totalBrandData[brand].append(temp)
    inputFile.close()

    for brand in brandList:
        print brand
        outputFile = open('dataset/brands/'+brand+'.data', 'w')
        outLierFile = open('dataset/exceptions/'+brand+'.outliers', 'w')
        brandData = []
        brandScoreList = []

        for data in totalBrandData[brand]:
            tweetID = long(data['id'])
            if tweetID not in exceptionList:
                finalIndex = len(data['dynamic']) - 1
                text = data['text'].encode('utf-8').lower()
                followers = float(data['dynamic'][finalIndex]['user_followers_count'])
                filtered = False
                for term in filterTerms:
                    if term in text.lower():
                        filtered = True
                        break
                if (not filtered) and (followers > 0):
                    content = tweetTextCleaner.tweetCleaner(text)
                    #finalIndex = 0
                    retweet = float(data['dynamic'][finalIndex]['retweet_count'])
                    favorite = float(data['dynamic'][finalIndex]['favorite_count'])
                    author_statuses_count = float(data['dynamic'][finalIndex]['user_statuses_count'])
                    author_favorite_count = float(data['dynamic'][finalIndex]['user_favorite_count'])
                    author_listed_count = float(data['dynamic'][finalIndex]['user_listed_count'])
                    if retweet == 0:
                        ratio = 0
                    else:
                        ratio = favorite/retweet
                    statFile.write(str(favorite)+'\t'+str(retweet)+'\t'+str(followers)+'\t'+str(ratio)+'\n')

                    dateTemp = data['create_at'].split()
                    day = dateTemp[0]
                    hour = dateTemp[3].split(':')[0]
                    postDate = dateTemp[1]+' '+dateTemp[2]+' '+dateTemp[5]
                    dateTemp = data['user_create_at'].split()
                    authorDate = dateTemp[1]+' '+dateTemp[2]+' '+dateTemp[5]
                    postData_object = datetime.strptime(postDate, '%b %d %Y')
                    authorData_object = datetime.strptime(authorDate, '%b %d %Y')
                    authorInterval = float((postData_object-authorData_object).days)

                    labelScore = (2.0*retweet + favorite)*10000/followers
                    brandData.append((content, labelScore, tweetID, day, hour, data['mentions'], data['hashtags'], author_statuses_count, author_favorite_count, author_listed_count, authorInterval))
                    brandScoreList.append(labelScore)
                else:
                    text = data['text'].encode('utf-8').replace('\r', ' ').replace('\n', ' ')
                    expFile.write(str(tweetID)+'\t'+text+'\n')

        zScores = stats.zscore(brandScoreList)
        if len(zScores) != len(brandData):
            print 'Z-score Error!'
        # maxScore = max(brandScoreList)
        # minScore = min(brandScoreList)
        '''
        for score in brandScoreList:
            out += str((score - minScore)/(maxScore - minScore)) + '\t'
        '''
        outputData = []
        for index, item in enumerate(brandData):
            outputData.append((float(item[1]), float(zScores[index]), item[2], item[0], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10]))

        cleanData = []
        cleanScore = []
        sorted_output = sorted(outputData, key=lambda x: x[0])
        for (score, z, tweetID, content, day, hour, mentions, hashtags, statusCount, favoriteCount, listedCount, authorInterval) in reversed(sorted_output):
            if z > 2:
                outLierFile.write(str(score)+' : '+str(z)+' : '+' : '+str(tweetID)+' : '+content+'\n')
                totalOutLierFile.write(str(score)+' : '+str(z)+' : '+' : '+str(tweetID)+' : '+content+'\n')
            else:
                cleanData.append((score, z, content, day, hour, tweetID, mentions, hashtags, statusCount, favoriteCount, listedCount, authorInterval))
                cleanScore.append(score)
                totalCleanScore.append(score)
                totalCleanData.append((score, z, content, day, hour, statusCount, favoriteCount, listedCount, authorInterval))
                outputFile.write(str(score)+' : '+str(z)+' : '+' : '+str(tweetID)+' : '+content+'\n')
                totalOutputFile.write(str(score)+' : '+str(z)+' : '+' : '+str(tweetID)+' : '+content+'\n')

        # label assignment: 30/70 split
        cleanSize = len(cleanScore)
        for count, (score, z, content, day, hour, tweetID, mentions, hashtags, statusCount, favoriteCount, listedCount, authorInterval) in enumerate(cleanData):
            hashtagOutput = ''
            mentionsOutput = ''
            for ht in hashtags:
                if ht not in hashtagList:
                    hashtagList.add(ht)
                hashtagOutput += ht + ';'
            if hashtagOutput == '':
                hashtagOutput = 'NONE'
            else:
                hashtagOutput = hashtagOutput[:-1]
            for ment in mentions:
                if ment not in mentionList:
                    mentionList.add(ment)
                mentionsOutput += ment + ';'
            if mentionsOutput == '':
                mentionsOutput = 'NONE'
            else:
                mentionsOutput = mentionsOutput[:-1]
            if count <= 0.5 * cleanSize:
                #rankedFile1.write(str(score)+' : '+day+' : '+hour+' : '+unicode(content, errors='ignore')+'\n')
                try:
                    totalPosFile.write(str(score)+' :: '+day+' :: '+hour+' :: '+unicode(content, errors='ignore')+' :: '+brand+' :: '+str(tweetID)+' :: '+hashtagOutput+' :: '+mentionsOutput+' :: '+str(statusCount)+' :: '+str(favoriteCount)+' :: '+str(listedCount)+' :: '+str(authorInterval)+'\n')
                except:
                    print content
            else:
                #rankedFile2.write(str(score)+' : '+day+' : '+hour+' : '+unicode(content, errors='ignore')+'\n')
                try:
                    totalNegFile.write(str(score)+' :: '+day+' :: '+hour+' :: '+unicode(content, errors='ignore')+' :: '+brand+' :: '+str(tweetID)+' :: '+hashtagOutput+' :: '+mentionsOutput+' :: '+str(statusCount)+' :: '+str(favoriteCount)+' :: '+str(listedCount)+' :: '+str(authorInterval)+'\n')
                except:
                    print content
        '''
        maxScore = max(cleanScore)
        minScore = min(cleanScore)

        normalScores = []
        for score in cleanScore:
            #outClean += str((score - minScore)/(maxScore - minScore)) + '\t'
            normalScores.append((score - minScore)/(maxScore - minScore))
        stdevScore = stat.stdev(normalScores)
        meanScore = stat.mean(normalScores)
        print 'mean: '+str(meanScore)
        print 'stdev: '+str(stdevScore)
        print 'mdean: '+str(stat.median(normalScores))
        if stdevScore >= meanScore:
            print 'TRUE'
        else:
            print 'FALSE'
        print ''
        '''
        outLierFile.close()
        outputFile.close()

    hashtagFile = open('dataset/experiment/hashtag.list', 'w')
    mentionFile = open('dataset/experiment/mention.list', 'w')
    for ht in hashtagList:
        hashtagFile.write(ht+'\n')
    for ment in mentionList:
        mentionFile.write(ment+'\n')

    hashtagFile.close()
    mentionFile.close()
    outputDistFile.write(outClean.strip())
    totalDistFile.write(out.strip())
    totalDistFile.close()
    totalOutLierFile.close()
    totalOutputFile.close()
    totalPosFile.close()
    totalNegFile.close()
    outputDistFile.close()
    statFile.close()
    expFile.close()


if __name__ == "__main__":
    outlierExtractor()