import time

__author__ = 'renhao.cui'
import json
import twitter

c_k = 'R2FZHZcAcHFatakYhKL2cQcVo'
c_s = 'jwkcIPCkrOBdxKVTVVE7d7cIwH8ZyHHtqxYeCVUZs35Lu4BOkY'
a_t = '141612471-3UJPl93cGf2XBm2JkBn26VFewzwK3WGN1EiKJi4T'
a_t_s = 'do1I1vtIvjgQF3vr0ln4pYVbsAj5OZIxuuATXjgBaqUYM'

def oauth_login():
    # credentials for OAuth
    CONSUMER_KEY = c_k
    CONSUMER_SECRET = c_s
    OAUTH_TOKEN = a_t
    OAUTH_TOKEN_SECRET = a_t_s
    # Creating the authentification
    auth = twitter.oauth.OAuth(OAUTH_TOKEN,
                               OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY,
                               CONSUMER_SECRET)
    # Twitter instance
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

requestLimit = 15
brandList = []
followerIDSet = {}
listFile = open('brand.list', 'r')
for line in listFile:
    brandList.append(line.strip())
listFile.close()

index = 0
twitter_api = oauth_login()
requestNum = 0
for brand in brandList:
    followerIDSet = set()
    print 'extracting followers for: '+brand
    recordFile = open("followers//" + brand + '.json', 'a')
    nextCursor = 0
    for i in range(10000):
        if i == 0:
            csr = -1
        else:
            csr = nextCursor
        try:
            response = twitter_api.followers.list(screen_name=brand,include_user_entities='true', count=200, cursor = csr, skip_status = 'false')
            nextCursor = response['next_cursor']
            if nextCursor == 0 or len(followerIDSet) > 50000:
                break
            else:
                for data in response['users']:
                    if data['id'] not in followerIDSet:
                        followerIDSet.add(data['id'])
                        recordFile.write(json.dumps(data))
                        recordFile.write('\n')
        except Exception as e:
            print (e)
            print 'Wait for 15 mins...'
            time.sleep(900)
            continue
    recordFile.close()

