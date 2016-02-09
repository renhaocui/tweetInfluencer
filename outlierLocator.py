__author__ = 'renhao.cui'
from scipy import stats
import json
import statistics as stat
import tweetTextCleaner

def outlierExtractor():
    print 'extracting outliers...'
    brandList = []
    listFile = open('brand.list', 'r')
    for line in listFile:
        brandList.append(line.strip())
    listFile.close()

    #combinedOutFile = open('adData/ConsolidatedTweets/total.json', 'r')
    totalOutputFile = open('adData/analysis/clean/total.clean', 'w')
    totalOutLierFile = open('adData/analysis/outliers/total.outliers', 'w')
    totalDistFile = open('adData/analysis/original/total.dist', 'w')
    outputDistFile = open('adData/analysis/clean/total.cleandist', 'w')
    totalRankedFile1 = open('adData/analysis/ranked/1/total.pos', 'w')
    totalRankedFile2 = open('adData/analysis/ranked/2/total.neg', 'w')
    statFile = open('adData/analysis/stat.total', 'w')
    exceptionFile = open('adData/analysis/exceptions.list', 'r')
    expFile = open('adData/analysis/exception.list', 'w')
    totalCleanScore = []
    totalCleanData = []
    out = ''
    outClean = ''

    exceptionList = set()
    for line in exceptionFile:
        exceptionList.add(long(line.strip()))
    exceptionFile.close()

    mentionList = set([])
    hashtagList = set([])
    for brand in brandList:
        print brand
        input = open('adData/ConsolidatedTweets/'+brand+'.json', 'r')
        outputFile = open('adData/analysis/clean/'+brand+'.clean', 'w')
        outLierFile = open('adData/analysis/outliers/'+brand+'.outliers', 'w')
        #rankedFile1 = open('adData/analysis/ranked/1/'+brand+'.pos', 'w')
        #rankedFile2 = open('adData/analysis/ranked/2/'+brand+'.neg', 'w')
        brandData = []
        brandScoreList = []

        for line in input:
            data = json.loads(line.strip())
            id = long(data['id'])
            if id not in exceptionList:
                text = data['text'].encode('utf-8').lower()
                content = tweetTextCleaner.tweetCleaner(text)
                finalIndex = len(data['dynamic'])-1
                followers = float(data['dynamic'][finalIndex]['user_followers_count'])
                retweet = float(data['dynamic'][finalIndex]['retweet_count'])
                favorite = float(data['dynamic'][finalIndex]['favorite_count'])
                if retweet == 0:
                    ratio = 0
                else:
                    ratio = favorite/retweet
                statFile.write(str(favorite)+'\t'+str(retweet)+'\t'+str(followers)+'\t'+str(ratio)+'\n')
                day = data['create_at'].split()[0]
                hour = data['create_at'].split()[3].split(':')[0]
                labelScore = (2.0*retweet + favorite)*10000/followers
                mentions = data['mentions']
                hashtags = data['hashtags']
                brandData.append((content, labelScore, id, day, hour, mentions, hashtags))
                brandScoreList.append(labelScore)
            else:
                text = data['text'].encode('utf-8')
                expFile.write(str(id)+'\t'+text+'\n')
        input.close()

        zScores = stats.zscore(brandScoreList)
        if len(zScores) != len(brandData):
            print 'z score error!'

        maxScore = max(brandScoreList)
        minScore = min(brandScoreList)
        for score in brandScoreList:
            out += str((score - minScore)/(maxScore - minScore)) + '\t'

        outputData = []
        for index, item in enumerate(brandData):
            content = item[0]
            score = item[1]
            id = item[2]
            day = item[3]
            hour = item[4]
            mentions = item[5]
            hashtags = item[6]
            outputData.append((float(score), float(zScores[index]), id, content, day, hour, mentions, hashtags))

        cleanData = []
        cleanScore = []
        sorted_output = sorted(outputData, key=lambda x: x[0])
        for (score, z, id, content, day, hour, mentions, hashtags) in reversed(sorted_output):
            if z > 2:
                outLierFile.write(str(score)+' : '+str(z)+' : '+' : '+str(id)+' : '+content+'\n')
                totalOutLierFile.write(str(score)+' : '+str(z)+' : '+' : '+str(id)+' : '+content+'\n')
            else:
                cleanData.append((score, z, content, day, hour, id, mentions, hashtags))
                cleanScore.append(score)
                totalCleanScore.append(score)
                totalCleanData.append((score, z, content, day, hour))
                outputFile.write(str(score)+' : '+str(z)+' : '+' : '+str(id)+' : '+content+'\n')
                totalOutputFile.write(str(score)+' : '+str(z)+' : '+' : '+str(id)+' : '+content+'\n')

        cleanSize = len(cleanScore)
        firstIndicator = True
        for count, (score, z, content, day, hour, id, mentions, hashtags) in enumerate(cleanData):
            if count <= 0.3*cleanSize:
                #rankedFile1.write(str(score)+' : '+day+' : '+hour+' : '+unicode(content, errors='ignore')+'\n')
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
                totalRankedFile1.write(str(score)+' :: '+day+' :: '+hour+' :: '+unicode(content, errors='ignore')+' :: '+brand+' :: '+str(id)+' :: '+hashtagOutput+' :: '+mentionsOutput+'\n')
            else:
                if firstIndicator:
                    firstIndicator = False
                #rankedFile2.write(str(score)+' : '+day+' : '+hour+' : '+unicode(content, errors='ignore')+'\n')
                totalRankedFile2.write(str(score)+' :: '+day+' :: '+hour+' :: '+unicode(content, errors='ignore')+' :: '+brand+' :: '+str(id)+' :: '+hashtagOutput+' :: '+mentionsOutput+'\n')

        maxScore = max(cleanScore)
        minScore = min(cleanScore)

        normalScores = []
        for score in cleanScore:
            outClean += str((score - minScore)/(maxScore - minScore)) + '\t'
            normalScores.append((score - minScore)/(maxScore - minScore))
        print 'mean: '+str(stat.mean(normalScores))
        print 'stdev: '+str(stat.stdev(normalScores))
        print 'mdean: '+str(stat.median(normalScores))
        if stat.stdev(normalScores) >= stat.mean(normalScores):
            print 'TRUE'
        else:
            print 'FALSE'
        print ''
        outLierFile.close()
        outputFile.close()
        #rankedFile1.close()
        #rankedFile2.close()

    hashtagFile = open('adData/analysis/ranked/hashtag.list', 'w')
    mentionFile = open('adData/analysis/ranked/mention.list', 'w')
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
    outputDistFile.close()
    statFile.close()
    expFile.close()

outlierExtractor()