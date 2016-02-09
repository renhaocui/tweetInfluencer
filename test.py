topicFile = open('results/topic.txt', 'r')
totalFile = open('results/total.txt', 'r')

topicList = {}
totalList = {}
temp = ''
for index, line in enumerate(topicFile):
    if index % 2 == 0:
        temp = line.strip()
    else:
        topicList[temp] = line.strip()

for index, line in enumerate(totalFile):
    if index % 2 == 0:
        temp = line.strip()
    else:
        totalList[temp] = line.strip()

topicFile.close()
totalFile.close()

for id, value in totalList.items():
    if id not in topicList:
        print id
        print value

