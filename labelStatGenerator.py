__author__ = 'renhao.cui'
import json
import statistics as stat

inputFile = open('adData//total.tweet', 'r')

favRatioFullList = []
favRetRatioFullList = []
list1=[]
list2=[]
favRatioList = []
favRetRatioList = []
followerLabelList = []
followerLabelFullList = []
listLabelList = []
listLabelFullList = []
friendLabelList = []
friendLabelFullList = []
for line in inputFile:
    data = json.loads(line.strip())
    id = data['id']
    finalIndex = len(data['dynamic'])-1
    totalFavorite = float(data['dynamic'][finalIndex]['user_favorite_count'])
    followers = float(data['dynamic'][finalIndex]['user_followers_count'])
    listed = float(data['dynamic'][finalIndex]['user_listed_count'])
    friends = float(data['dynamic'][finalIndex]['user_friends_count'])
    totalTweet = float(data['dynamic'][finalIndex]['user_statuses_count'])
    retweet = float(data['dynamic'][finalIndex]['retweet_count'])
    favorite = float(data['dynamic'][finalIndex]['favorite_count'])
    avgFavorite = totalFavorite/totalTweet
    favRatio = favorite/avgFavorite
    if retweet == 0:
        favRetRatio = -1
    else:
        favRetRatio = favorite/retweet
    if 50000 > favRatio > 0:
        favRatioList.append(favRatio)
    favRatioFullList.append(favRatio)
    if 10 > favRetRatio > 0:
        favRetRatioList.append(favRetRatio)
    favRetRatioFullList.append(favRetRatio)
    followerLabelData = (2*retweet + favorite)*10000/followers
    if 5 > followerLabelData > 0:
        followerLabelList.append(followerLabelData)
    followerLabelFullList.append(followerLabelData)
    listLabelData = (2*retweet+favorite)*100/listed
    if 10 > listLabelData > 0:
        listLabelList.append(listLabelData)
    listLabelFullList.append(listLabelData)
    friendLabelData = (2*retweet+favorite)*10/friends
    if 10 > friendLabelData > 0:
        friendLabelList.append(friendLabelData)
    friendLabelFullList.append(friendLabelData)

print 'favRatio'
print stat.mean(favRatioFullList)
print stat.median(favRatioFullList)
print stat.median(favRatioList)
print float(len(favRatioList))/len(favRatioFullList)
print stat.mean(favRatioList)
print stat.stdev(favRatioList)

for point in favRatioFullList:
    if point >= stat.median(favRatioFullList):
        list1.append(point)
    else:
        list2.append(point)
print stat.median(list1)
print stat.median(list2)


print '\nfavRetRatio'
print stat.mean(favRetRatioFullList)
print stat.median(favRetRatioFullList)
print stat.median(favRetRatioList)
print float(len(favRetRatioList))/len(favRetRatioFullList)
print stat.mean(favRetRatioList)
print stat.median(favRetRatioList)
print stat.stdev(favRetRatioList)

print '\nFollowerLabels'
print stat.mean(followerLabelFullList)
print stat.median(followerLabelFullList)
print stat.stdev(followerLabelFullList)
print float(len(followerLabelList))/len(followerLabelFullList)
print stat.mean(followerLabelList)
print stat.median(followerLabelList)
print stat.stdev(followerLabelList)

print '\nListLabels'
print stat.mean(listLabelFullList)
print stat.median(listLabelFullList)
print stat.stdev(listLabelFullList)
print float(len(listLabelList))/len(listLabelFullList)
print stat.mean(listLabelList)
print stat.median(listLabelList)
print stat.stdev(listLabelList)

print '\nFriendLabels'
print stat.mean(friendLabelFullList)
print stat.median(friendLabelFullList)
print stat.stdev(friendLabelFullList)
print float(len(friendLabelList))/len(friendLabelFullList)
print stat.mean(friendLabelList)
print stat.median(friendLabelList)
print stat.stdev(friendLabelList)
