import modelUtility as mu

def longestLength(input):
    outputLength = 0
    for key, value in input.items():
        length = 0
        if value != '-1' and value != '_':
            length += 1
            if value == '0':
                if length > outputLength:
                    outputLength = length
                continue
            nextNode = value
            while nextNode != '-1' and nextNode != '_' and nextNode != '0':
                length += 1
                nextNode = input[nextNode]
        if length > outputLength:
            outputLength = length
    return outputLength

def outputHeads(input):
    output = ''
    for key, value in input.items():
        if value[1] == 0:
            output += value[0]+'/'+value[2] + ' '
    return output.strip()

def parseExtractor():
    inputFile = open('adData/analysis/test/test.predict', 'r')
    tempData = {}
    tempOutput = {}
    headCounts = []
    posLengths = []
    for line in inputFile:
        if line.strip() != '':
            words = line.strip().split()
            tempData[words[0]] = words[6]
            tempOutput[int(words[0])] = (words[1], int(words[6]), words[4])
        else:
            posLengths.append(longestLength(tempData))
            headCounts.append(len(outputHeads(tempOutput)))
            tempData = {}
            tempOutput = {}

    inputFile.close()

    return posLengths, headCounts


mentionFile = open('adData/analysis/test/test.mention', 'r')
contentFile = open('adData/analysis/test/test.content', 'r')
day = 'Sat'
time = '17'
contents = []
mentions = []

for line in contentFile:
    contents.append(line.strip())
contentFile.close()

for line in mentionFile:
    mention = line.strip().split(',')
    mentions.append(mention)
mentionFile.close()

(posLengths, headCounts) = parseExtractor()

for index, tweet in enumerate(contents):
    inferData = {'content': tweet, 'day': mu.dayMapper[day], 'time': mu.hourMapper(time), 'parseLength': posLengths[index], 'headCount': headCounts[index], 'usernames': mentions[index]}

    print mu.infer3('totalGroup', 0, 1, 2, inferData)