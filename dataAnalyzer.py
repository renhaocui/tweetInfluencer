import re
import numpy
import utilities

__author__ = 'renhao.cui'
import json
from tokenizer import simpleTokenize
import statistics as stat
from textstat.textstat import textstat

def shrinkPuncuation(input):
    input = re.sub('\.+', '.', input)
    input = re.sub(',+', ',', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('=+', '=', input)
    input = re.sub('-+', '-', input)
    input = re.sub('_+', '_', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('@+', '@', input)
    input = re.sub('&+', '&', input)
    input = re.sub('#+', '#', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('\*+', '*', input)
    return input


def removeUsername(input):
    users = re.findall(r'@(\w+)', input)
    if len(users) != 0:
        for user in users:
            input = input.replace(user, '<USERNAME>')
            input = input.replace('@: ', '')
    return input


def tokenizeLinks(input):
    urls = re.findall("(?P<url>https?://[^\s]+)", input)
    if len(urls) != 0:
        for url in urls:
            input = input.replace(url, ' <URL> ')
    return input


def normalizeText(input):
    input = input.replace('\r', '')
    input = input.replace('\n', '')
    input = tokenizeLinks(input)
    input = shrinkPuncuation(input)
    return input

brandList = []
listFile = open('brand.list', 'r')
for line in listFile:
    brandList.append(line.strip())
listFile.close()

combinedOutFile = open('adData//ConsolidatedTweets2//total.json', 'r')
limit = 0.07
keywords = ['free', 'promotion', 'deal']
#scoreOutput = open('adData\\analysis2\\total.score', 'w')
#totalScore = ''
totalBrandData = []
for brand in brandList:
    print brand
    input = open('adData\\ConsolidatedTweets2\\'+brand+'.json', 'r')
    output = open('adData\\analysis2\\'+brand+'.content', 'w')

    high = open('adData\\analysis2\\'+brand+'high.content', 'w')
    low = open('adData\\analysis2\\'+brand+'low.content', 'w')
    brandData = []
    highContent = []
    lowContent = []
    highLength = []
    lowLength = []

    highCount = 0.0
    highURLCount = 0.0
    highHTCount = 0.0
    highDollarCount = 0.0
    highURL = 0.0
    highHT = 0.0
    highDollar = 0.0

    lowCount = 0.0
    lowURLCount = 0.0
    lowHTCount = 0.0
    lowDollarCount = 0.0
    lowURL = 0.0
    lowHT = 0.0
    lowDollar = 0.0

    brandScoreList = []
    for line in input:
        data = json.loads(line.strip())
        content = normalizeText(data['text'].encode('utf-8')).lower()
        finalIndex = len(data['dynamic'])-1
        #totalFavorite = float(data['dynamic'][finalIndex]['user_favorite_count'])
        followers = float(data['dynamic'][finalIndex]['user_followers_count'])
        #listed = float(data['dynamic'][finalIndex]['user_listed_count'])
        #friends = float(data['dynamic'][finalIndex]['user_friends_count'])
        #totalTweet = float(data['dynamic'][finalIndex]['user_statuses_count'])
        retweet = float(data['dynamic'][finalIndex]['retweet_count'])
        favorite = float(data['dynamic'][finalIndex]['favorite_count'])
        labelScore = (2.0*retweet + favorite)*10000/followers
        brandData.append((content, labelScore))
        brandScoreList.append(labelScore)
    input.close()
    maxScore = max(brandScoreList)
    minScore = min(brandScoreList)

    for item in brandData:
        score = (item[1]-minScore)/(maxScore - minScore)
        content = item[0]
        output.write(str(score)+': '+content+'\n')
        #totalScore += str(score)+'\t'
        #scoreOutput.write(str(score)+'\t')
        totalBrandData.append((content, score))
    '''
        if score >= limit:
            highCount += 1
            highContent.append((score, content))
            if '<URL>' in content:
                highURLCount += content.count('<url>')
                highURL += 1.0
            if '#' in content:
                highHTCount += content.count('#')
                highHT += 1.0
            if '$' in content:
                highDollarCount += content.count('$')
                highDollar += 1.0
            #if (keyword in content):
             #   tempHigh += 1.0
            highLength.append(len(simpleTokenize(content)))
            high.write(str(score)+': '+content+'\n')
        else:
            lowCount += 1
            low.write(str(score)+': '+content+'\n')
            if '<URL>' in content:
                lowURLCount += content.count('<url>')
                lowURL += 1.0
            if '#' in content:
                lowHTCount += content.count('#')
                lowHT += 1.0
            if '$' in content:
                lowDollarCount += content.count('$')
                lowDollar += 1.0
            #if (keyword in content):
              #  tempLow += 1.0
            lowContent.append((score, content))
            lowLength.append(len(simpleTokenize(content)))
    #scoreOutput.write('\n')

    try:
        print 'high: '
        print highCount
        print 'percentage dollar: '+str(highDollar/highCount)
        print 'percentage URL: '+str(highURL/highCount)
        print 'percentage HT: '+str(highHT/highCount)
        print 'average dollar: '+str(highDollarCount/highCount)
        print 'average URL: '+str(highURLCount/highCount)
        print 'average HT: '+str(highHTCount/highCount)
        print 'length mean: '+str(stat.mean(highLength))
        print 'length median: '+str(stat.median(highLength))
        print 'length std: '+str(stat.stdev(highLength))

        print 'low: '
        print lowCount
        print 'percentage dollar: '+str(lowDollar/lowCount)
        print 'percentage URL: '+str(lowURL/lowCount)
        print 'percentage HT: '+str(lowHT/lowCount)
        print 'average dollar: '+str(lowDollarCount/lowCount)
        print 'average URL: '+str(lowURLCount/lowCount)
        print 'average HT: '+str(lowHTCount/lowCount)
        print 'length mean: '+str(stat.mean(lowLength))
        print 'length median: '+str(stat.median(lowLength))
        print 'length std: '+str(stat.stdev(lowLength))
    except Exception as e:
        continue

    print '\n'
    '''
    high.close()
    low.close()
    output.close()


highContent = []
lowContent = []
highLength = []
lowLength = []
highReadability = []
lowReadability = []

highSentiCount = 0.0
highCount = 0.0
highURLCount = 0.0
highHTCount = 0.0
highDollarCount = 0.0
highURL = 0.0
highHT = 0.0
highDollar = 0.0
highKeyword = 0.0

lowSentiCount = 0.0
lowCount = 0.0
lowURLCount = 0.0
lowHTCount = 0.0
lowDollarCount = 0.0
lowURL = 0.0
lowHT = 0.0
lowDollar = 0.0
lowKeyword = 0.0

happy_log_probs, sad_log_probs = utilities.readSentimentList('twitter_sentiment_list.csv')
output = open('adData\\analysis2\\total.content', 'w')
high = open('adData\\analysis2\\totalhigh.content', 'w')
low = open('adData\\analysis2\\totallow.content', 'w')
classFlag = []
URLFlag = []
HTFlag = []
DollarFlag = []
lengthFlag = []
keywordFlag = []
sentiFlag = []
readabilityScore = []
for item in totalBrandData:
    score = item[1]
    content = item[0]
    output.write(str(score)+': '+content+'\n')
    if '<url>' in content:
        URLFlag.append(1)
    else:
        URLFlag.append(0)
    if '#' in content:
        HTFlag.append(1)
    else:
        HTFlag.append(0)
    if '$' in content:
        DollarFlag.append(1)
    else:
        DollarFlag.append(0)
    temp = 0
    for word in keywords:
        if word in content:
            temp = 1
            break
    readScore = textstat.coleman_liau_index(content)
    readabilityScore.append(readScore)
    keywordFlag.append(temp)
    lengthFlag.append(len(simpleTokenize(content)))
    posProb, negProb = utilities.classifySentiment(simpleTokenize(content), happy_log_probs, sad_log_probs)
    if posProb >= 0.5:
        senti = 1
    else:
        print 111111111
        senti = 0
    sentiFlag.append(senti)

    if score >= limit:
        classFlag.append(1)
        highCount += 1
        highContent.append((score, content))
        if '<url>' in content:
            highURLCount += content.count('<url>')
            highURL += 1.0
        if '#' in content:
            highHTCount += content.count('#')
            highHT += 1.0
        if '$' in content:
            highDollarCount += content.count('$')
            highDollar += 1.0
        for word in keywords:
            if word in content:
                highKeyword += 1.0
                break
        if senti == 1:
            highSentiCount += 1.0
        #if (keyword in content):
         #   tempHigh += 1.0
        highReadability.append(readScore)
        highLength.append(len(simpleTokenize(content)))
        high.write(str(score)+': '+content+'\n')
    else:
        classFlag.append(0)
        lowCount += 1
        low.write(str(score)+': '+content+'\n')
        if '<url>' in content:
            lowURLCount += content.count('<url>')
            lowURL += 1.0
        if '#' in content:
            lowHTCount += content.count('#')
            lowHT += 1.0
        if '$' in content:
            lowDollarCount += content.count('$')
            lowDollar += 1.0
        for word in keywords:
            if word in content:
                lowKeyword += 1.0
                break
        if senti == 1:
            lowSentiCount += 1.0
        #if (keyword in content):
          #  tempLow += 1.0
        lowReadability.append(readScore)
        lowContent.append((score, content))
        lowLength.append(len(simpleTokenize(content)))

print 'total'
print 'high: '
print highCount
#print 'percentage dollar: '+str(highDollar/highCount)
#print 'percentage URL: '+str(highURL/highCount)
#print 'percentage HT: '+str(highHT/highCount)
#print 'average dollar: '+str(highDollarCount/highCount)
#print 'average URL: '+str(highURLCount/highCount)
#print 'average HT: '+str(highHTCount/highCount)
#print 'length mean: '+str(stat.mean(highLength))
#print 'length median: '+str(stat.median(highLength))
#print 'length std: '+str(stat.stdev(highLength))
print 'keyword: '+str(highKeyword/highCount)
#print 'read mean: '+str(stat.mean(highReadability))
#print 'read median: '+str(stat.median(highReadability))
#print 'read std: '+str(stat.stdev(highReadability))
print 'percentage senti: '+str(highSentiCount/highCount)


print 'low: '
print lowCount
#print 'percentage dollar: '+str(lowDollar/lowCount)
#print 'percentage URL: '+str(lowURL/lowCount)
#print 'percentage HT: '+str(lowHT/lowCount)
#print 'average dollar: '+str(lowDollarCount/lowCount)
#print 'average URL: '+str(lowURLCount/lowCount)
#print 'average HT: '+str(lowHTCount/lowCount)
#print 'length mean: '+str(stat.mean(lowLength))
#print 'length median: '+str(stat.median(lowLength))
#print 'length std: '+str(stat.stdev(lowLength))
print 'keyword: '+str(lowKeyword/lowCount)
#print 'read mean: '+str(stat.mean(lowReadability))
#print 'read median: '+str(stat.median(lowReadability))
#print 'read std: '+str(stat.stdev(lowReadability))
print 'percentage senti: '+str(lowSentiCount/lowCount)

#print 'URL coe: '+str(numpy.corrcoef(URLFlag, classFlag)[0, 1])
#print 'HT coe: '+str(numpy.corrcoef(HTFlag, classFlag)[0, 1])
#print 'Dollar coe: '+str(numpy.corrcoef(DollarFlag, classFlag)[0, 1])
#print 'Length coe: '+str(numpy.corrcoef(lengthFlag, classFlag)[0, 1])
print 'keyword coe: '+str(numpy.corrcoef(keywordFlag, classFlag)[0, 1])
#print 'readability coe: '+str(numpy.corrcoef(readabilityScore, classFlag)[0, 1])
print 'senti coe: '+str(numpy.corrcoef(sentiFlag, classFlag)[0, 1])
'''
URLoutputFile = open('url.points', 'w')
URLoutputFile.write(str(URLFlag)[1:-1]+'\n'+str(classFlag)[1:-1])
URLoutputFile.close()
'''
#scoreOutput.write(totalScore.strip())
#scoreOutput.close()
