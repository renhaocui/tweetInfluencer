__author__ = 'rencui'
from sklearn import svm
from sklearn import cross_validation

dayMapper = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}
posFile = open('adData\\analysis\\ranked\\1\\total.pos', 'r')
negFile = open('adData\\analysis\\ranked\\2\\total.neg', 'r')

meta = []
labels = []
for line in posFile:
    seg = line.strip().split(' : ')
    meta.append([dayMapper[seg[1]]])
    labels.append(1)
posSize = len(meta)

for line in negFile:
    seg = line.strip().split(' : ')
    meta.append([dayMapper[seg[1]]])
    labels.append(2)

posFile.close()
negFile.close()

precisionSum = 0.0
recallSum = 0.0
accuracySum = 0.0
for i in range(5):
    feature_train, feature_test, label_train, label_test = cross_validation.train_test_split(meta, labels, test_size=0.2, random_state=42)

    svmModel = svm.SVC().fit(feature_train, label_train)
    predictions = svmModel.predict(feature_test)
    print predictions
    print label_test
    precisionCount = 0.0
    totalCount = 0.0
    recallCount = 0.0
    if len(predictions) != len(label_test):
        print 'inference error!'
    for index, label in enumerate(predictions):
        if label == 1:
            if label_test[index] == 1:
                precisionCount += 1
            totalCount += 1
        if label_test[index] == 1 and label == 1:
            recallCount += 1
    if totalCount == 0:
        precision = 0
    else:
        precision = precisionCount / totalCount
    recall = recallCount / label_test.count(1)
    accuracy = svmModel.score(feature_test, label_test)

    precisionSum += precision
    recallSum += recall
    accuracySum += accuracy

print precisionSum/5
print recallSum/5
print accuracySum/5