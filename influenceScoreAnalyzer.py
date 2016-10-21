import json


def analyzer():
    inputFile = open('dataset/ConsolidatedTweets/total.json', 'r')
    favoriteData = []
    retweetData = []
    scores = []
    for line in inputFile:
        data = json.loads(line.strip())
        finalIndex = len(data['dynamic']) - 1
        retweet = float(data['dynamic'][finalIndex]['retweet_count'])
        favorite = float(data['dynamic'][finalIndex]['favorite_count'])
        followers = float(data['dynamic'][finalIndex]['user_followers_count'])
        if followers == 0:
            score = 0
        else:
            score = (2.0 * retweet + favorite) * 10000 / followers
        favoriteData.append(favorite)
        retweetData.append(retweet)
        scores.append(score)
    inputFile.close()

    favoriteFile = open('dataset/analysis/favorite.list', 'w')
    retweetFile = open('dataset/analysis/retweet.list', 'w')
    scoreFile = open('dataset/analysis/score.list', 'w')
    for item in favoriteData:
        favoriteFile.write(str(item)+'\n')
    for item in retweetData:
        retweetFile.write(str(item)+'\n')
    for item in scores:
        scoreFile.write(str(item)+'\n')
    favoriteFile.close()
    retweetFile.close()
    scoreFile.close()

if __name__ == "__main__":
    analyzer()