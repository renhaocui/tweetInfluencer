__author__ = 'rencui'
import json
import twitter
import time
from sets import Set
import os

logFile = open('log', 'w')

brandList = []
listFile = open('brand.list', 'r')
for line in listFile:
    brandList.append(line.strip())
listFile.close()

for brand in brandList:
    if not os.path.isdir('adData//'+brand):
        os.makedirs('adData//'+brand)


c_k = 'NNFnQv3zyeM99IDXg1IOrtMcQ'
c_s = 'GDc4vZtorwOiPgDNiaGrWDTWfqKNW2ZzMOTUkpJuF7gLdBCLZI'
a_t = '141612471-AnWgHssHt5rtOhlC8Cmy6GwEge9Z81v8MHQw6nXr'
a_t_s = 'gNE1nOhhc5CJoinMR6eUuyYBLR8YT3wK0tRb4yTUAY8Od'

requestLimit = 180


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


for index in range(2800):
    index = index + 13
    print 'round: '+str(index)
    logFile.write('round: '+str(index)+'\n')
    logFile.flush()
    brandIDSet = {}
    for brand in brandList:
        brandIDSet[brand] = Set([])

    twitter_api = oauth_login()
    startTime = time.time()
    requestNum = 0
    for brand in brandList:
        print 'extracting tweets for: '+brand
        logFile.write('extracting tweets for: '+brand+'\n\n')
        recordFile = open("adData//" + brand + '//' + str(index)+'.json', 'w')
        for i in range(10):
            requestNum += 1
            if requestNum > requestLimit:
                print 'waiting for 15m...'
                logFile.write('waiting for 15m...\n\n')
                logFile.flush()
                time.sleep(900)
                requestNum = 0
            try:
                statuses = twitter_api.statuses.user_timeline(screen_name=brand, include_rts='false',
                                                          exclude_replies='true', count=200)
            except Exception as e:  # take care of errors
                print 'API ERROR: '+str(e)
                logFile.write('API ERROR: '+str(e)+'\n')
                logFile.write('')
                logFile.flush()
                continue
            for tweet in statuses:
                if tweet['id'] not in brandIDSet[brand]:
                    brandIDSet[brand].add(tweet['id'])
                    recordFile.write(json.dumps(tweet))
                    recordFile.write('\n')
        recordFile.close()
        logFile.flush()
    endTime = time.time()

    print 'Paused for next extraction in 12 hours...'
    logFile.write('Paused for next extraction in 12 hours...')
    logFile.flush()
    time.sleep(startTime + 43200 - endTime)

logFile.close()