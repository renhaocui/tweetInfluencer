__author__ = 'rencui'
import json
import twitter
import time
from sets import Set

brandList = ['amazon', 'dominos', 'Gap', 'Jeep', 'AppStore', 'Chilis', 'Colgate', 'Motorola', 'AmericanExpress',
             'Microsoft']

logFile = open('log', 'w')

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



for index in range(280):
    brandIDSet = {}
    for brand in brandList:
        brandIDSet[brand] = Set([])

    twitter_api = oauth_login()
    startTime = time.time()

    for brand in brandList:
        logFile.write('extracting tweets for: '+brand)
        recordFile = open("adData//" + brand + '.' + str(index+12), 'w')
        for i in range(requestLimit / len(brandList)):
            try:
                statuses = twitter_api.statuses.user_timeline(screen_name=brand, include_rts='false',
                                                          exclude_replies='true', count=200)
            except Exception as e:  # take care of errors
                logFile.write('API ERROR: '+str(e))
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

    logFile.write('Paused for next extraction')
    logFile.flush()
    time.sleep(startTime + 43200 - endTime)

logFile.close()