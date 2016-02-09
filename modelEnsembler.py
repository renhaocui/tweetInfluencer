import math
import operator
import modelUtility as mu

groupAssign = {'totalGroup': 1, 'brandGroup': 3, 'subBrandGroup': 3, 'topicGroup': 5, 'simGroup':5}
grouping = ['brandGroup', 'subBrandGroup', 'topicGroup', 'simGroup']

# modelTitle, modelGroup, vectorMode, featureMode, inferData, inferParseLength, inferHeadCount
# infer('totalGroup', 0, 1, 2, 'adData/analysis/groups/simGroup/group1', 'adData/analysis/groups/simGroup/parserLength1', 'adData/analysis/groups/simGroup/parserHeadCount1')


def generator(predicts, labels):
    if len(predicts) != len(labels):
        print 'length error!'
    total = 0.0
    count = 0.0
    correct = 0.0
    precision = 0.0
    for index, predict in enumerate(predicts):
        count += 1
        if predict == labels[index]:
            correct += 1
        if predict == '1':
            total += 1
            if labels[index] == '1':
                precision += 1
    return str(precision/total) + '\t' + str(precision/labels.count('1')) + '\t' + str(correct/count)


def loadMapper(groupTitle, groupSize):
    outMapper = {}
    for group in range(groupSize):
        posFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.pos', 'r')
        negFile = open('adData/analysis/groups/' + groupTitle + '/group' + str(group) + '.neg', 'r')
        for line in posFile:
            seg = line.strip().split(' :: ')
            outMapper[seg[5]] = group
        for line in negFile:
            seg = line.strip().split(' :: ')
            outMapper[seg[5]] = group
        posFile.close()
        negFile.close()


    return outMapper

def modelShifter():
    outputFile = open('results/modelShifter.result', 'w')

    outputFile.write('brandGroup using group model 1\n')
    for index in range(groupAssign['brandGroup']):
        out = mu.infer('brandGroup', 0, 1, 2, 'adData/analysis/groups/brandGroup/group'+str(index), 'adData/analysis/groups/brandGroup/parserLength'+str(index), 'adData/analysis/groups/brandGroup/parserHeadCount'+str(index))
        outputFile.write('brandGroup '+str(index)+'\n')
        outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('totalGroup 0'+'\n')
    out = mu.infer('brandGroup', 0, 1, 2, 'adData/analysis/groups/totalGroup/group0', 'adData/analysis/groups/totalGroup/parserLength0', 'adData/analysis/groups/totalGroup/parserHeadCount0')
    outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('\n')

    outputFile.write('subBrandGroup using group model 0\n')
    for index in range(groupAssign['subBrandGroup']):
        out = mu.infer('subBrandGroup', 0, 1, 2, 'adData/analysis/groups/subBrandGroup/group'+str(index), 'adData/analysis/groups/subBrandGroup/parserLength'+str(index), 'adData/analysis/groups/subBrandGroup/parserHeadCount'+str(index))
        outputFile.write('subBrandGroup '+str(index)+'\n')
        outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('totalGroup 0'+'\n')
    out = mu.infer('subBrandGroup', 0, 1, 2, 'adData/analysis/groups/totalGroup/group0', 'adData/analysis/groups/totalGroup/parserLength0', 'adData/analysis/groups/totalGroup/parserHeadCount0')
    outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('\n')

    outputFile.write('topicGroup using group model 1\n')
    for index in range(groupAssign['topicGroup']):
        out = mu.infer('topicGroup', 0, 1, 2, 'adData/analysis/groups/topicGroup/group'+str(index), 'adData/analysis/groups/topicGroup/parserLength'+str(index), 'adData/analysis/groups/topicGroup/parserHeadCount'+str(index))
        outputFile.write('topicGroup '+str(index)+'\n')
        outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('totalGroup 0'+'\n')
    out = mu.infer('totalGroup', 0, 1, 2, 'adData/analysis/groups/totalGroup/group0', 'adData/analysis/groups/totalGroup/parserLength0', 'adData/analysis/groups/totalGroup/parserHeadCount0')
    outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('\n')

    outputFile.write('simGroup using group model 1\n')
    for index in range(groupAssign['simGroup']):
        out = mu.infer('simGroup', 1, 1, 2, 'adData/analysis/groups/simGroup/group'+str(index), 'adData/analysis/groups/simGroup/parserLength'+str(index), 'adData/analysis/groups/simGroup/parserHeadCount'+str(index))
        outputFile.write('simGroup '+str(index)+'\n')
        outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('totalGroup 0'+'\n')
    out = mu.infer('simGroup', 1, 1, 2, 'adData/analysis/groups/totalGroup/group0', 'adData/analysis/groups/totalGroup/parserLength0', 'adData/analysis/groups/totalGroup/parserHeadCount0')
    outputFile.write(str(out[1:])[1:-1]+'\n\n')
    outputFile.write('\n')

    outputFile.close()

