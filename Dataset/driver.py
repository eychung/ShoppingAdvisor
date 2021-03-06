import userData
import csv

# If no score is present because id does not match, returning 0 means there is no score available.
def getScoreOfProduct(pid):
	with open('userData.csv') as csvfile:
		count = 0
		score = 0

		reader = csv.reader(csvfile)
		reader.next() # skip header

		for userId, productId, rating, userAtrributes in reader:

			if productId == str(pid):
				score += float(rating)
				count += 1
		
		if score > 0:
			score = score/count

		return score

# We notice that the scores are around 2.5.
def testGetScoreOfProduct():
	for count in range(100):
		pid = userData.getRandProduct(userData.getRandProductAssociation())
		print "pid " + str(pid) + " has score " + str(getScoreOfProduct(pid))
