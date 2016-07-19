__author__ = 'rencui'

def contenter(indexList):
    print 'generating content....'
    for group in indexList:
        totalRankedFile1 = open('adData/analysis/ranked/1/topic'+str(group)+'.pos', 'r')
        totalRankedFile2 = open('adData/analysis/ranked/2/topic'+str(group)+'.neg', 'r')
        outputFile1 = open('adData/analysis/ranked/content/topic'+str(group)+'.posContent', 'w')
        outputFile2 = open('adData/analysis/ranked/content/topic'+str(group)+'.negContent', 'w')

        for line in totalRankedFile1:
            data = line.strip().split(' : ')
            outputFile1.write(data[3]+'\n')

        for line in totalRankedFile2:
            data = line.strip().split(' : ')
            outputFile2.write(data[3]+'\n')
    
        totalRankedFile1.close()
        totalRankedFile2.close()
        outputFile1.close()
        outputFile2.close()

def contenterExtractor():
    totalRankedFile1 = open('dataset/experiment/ranked/total.pos', 'r')
    totalRankedFile2 = open('dataset/experiment/ranked/total.neg', 'r')
    outputFile1 = open('dataset/experiment/content/total.posContent', 'w')
    outputFile2 = open('dataset/experiment/content/total.negContent', 'w')

    for line in totalRankedFile1:
        data = line.strip().split(' :: ')
        outputFile1.write(data[3]+'\n')

    for line in totalRankedFile2:
        data = line.strip().split(' :: ')
        outputFile2.write(data[3]+'\n')

    totalRankedFile1.close()
    totalRankedFile2.close()
    outputFile1.close()
    outputFile2.close()


#contenter([0,1,2,3,4, 'Total'])