def modelEnsemble(mode):
    print 'loading mappers...'
    brandMapper = loadMapper('brandGroup', 3)
    subBrandMapper = loadMapper('subBrandGroup', 3)
    topicMapper = loadMapper('topicGroup', 5)
    simMapper = loadMapper('simGroup', 5)

    print 'loading total data...'
    posFile = open('adData/analysis/groups/totalGroup/group0.pos', 'r')
    negFile = open('adData/analysis/groups/totalGroup/group0.neg', 'r')
    posParseLengthFile = open('adData/analysis/groups/totalGroup/parserLength0.pos', 'r')
    negParseLengthFile = open('adData/analysis/groups/totalGroup/parserLength0.neg', 'r')
    posHeadCountFile = open('adData/analysis/groups/totalGroup/parserHeadCount0.pos', 'r')
    negHeadCountFile = open('adData/analysis/groups/totalGroup/parserHeadCount0.neg', 'r')
    resultFile = open('results/ensemble_Fitted.result', 'w')

    ids = []
    contents = []
    scores = []
    days = []
    time = []
    labels = []
    parseLength = []
    headCount = []
    usernames = []

    for line in posFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        time.append(mu.hourMapper(seg[2]))
        day = seg[1]
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
        days.append(mu.dayMapper[day])
        contents.append(text)
        scores.append(score)
        labels.append(1)

    for line in negFile:
        seg = line.strip().split(' :: ')
        text = seg[3]
        username = seg[7].split(';')
        time.append(mu.hourMapper(seg[2]))
        day = seg[1]
        score = float(seg[0])
        ids.append(seg[5])
        usernames.append(username)
        days.append(mu.dayMapper[day])
        contents.append(text)
        scores.append(score)
        labels.append(0)

    for line in posParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in negParseLengthFile:
        parseLength.append(int(line.strip(' :: ')[0]))
    for line in posHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))
    for line in negHeadCountFile:
        headCount.append(int(line.strip(' :: ')[0]))

    for index in range(len(contents)):
        if index % 100 == 0:
            print index
        if index%1 == 0:
            inferData = {}
            inferData['content'] = contents[index]
            inferData['id'] = ids[index]
            inferData['score'] = scores[index]
            inferData['day'] = days[index]
            inferData['time'] = time[index]
            inferData['parseLength'] = parseLength[index]
            inferData['headCount'] = headCount[index]
            inferData['usernames'] = usernames[index]
            inferData['label'] = labels[index]
            out = inferData['id'] + '\t' + inferData['content']+'\t' + str(inferData['label'])+'\t'
            if mode == 1:
                out += str(mu.infer2('brandGroup', 0, 1, 2, inferData)) + '\t'
                out += str(mu.infer2('subBrandGroup', 0, 1, 2, inferData)) + '\t'
                out += str(mu.infer2('topicGroup', 0, 1, 2, inferData)) + '\t'
                out += str(mu.infer2('simGroup', 1, 1, 2, inferData)) + '\n'
            else:
                if inferData['id'] in brandMapper:
                    output = mu.infer2('brandGroup', brandMapper[inferData['id']], 1, 2, inferData)
                    out += str(output[0]) + '\t' + str(output[1]) + '\t'
                else:
                    out += '-1\t0\t'
                if inferData['id'] in subBrandMapper:
                    output = mu.infer2('subBrandGroup', subBrandMapper[inferData['id']], 1, 2, inferData)
                    out += str(output[0]) + '\t' + str(output[1]) + '\t'
                else:
                    out += '-1\t0\t'
                output = mu.infer2('topicGroup', topicMapper[inferData['id']], 1, 2, inferData)
                out += str(output[0]) + '\t' + str(output[1]) + '\t'
                output = mu.infer2('simGroup', simMapper[inferData['id']], 1, 2, inferData)
                out += str(output[0]) + '\t' + str(output[1])+'\n'
            resultFile.write(out)
    resultFile.close()

