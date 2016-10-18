__author__ = 'rencui'
import json


def blend(fileSize, offset):
    print 'blending tweets...'
    brandList = []
    listFile = open('brand.list', 'r')
    for line in listFile:
        brandList.append(line.strip())
    listFile.close()

    combinedOutFile = open('dataset/ConsolidatedTweets/total.json', 'w')
    totalIndex = 0
    for brand in brandList:
        outputFile = open('dataset/ConsolidatedTweets/' + brand + '.json', 'w')
        finalOutputFile = open('dataset/ConsolidatedTweets/total.final', 'w')
        tweetIDSet = set()
        tweetData = {}
        finalTweetData = {}
        for index in range(fileSize):
            inputFile = open("C:/Users/renhao.cui/Desktop/ad data/" + brand + '/' + str(index + offset) + '.json', 'r')
            for line in inputFile:
                data = json.loads(line.strip())
                tweetID = data['id']
                if tweetID not in tweetIDSet:
                    totalIndex += 1
                    tweetIDSet.add(tweetID)
                    temp = {'id': tweetID, 'text': data['text'], 'create_at': data['created_at']}
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
                    subTemp = {'index': 0, 'favorite_count': data['favorite_count'], 'retweet_count': data['retweet_count'],
                               'user_favorite_count': data['user']['favourites_count'], 'user_followers_count': data['user']['followers_count'],
                               'user_friends_count': data['user']['friends_count'], 'user_statuses_count': data['user']['statuses_count'],
                               'user_listed_count': data['user']['listed_count']}
                    tempList.append(subTemp)
                    temp['dynamic'] = tempList
                    temp['brand'] = brand
                    tweetData[tweetID] = temp
                    finalTweetData[tweetID] = temp
                else:
                    subTemp = {'index': len(tweetData[tweetID]['dynamic']), 'favorite_count': data['favorite_count'], 'retweet_count': data['retweet_count'],
                               'user_favorite_count': data['user']['favourites_count'], 'user_followers_count': data['user']['followers_count'],
                               'user_friends_count': data['user']['friends_count'], 'user_statuses_count': data['user']['statuses_count'],
                               'user_listed_count': data['user']['listed_count']}
                    finalTweetData[tweetID]['dynamic'][0] = subTemp
                    tweetData[tweetID]['dynamic'].append(subTemp)
            inputFile.close()

        print brand + ': ' + str(totalIndex)
        for (tweetID, tweet) in tweetData.items():
            outputFile.write(json.dumps(tweet) + '\n')
            combinedOutFile.write(json.dumps(tweet) + '\n')
        outputFile.close()
        for (tweetID, tweet) in finalTweetData.items():
            finalOutputFile.write(json.dumps(tweet) + '\n')
        finalOutputFile.close()
    combinedOutFile.close()


if __name__ == "__main__":
    blend(745, 0)
