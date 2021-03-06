import csv
import cPickle
import itertools
import random
import sys

dataPath = "../Dataset/"
trainPath = "train/"
testPath = "test/"

userTableFilePath = "userData.csv"
productTableFilePath = "products.txt"
trainFilePath = "Train.csv"
testFilePath = "Test.csv"
compressedTrainFilePath = "Compressed Train.csv"
productUserAttributesFilePath = "productUserAttributes.csv"

# Note that "code" (2) and "industry" (3) can be tree nodes or leaf nodes.
userAttributesLevel1 = ["work", "casual"]
userAttributesLevel2 = ["code1", "admin", "gaming", "applications"]
userAttributesLevel3 = ["graphic_intensive", "data_intensive", "advance_usage", "simple_usage", "hardcore", "softcore", "browsing", "software"]
userAttributesLevel4 = ["game_dev", "artist", "scientist", "engineer", "comm", "data", "word_processing", "pos", "repetitive", "strategic", "real_time", "casino_games", "media", "website", "writing", "designing"]
userAttributesLevel5 = ["graphic_design", "game_engine", "vector", "animator", "research", "industry1", "school", "industry2", "high_end_user", "low_end_user", "operator", "system_admin", "student", "industry3", "small_business", "large_business", "pictures", "video", "online_gaming", "social", "long_form", "short_form", "code2", "art"]
userAttributes = userAttributesLevel1 + userAttributesLevel2 + userAttributesLevel3 + userAttributesLevel4 + userAttributesLevel5

class User():
	def __init__(self):
		self.reviews = []

class Review():
	def __init__(self):
		self.product = -1
		self.rating = -1
		self.userAttributes = []
		self.reviewedBy = []

class Product():
	def __init__(self):
		self.base = -1
		self.technicalAttributes = []
		self.reviewedBy = []
		self.possibleUserAttributes = []

def loadUsersProducts():
	users = {}
	reviews = {}
	products = {}
	
	with open(dataPath + userTableFilePath) as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for userId, productId, rating, userAttributes in reader:
			userId, productId = int(userId), int(productId)
			if userId not in users:
				users[userId] = User()
			userReview = Review()
			userReview.product = productId
			userReview.rating = rating
			userReview.userAttributes.append(userAttributes)
			users[userId].reviews.append(userReview)
			if productId not in products:
				products[productId] = Product()
			products[productId].reviewedBy.append(userId)
			for userAttribute in userAttributes.split(' '):
				if userAttribute not in products[productId].possibleUserAttributes:
					products[productId].possibleUserAttributes.append(userAttribute)

	with open(dataPath + productTableFilePath) as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for productId, base, technicalAttributes in reader:
			productId = int(productId)
			if productId not in products:
				products[productId] = Product()
			products[productId].base = base
			products[productId].technicalAttributes.append(technicalAttributes)
	
	return users, products

def saveFeature(feature, name, mode):
	path = ""
	if mode == 'train':
		path = trainPath
	elif mode == 'test':
		path = testPath
	filename = path + name + '.' + mode
	print 'saving feature to', filename, '...'
	cPickle.dump(feature, open(filename, 'wb'))

def csvGenerator(mode):
	if mode == 'train':
		with open(dataPath + trainFilePath) as csvfile:
			reader = csv.reader(csvfile)
			reader.next()
			for productId, rating, correctUserAttributes, incorrectUserAttributes in reader:
				yield productId, correctUserAttributes, incorrectUserAttributes

	elif mode == 'test':
		with open(dataPath + testFilePath) as csvfile:
			reader = csv.reader(csvfile)
			reader.next()
			for productId, rating, userAttributes in reader:
				yield productId, userAttributes

	else:
		print 'mode must be "train" or "test"'
		raise ValueError

def createCompressedTrainFile(products):
	compressedTrainFile = open(dataPath + compressedTrainFilePath, mode='w')
	compressedTrainFile.write("ProductId,PossibleUserAttributes\n")
	for productId in products:
		compressedTrainFile.write(str(productId) + ',' + ' '.join(products[productId].possibleUserAttributes) + '\n')
	compressedTrainFile.close()

# Returns a list of products, each with a list of possible user attributes collected from a compressed train file.
def labels(mode='train'):
	global userAttributes
	labels = []
	if mode == 'train':
		with open(dataPath + compressedTrainFilePath) as csvfile:
			reader = csv.reader(csvfile)
			reader.next()
			for productId, possibleUserAttributes in reader:
				mylabels = []
				for userAttribute in userAttributes:
					if userAttribute in possibleUserAttributes:
						mylabels.append(1)
					else:
						mylabels.append(0)
				labels.append(mylabels)
	
	elif mode == 'test':
		for productId, userAttributes in csvGenerator(mode=mode):
			labels.append([productId, userAttributes])
	
	else:
		print 'mode must be "train" or "test"'
		raise ValueError

	saveFeature(labels, name='labels', mode=mode)

# Creates a file with a list of products, each with a list of correct user attributes.
def createFeatureFiles(users, products, mode='train'):
	global userAttributes
	features = []
	with open(dataPath + productUserAttributesFilePath) as csvfile:
		reader = csv.reader(csvfile)
		reader.next()

		for productId, attributes in reader:
			myfeatures = []
			for userAttribute in userAttributes:
				if userAttribute in attributes:
					myfeatures.append(1)
				else:
					myfeatures.append(0)
			features.append(myfeatures)			

		saveFeature(features, name='user_attributes', mode=mode)

if __name__ == '__main__':
	users, products = loadUsersProducts()
	createCompressedTrainFile(products)
	
	for mode in ['train', 'test']:
		labels(mode=mode)

	createFeatureFiles(users, products)
