__author__ = 'rencui'
import tweetBlender
import outlierLocator
import contenter
import parserExtractor
import tweetGrouper
import basicModel

# blender the brand dataset
tweetBlender.blend(300, 0)
# remove outliers and assign labels
outlierLocator.outlierExtractor()
# extract content and parse
contenter.contenter2()
# need to run TweeboParser here
parserExtractor.extractor()
# grouping the data
tweetGrouper.runGrouper()
# run the experiment
basicModel.runModel()