def ensembleStat(mode):
    if mode == 1:
        resultFile = open('results/ensembleBest_Both.result', 'r')
    else:
        resultFile = open('results/ensemble_Both.result', 'r')

    count = 0.0
    count2 = 0.0
    idealCountTotal = 0.0
    idealCountBrandTopicSim = 0.0
    idealCountsubBrandTopicSim = 0.0
    idealCountTopicSim = 0.0

    labels = []
    brandLabels = []
    subBrandLabels = []
    topicLabels = []
    simLabels = []

    validLabelsBrand = []
    validLabelssubBrand = []
    validLabelsBrandsubBrand = []

    ensembleEqualTotal = []
    ensembleEqualBrandTopicSim = []
    ensembleEqualsubBrandTopicSim = []
    ensembleEqualTopicSim = []

    ensembleValidEqualTotal = []
    ensembleValidEqualBrandTopicSim = []
    ensembleValidEqualsubBrandTopicSim = []
    ensembleValidEqualTopicSim = []

    ORTotalLabels = []
    ORTopicSimLabels = []
    ORBrandTopicSimLabels = []
    ORsubBrandTopicSimLabels = []
    ANDTotalLabels = []
    ANDTopicSimLabels = []
    ANDBrandTopicSimLabels = []
    ANDsubBrandTopicSimLabels = []

    for line in resultFile:
        data = line.strip().split('\t')
        id = data[0]
        content = data[1]
        label = data[2]
        brandLabel = data[3]
        brandScore = float(data[4])
        subBrandLabel = data[5]
        subBrandScore = float(data[6])
        topicLabel = data[7]
        topicScore = float(data[8])
        simLabel = data[9]
        simScore = float(data[10])
        count += 1
        labels.append(label)

        if mode == 1:
            brandLabels.append(brandLabel)
            subBrandLabels.append(subBrandLabel)

            if topicLabel == label or simLabel == label or brandLabel == label or subBrandLabel == label:
                idealCountTotal += 1
            if brandLabel == subBrandLabel == topicLabel == simLabel:
                ensembleEqualTotal.append(brandLabel)
                ensembleValidEqualTotal.append(label)
            if topicLabel == '1' or simLabel == '1' or brandLabel == '1' or subBrandLabel == '1':
                ORTotalLabels.append('1')
            else:
                ORTotalLabels.append('0')
            if topicLabel == '1' and simLabel == '1' and brandLabel == '1' and subBrandLabel == '1':
                ANDTotalLabels.append('1')
            else:
                ANDTotalLabels.append('0')

        else:
            if brandLabel != '-1':
                brandLabels.append(brandLabel)
                validLabelsBrand.append(label)

                if brandLabel == '1' or topicLabel == '1' or simLabel == '1':
                    ORBrandTopicSimLabels.append('1')
                else:
                    ORBrandTopicSimLabels.append('0')
                if brandLabel == '1' and topicLabel == '1' and simLabel == '1':
                    ANDBrandTopicSimLabels.append('1')
                else:
                    ANDBrandTopicSimLabels.append('0')

                if brandLabel == label or simLabel == label or topicLabel == label:
                    idealCountBrandTopicSim += 1
                if brandLabel == simLabel == topicLabel:
                    ensembleEqualBrandTopicSim.append(brandLabel)
                    ensembleValidEqualBrandTopicSim.append(label)

            if subBrandLabel != '-1':
                subBrandLabels.append(subBrandLabel)
                validLabelssubBrand.append(label)

                if subBrandLabel == '1' or topicLabel == '1' or simLabel == '1':
                    ORsubBrandTopicSimLabels.append('1')
                else:
                    ORsubBrandTopicSimLabels.append('0')
                if subBrandLabel == '1' and topicLabel == '1' and simLabel == '1':
                    ANDsubBrandTopicSimLabels.append('1')
                else:
                    ANDsubBrandTopicSimLabels.append('0')

                if subBrandLabel == label or simLabel == label or topicLabel == label:
                    idealCountsubBrandTopicSim += 1
                if subBrandLabel == simLabel == topicLabel:
                    ensembleEqualsubBrandTopicSim.append(subBrandLabel)
                    ensembleValidEqualsubBrandTopicSim.append(label)

            if brandLabel != '-1' and subBrandLabel != '-1':
                validLabelsBrandsubBrand.append(label)
                count2 += 1
                if brandLabel == '1' or subBrandLabel == '1' or topicLabel == '1' or simLabel == '1':
                    ORTotalLabels.append('1')
                else:
                    ORTotalLabels.append('0')
                if topicLabel == '1' and simLabel == '1' and brandLabel == '1' and subBrandLabel == '1':
                    ANDTotalLabels.append('1')
                else:
                    ANDTotalLabels.append('0')

                if topicLabel == label or simLabel == label or brandLabel == label or subBrandLabel == label:
                    idealCountTotal += 1
                if brandLabel == subBrandLabel == topicLabel == simLabel:
                    ensembleEqualTotal.append(brandLabel)
                    ensembleValidEqualTotal.append(label)

        topicLabels.append(topicLabel)
        simLabels.append(simLabel)

        if topicLabel == label or simLabel == label:
            idealCountTopicSim += 1
        if topicLabel == simLabel:
            ensembleEqualTopicSim.append(topicLabel)
            ensembleValidEqualTopicSim.append(label)

        if topicLabel == '1' or simLabel == '1':
            ORTopicSimLabels.append('1')
        else:
            ORTopicSimLabels.append('0')
        if topicLabel == '1' and simLabel == '1':
            ANDTopicSimLabels.append('1')
        else:
            ANDTopicSimLabels.append('0')

    if mode == 1:
        print ''
        #print 'Ideal total model accuracy: '+str(idealCountTotal/count) + '\t'+str(count)
        #print 'Best brand model performance: '+generator(brandLabels, labels)
        #print 'Best subBrand model performance: '+generator(subBrandLabels, labels)
        #print 'Best OR Total model performance: ' + generator(ORTotalLabels, labels)
        #print 'Best AND total model performance: '+generator(ANDTotalLabels, labels)
        #print 'Best EnsembleEqual total model performance: '+generator(ensembleEqualTotal, ensembleValidEqualTotal)
    else:
        print ''
        #print 'Ideal model (BrandTopicSim) accuracy: '+str(idealCountBrandTopicSim/len(brandLabels)) + '\t' + str(len(brandLabels))
        #print 'Ideal model (subBrandTopicSim) accuracy: '+str(idealCountsubBrandTopicSim/len(subBrandLabels)) + '\t' + str(len(subBrandLabels))
        #print 'Ideal total model accuracy: '+str(idealCountTotal/count2)+'\t'+str(count2)
        #print 'Fitted brand model performance: '+generator(brandLabels, validLabelsBrand)+' '+str(len(validLabelsBrand))
        #print 'Fitted subBrand model performance: '+generator(subBrandLabels, validLabelssubBrand)+'\t'+str(len(validLabelssubBrand))
        #print 'Fitted OR BrandTopicSim model performance: '+generator(ORBrandTopicSimLabels, validLabelsBrand)+'\t'+str(len(validLabelsBrand))
        #print 'Fitted AND BrandTopicSim model performance: '+generator(ANDBrandTopicSimLabels, validLabelsBrand)+'\t'+str(len(validLabelsBrand))
        #print 'Fitted OR subBrandTopicSim model performance: '+generator(ORsubBrandTopicSimLabels, validLabelssubBrand)+'\t'+str(len(validLabelssubBrand))
        #print 'Fitted AND subBrandTopicSim model performance: '+generator(ANDsubBrandTopicSimLabels, validLabelssubBrand)+'\t'+str(len(validLabelssubBrand))
        #print 'Fitted OR Total model performance: '+generator(ORTotalLabels, validLabelsBrandsubBrand)+'\t'+str(len(validLabelsBrandsubBrand))
        #print 'Fitted AND Total model performance: '+generator(ANDTotalLabels, validLabelsBrandsubBrand)+'\t'+str(len(validLabelsBrandsubBrand))
        #print 'Fitted EnsembleEqual Brand model performance: '+generator(ensembleEqualBrandTopicSim, ensembleValidEqualBrandTopicSim)+'\t'+str(len(ensembleValidEqualBrandTopicSim))
        #print 'Fitted EnsembleEqual subBrand model performance: '+generator(ensembleEqualsubBrandTopicSim, ensembleValidEqualsubBrandTopicSim)+'\t'+str(len(ensembleValidEqualsubBrandTopicSim))
        #print 'Fitted EnsembleEqual total model performance: '+generator(ensembleEqualTotal, ensembleValidEqualTotal)+'\t'+str(len(ensembleValidEqualTotal))

    #print 'Ideal model (topic + sim) accuracy: '+str(idealCountTopicSim/count)+'\t'+str(count)
    #print 'Fitted topic model performance: '+generator(topicLabels, labels)+'\t'+str(len(labels))
    #print 'Fitted sim model performance: '+generator(simLabels, labels)+'\t'+str(len(labels))
    #print 'Fitted OR TopicSim model performance: ' + generator(ORTopicSimLabels, labels)+'\t'+str(len(labels))
    #print 'Fitted AND TopicSim model performance: '+generator(ANDTopicSimLabels, labels)+'\t'+str(len(labels))
    #print 'Fitted EnsembleEqual TopicSim model performance: '+generator(ensembleEqualTopicSim, ensembleValidEqualTopicSim)+'\t'+str(len(ensembleValidEqualTopicSim))


