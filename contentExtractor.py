import re

__author__ = 'renhao.cui'
import json
import statistics as stat
from tokenizer import simpleTokenize

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

brandList = ['amazon', 'dominos', 'Gap', 'Jeep', 'AppStore', 'Chilis', 'Motorola', 'AmericanExpress',
             'Microsoft', 'total']
keyword = 'follow'
limit = 3
for brand in brandList:
    print brand
    input = open('adData\\'+brand+'.tweet', 'r')
    output = open('adData\\'+brand+'.content', 'w')
    high = open('adData\\'+brand+'high.content', 'w')
    low = open('adData\\'+brand+'low.content', 'w')
    highContent = []
    lowContent = []
    highLength = []
    lowLength = []
    tempHigh = 0.0
    tempLow = 0.0
    highURL = 0.0
    highHT = 0.0
    lowURL = 0.0
    lowHT = 0.0
    highDollar = 0.0
    lowDollar = 0.0
    for line in input:
        data = json.loads(line.strip())
        content = normalizeText(data['text'].encode('utf-8')).lower()
        finalIndex = len(data['dynamic'])-1
        totalFavorite = float(data['dynamic'][finalIndex]['user_favorite_count'])
        followers = float(data['dynamic'][finalIndex]['user_followers_count'])
        listed = float(data['dynamic'][finalIndex]['user_listed_count'])
        friends = float(data['dynamic'][finalIndex]['user_friends_count'])
        totalTweet = float(data['dynamic'][finalIndex]['user_statuses_count'])
        retweet = float(data['dynamic'][finalIndex]['retweet_count'])
        favorite = float(data['dynamic'][finalIndex]['favorite_count'])
        label = (2*retweet + favorite)*10000/followers
        output.write(str(label)+': '+content+'\n')
        if label >= limit:
            highContent.append((label, content))
            if '<URL>' in content:
                highURL += 1.0
            if '#' in content:
                highHT += 1.0
            if '$' in content:
                highDollar += 1.0
            if (keyword in content):
                tempHigh += 1.0
            highLength.append(len(simpleTokenize(content)))
            high.write(str(label)+': '+content+'\n')
        else:
            low.write(str(label)+': '+content+'\n')
            if '<URL>' in content:
                lowURL += 1.0
            if '#' in content:
                lowHT += 1.0
            if '$' in content:
                lowDollar += 1.0
            if (keyword in content):
                tempLow += 1.0
            lowContent.append((label, content))
            lowLength.append(len(simpleTokenize(content)))

    print 'high: '
    print len(highLength)
    #print highDollar/len(highLength)
    #print tempHigh*100/len(highLength)
    #print highURL/len(highLength)
    #print highHT/len(highLength)
    #print stat.mean(highLength)
    #print stat.median(highLength)
    #print stat.stdev(highLength)

    print 'low: '
    print len(lowLength)
    #print lowDollar/len(lowLength)
    #print tempLow*100/len(lowLength)
    #print lowURL/len(lowLength)
    #print lowHT/len(lowLength)
    #print stat.mean(lowLength)
    #print stat.median(lowLength)
    #print stat.stdev(lowLength)

    print '\n'
    high.close()
    low.close()
    input.close()
    output.close()