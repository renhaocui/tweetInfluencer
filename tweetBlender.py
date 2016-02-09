__author__ = 'rencui'
import json

def blend(fileSize, offset):
    print 'blending tweets...'
    brandList = []
    listFile = open('brand.list', 'r')
    for line in listFile:
        brandList.append(line.strip())
    listFile.close()

    combinedOutFile = open('adData/ConsolidatedTweets/total.json', 'w')
    totalIndex = 0
    for brand in brandList:
        tweetIDSet = set()
        tweetData = {}
        for index in range(fileSize):
            inputFile = open("C:/Users/renhao.cui/Desktop/ad data/" + brand + '/' + str(index+offset)+'.json', 'r')
            for line in inputFile:
                data = json.loads(line.strip())
                id = data['id']
                if id not in tweetIDSet:
                    totalIndex += 1
                    tweetIDSet.add(id)
                    temp = {}
                    temp['id'] = id
                    temp['text'] = data['text']
                    temp['create_at'] = data['created_at']
                    hashtags = []
                    if 'hashtags' in data['entities']:
                        for tag in data['entities']['hashtags']:
                            hashtags.append(tag['text'])
                    temp['hashtags'] = hashtags
                    urls = []
                    if 'urls' in data['entities']:
                        for url in data['entities']['urls']:
                            urls.append(url['url'])
                    temp['urls'] = urls
                    mentions = []
                    if 'user_mentions' in data['entities']:
                        for mention in data['entities']['user_mentions']:
                            mentions.append(mention['screen_name'])
                    temp['mentions'] = mentions
                    media = []
                    if 'media' in data['entities']:
                        for item in data['entities']['media']:
                            media.append((item['media_url'], item['type']))
                    temp['media'] = media
                    temp['source'] = data['source']
                    tempList = []
                    subTemp = {}
                    subTemp['index'] = 0
                    subTemp['favorite_count'] = data['favorite_count']
                    subTemp['retweet_count'] = data['retweet_count']
                    subTemp['user_favorite_count'] = data['user']['favourites_count']
                    subTemp['user_followers_count'] = data['user']['followers_count']
                    subTemp['user_friends_count'] = data['user']['friends_count']
                    subTemp['user_statuses_count'] = data['user']['statuses_count']
                    subTemp['user_listed_count'] = data['user']['listed_count']
                    tempList.append(subTemp)
                    temp['dynamic'] = tempList
                    temp['brand'] = brand
                    tweetData[id] = temp
                else:
                    subTemp = {}
                    subTemp['index'] = len(tweetData[id]['dynamic'])
                    subTemp['favorite_count'] = data['favorite_count']
                    subTemp['retweet_count'] = data['retweet_count']
                    subTemp['user_favorite_count'] = data['user']['favourites_count']
                    subTemp['user_followers_count'] = data['user']['followers_count']
                    subTemp['user_friends_count'] = data['user']['friends_count']
                    subTemp['user_statuses_count'] = data['user']['statuses_count']
                    subTemp['user_listed_count'] = data['user']['listed_count']
                    tweetData[id]['dynamic'].append(subTemp)
            inputFile.close()
        outputFile = open('adData/ConsolidatedTweets/'+brand+'.json', 'w')
        print brand+': '+str(totalIndex)
        for (id, tweet) in tweetData.items():
            outputFile.write(json.dumps(tweet)+'\n')
            combinedOutFile.write(json.dumps(tweet)+'\n')
        outputFile.close()
    combinedOutFile.close()

blend(295, 0)