def ensembleStat2():
    resultFile = open('results/ensemble_Fitted.result', 'r')

    labels = []
    validLabelsBrand = []
    validLabelsTotal = []
    outputLabelBrand = []
    outputLabelTotal =[]
    outputLabelTopicSim = []

    for line in resultFile:
        data = line.strip().split('\t')
        label = data[2]
        brandLabel = data[3]
        brandScore = math.fabs(float(data[4]))
        subBrandLabel = data[5]
        subBrandScore = math.fabs(float(data[6]))
        topicLabel = data[7]
        topicScore = math.fabs(float(data[8]))
        simLabel = data[9]
        simScore = math.fabs(float(data[10]))

        labels.append(label)
        scoreDict = {'brand': brandScore, 'subBrand': subBrandScore, 'topic':topicScore, 'sim': simScore}
        scoreDict2 = {'topic':topicScore, 'sim': simScore}
        labelDict = {'brand': brandLabel, 'subBrand': subBrandLabel, 'topic': topicLabel, 'sim': simLabel}
        sorted_score = sorted(scoreDict.items(), key=operator.itemgetter(1), reverse=True)
        sorted_score2 = sorted(scoreDict2.items(), key=operator.itemgetter(1), reverse=True)

        if subBrandLabel == '-1' and brandLabel != '-1':
            validLabelsBrand.append(label)
            outputLabelBrand.append(labelDict[sorted_score[0][0]])

        if brandLabel != '-1' and subBrandLabel != '-1':
            validLabelsTotal.append(label)
            outputLabelTotal.append(labelDict[sorted_score[0][0]])

        outputLabelTopicSim.append(labelDict[sorted_score2[0][0]])

    print 'Fitted Ensemble Brand_Topic_Sim model: '+generator(outputLabelBrand, validLabelsBrand)+'\t'+str(len(validLabelsBrand))
    print 'Fitted Ensemble Total model: '+generator(outputLabelTotal, validLabelsTotal)+'\t'+str(len(validLabelsTotal))
    print 'Fitted EnsembleEqual Topic_Sim model: '+generator(outputLabelTopicSim, labels)+'\t'+str(len(labels))


