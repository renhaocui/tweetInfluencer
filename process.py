__author__ = 'rencui'
import tweetBlender
import dataLabeler
import contenter
import parserExtractor
import tweetGrouper
import runModel

# blender the brand dataset
tweetBlender.blend(300, 0)
# remove outliers and assign labels
dataLabeler.outlierExtractor()
# extract content and parse
contenter.contenterExtractor()
# need to run TweeboParser here
parserExtractor.extractor()
# grouping the data
tweetGrouper.runGrouper()
# run the experiment
runModel(1, 'totalGroup', 2, 4, 'SVM', outputFile='results/temp.result')