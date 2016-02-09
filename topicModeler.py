import glob
import os
import shutil
import subprocess

__author__ = 'renhao.cui'

def genTopicFeatures():
    outputFeatures = {}
    print 'Running LDA modelling...'
    '''
    for cacheFile in glob.glob('tmtData\\data.csv.term-counts.cache*'):
        os.remove(cacheFile)
    if os.path.exists('TMT Cache'):
        shutil.rmtree('TMT Cache')
    subprocess.check_output(
        'java -Xms1000m -Xmx1000m -jar tmtData\\tmt-0.4.0.jar tmtData\\script.scala',
        shell=True)
    '''
    distFile = open('tmtData\\document-topic-distributions.csv', 'r')
    topicIndex = []
    for line in distFile:
        item = line.strip().split(',')
        topicIndex.append(int(item[0]))
        temp = []
        for prob in item[1:]:
            temp.append(float(prob))
        outputFeatures[int(item[0])] = temp
    distFile.close()
    return outputFeatures, topicIndex