def ensembleStat3():
    resultFile = open('results/ensemble_Fitted.result', 'r')

    labels = []
    validLabelsBrand = []
    validLabelsTotal = []
    outputLabelsubBrand = []
    outputLabelTotal =[]

    for line in resultFile:
        data = line.strip().split('\t')
        label = data[2]
        brandLabel = data[3]
        brandScore = math.fabs(float(data[4]))
        subBrandLabel = data[5]
        subBrandScore = math.fabs(float(data[6]))
        topicLabel = data[7]
        topicScore = math.fabs(float(data[8]))
        simLabel = data[9]
        simScore = math.fabs(float(data[10]))

        labels.append(label)
        scoreDict = {'brand': brandScore, 'subBrand': subBrandScore, 'topic': topicScore, 'sim': simScore}
        labelDict = {'brand': brandLabel, 'subBrand': subBrandLabel, 'topic': topicLabel, 'sim': simLabel}

        if subBrandLabel == '-1' and brandLabel != '-1':
            validLabelsBrand.append(label)
            if labelDict.values().count('1') > labelDict.values().count('0'):
                outputLabelsubBrand.append('1')
            else:
                outputLabelsubBrand.append('0')

        if brandLabel != '-1' and subBrandLabel != '-1':
            validLabelsTotal.append(label)
            posValue = 0.0
            negValue = 0.0
            posCount = 0.0
            negCount = 0.0
            for key, value in scoreDict.items():
                if labelDict[key] == '1':
                    posValue += value
                    posCount += 1
                else:
                    negValue += value
                    negCount += 1
            if posCount == 0:
                outputLabelTotal.append('0')
            elif negCount == 0:
                outputLabelTotal.append('1')
            elif (posValue/posCount) >= (negValue/negCount):
                outputLabelTotal.append('1')
            else:
                outputLabelTotal.append('0')

    print 'Fitted Ensemble Brand_Topic_Sim model: '+generator(outputLabelsubBrand, validLabelsBrand)+'\t'+str(len(validLabelsBrand))
    print 'Fitted Ensemble Total model: '+generator(outputLabelTotal, validLabelsTotal)+'\t'+str(len(validLabelsTotal))

#modelEnsemble(0)
#modelShifter()
#ensembleStat(0)
#ensembleStat2()
ensembleStat2()