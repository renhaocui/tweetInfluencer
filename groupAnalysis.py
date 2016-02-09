__author__ = 'rencui'
import statistics as stat

def hourMapper(hour):
    input = int(hour)
    if 0 <= input < 6:
        output = 0
    elif 6 <= input < 12:
        output = 1
    elif 12 <= input < 18:
        output = 2
    else:
        output = 3

    return output


def analyzer(groupSize, groupTitle):
    # tweetID, group, brand, performanceScore, day, time, parserLength, headCount
    posFile = open('adData/analysis/groups/' + groupTitle + '/details.pos', 'r')
    negFile = open('adData/analysis/groups/' + groupTitle + '/details.neg', 'r')

    brandList = []
    listFile = open('brand.list', 'r')
    for line in listFile:
        brandList.append(line.strip())
    listFile.close()
    posTotalBrandCounter = {}
    negTotalBrandCounter = {}
    for brand in brandList:
        posTotalBrandCounter[brand] = 0.0
        negTotalBrandCounter[brand] = 0.0

    groupData = {}
    posTotalScoreList = []
    posTotalParseLengthList = []
    posTotalHeadCountList = []
    negTotalScoreList = []
    negTotalParseLengthList = []
    negTotalHeadCountList = []
    for i in range(groupSize):
        groupData[i] = {'posDayCounter': {},
                        'posTimeCounter': {},
                        'posBrandCounter': {},
                        'posScoreList': [],
                        'posParseLengthList': [],
                        'posHeadCountList': [],
                        'negDayCounter': {},
                        'negTimeCounter': {},
                        'negBrandCounter': {},
                        'negScoreList': [],
                        'negParseLengthList': [],
                        'negHeadCountList': []}

    for line in posFile:
        items = line.strip().split('\t')
        group = int(items[1])
        brand = items[2]
        score = items[3]
        day = items[4]
        time = items[5]
        parserLength = items[6]
        headCount = items[7]
        if day not in groupData[group]['posDayCounter']:
            groupData[group]['posDayCounter'][day] = 1
        else:
            groupData[group]['posDayCounter'][day] += 1
        if hourMapper(time) not in groupData[group]['posTimeCounter']:
            groupData[group]['posTimeCounter'][hourMapper(time)] = 1
        else:
            groupData[group]['posTimeCounter'][hourMapper(time)] += 1
        if brand not in groupData[group]['posBrandCounter']:
            groupData[group]['posBrandCounter'][brand] = 1
        else:
            groupData[group]['posBrandCounter'][brand] += 1
        groupData[group]['posScoreList'].append(float(score))
        groupData[group]['posParseLengthList'].append(float(parserLength))
        groupData[group]['posHeadCountList'].append(float(headCount))
        posTotalScoreList.append(float(score))
        posTotalParseLengthList.append(float(parserLength))
        posTotalHeadCountList.append(float(headCount))
    posFile.close()

    for line in negFile:
        items = line.strip().split('\t')
        group = int(items[1])
        brand = items[2]
        score = items[3]
        day = items[4]
        time = items[5]
        parserLength = items[6]
        headCount = items[7]
        if day not in groupData[group]['negDayCounter']:
            groupData[group]['negDayCounter'][day] = 1
        else:
            groupData[group]['negDayCounter'][day] += 1
        if hourMapper(time) not in groupData[group]['negTimeCounter']:
            groupData[group]['negTimeCounter'][hourMapper(time)] = 1
        else:
            groupData[group]['negTimeCounter'][hourMapper(time)] += 1
        if brand not in groupData[group]['negBrandCounter']:
            groupData[group]['negBrandCounter'][brand] = 1
        else:
            groupData[group]['negBrandCounter'][brand] += 1
        groupData[group]['negScoreList'].append(float(score))
        groupData[group]['negParseLengthList'].append(float(parserLength))
        groupData[group]['negHeadCountList'].append(float(headCount))
        negTotalScoreList.append(float(score))
        negTotalParseLengthList.append(float(parserLength))
        negTotalHeadCountList.append(float(headCount))
    negFile.close()

    for i in range(groupSize):
        print 'group: '+str(i)
        print 'pos'

        print 'Day Counter'
        for key, value in groupData[i]['posDayCounter'].items():
            print key + '\t' + str(value)
        print 'Time Counter'
        for key, value in groupData[i]['posTimeCounter'].items():
            print str(key) + '\t' + str(value)
        print 'Brand Counter'
        for brand in brandList:
            if brand not in groupData[i]['posBrandCounter']:
                print brand + '\t0'
                posTotalBrandCounter[brand] += 0.0
            else:
                print brand + '\t' + str(groupData[i]['posBrandCounter'][brand])
                posTotalBrandCounter[brand] += groupData[i]['posBrandCounter'][brand]
        print ''
        print 'Performance Score'
        print 'Mean' + '\t' + str(stat.mean(groupData[i]['posScoreList']))
        print 'Median' + '\t' + str(stat.median(groupData[i]['posScoreList']))
        print 'Stdev' + '\t' + str(stat.stdev(groupData[i]['posScoreList']))
        print 'Parse Length'
        print 'Mean' + '\t' + str(stat.mean(groupData[i]['posParseLengthList']))
        print 'Median' + '\t' + str(stat.median(groupData[i]['posParseLengthList']))
        print 'Stdev' + '\t' + str(stat.stdev(groupData[i]['posParseLengthList']))
        print 'Head Count'
        print 'Mean' + '\t' + str(stat.mean(groupData[i]['posHeadCountList']))
        print 'Median' + '\t' + str(stat.median(groupData[i]['posHeadCountList']))
        print 'Stdev' + '\t' + str(stat.stdev(groupData[i]['posHeadCountList']))

        print 'neg'

        print 'Day Counter'
        for key, value in groupData[i]['negDayCounter'].items():
            print key + '\t' + str(value)
        print 'Time Counter'
        for key, value in groupData[i]['negTimeCounter'].items():
            print str(key) + '\t' + str(value)
        print 'Brand Counter'
        for brand in brandList:
            if brand not in groupData[i]['negBrandCounter']:
                print brand + '\t0'
                negTotalBrandCounter[brand] += 0.0
            else:
                print brand + '\t' + str(groupData[i]['negBrandCounter'][brand])
                negTotalBrandCounter[brand] += groupData[i]['negBrandCounter'][brand]
        print ''
        print 'Performance Score'
        print 'Mean' + '\t' + str(stat.mean(groupData[i]['negScoreList']))
        print 'Median' + '\t' + str(stat.median(groupData[i]['negScoreList']))
        print 'Stdev' + '\t' + str(stat.stdev(groupData[i]['negScoreList']))
        print 'Parse Length'
        print 'Mean' + '\t' + str(stat.mean(groupData[i]['negParseLengthList']))
        print 'Median' + '\t' + str(stat.median(groupData[i]['negParseLengthList']))
        print 'Stdev' + '\t' + str(stat.stdev(groupData[i]['negParseLengthList']))
        print 'Head Count'
        print 'Mean' + '\t' + str(stat.mean(groupData[i]['negHeadCountList']))
        print 'Median' + '\t' + str(stat.median(groupData[i]['negHeadCountList']))
        print 'Stdev' + '\t' + str(stat.stdev(groupData[i]['negHeadCountList']))
        print ''
        print 'total'
        print 'pos'
        print 'Performance Score'
        print 'Mean' + '\t' + str(stat.mean(posTotalScoreList))
        print 'Median' + '\t' + str(stat.median(posTotalScoreList))
        print 'Stdev' + '\t' + str(stat.stdev(posTotalScoreList))
        print 'Parse Length'
        print 'Mean' + '\t' + str(stat.mean(posTotalParseLengthList))
        print 'Median' + '\t' + str(stat.median(posTotalParseLengthList))
        print 'Stdev' + '\t' + str(stat.stdev(posTotalParseLengthList))
        print 'Head Count'
        print 'Mean' + '\t' + str(stat.mean(posTotalHeadCountList))
        print 'Median' + '\t' + str(stat.median(posTotalHeadCountList))
        print 'Stdev' + '\t' + str(stat.stdev(posTotalHeadCountList))
        print 'neg'
        print 'Performance Score'
        print 'Mean' + '\t' + str(stat.mean(negTotalScoreList))
        print 'Median' + '\t' + str(stat.median(negTotalScoreList))
        print 'Stdev' + '\t' + str(stat.stdev(negTotalScoreList))
        print 'Parse Length'
        print 'Mean' + '\t' + str(stat.mean(negTotalParseLengthList))
        print 'Median' + '\t' + str(stat.median(negTotalParseLengthList))
        print 'Stdev' + '\t' + str(stat.stdev(negTotalParseLengthList))
        print 'Head Count'
        print 'Mean' + '\t' + str(stat.mean(negTotalHeadCountList))
        print 'Median' + '\t' + str(stat.median(negTotalHeadCountList))
        print 'Stdev' + '\t' + str(stat.stdev(negTotalHeadCountList))

    print ''
    for i in range(groupSize):
        print 'pos'
        for brand in brandList:
            if brand not in groupData[i]['posBrandCounter']:
                print brand + '\t0'
            else:
                print brand + '\t' + str(groupData[i]['posBrandCounter'][brand]/posTotalBrandCounter[brand])
        print 'neg'
        for brand in brandList:
            if brand not in groupData[i]['negBrandCounter']:
                print brand + '\t0'
            else:
                print brand + '\t' + str(groupData[i]['negBrandCounter'][brand]/negTotalBrandCounter[brand])


#analyzer(1, 'totalGroup')
#analyzer(3, 'brandGroup')
analyzer(5, 'simGroup')