#!/usr/bin/python
#-*- coding:utf-8 -*-


import utilsOs
import time, datetime, random, cv2, urllib.request
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException




####################################################################################
#GENERAL FUNCTIONS
####################################################################################

def getCategorySpecificHashtagList(categoryNameList=u'all', emojiCharDictPath=u'./emojiDict/emojiCharDict.json'):
	'''
	given a list of category names ('people', 'nature', 'food-drink', 'activity', 'travel-places', 'objects', 'symbols', 'flags')
	opens the emoji char dict and returns a set of the given category
	'''
	emojiHashtagSet = set([])
	emojiCharDict = utilsOs.openJsonFileAsDict(emojiCharDictPath)
	for emoji, valDict in emojiCharDict.items():
		#take the specified categories
		if categoryNameList == u'all' or valDict[u'category'] in categoryNameList:
			hashtagList = valDict[u'hashtags']
			#populate the hashtag dict
			for hashtag in hashtagList:
				emojiHashtagSet.add(hashtag)
	return emojiHashtagSet


def makeRandomComment(emojiHashtag=None, emojiHashtagDictPath=u'./emojiDict/emojiHashtagDict.json'):
	'''	returns a random comment '''
	#make the comment by associating from a set of lists at random
	epithet = [u'Nice', u'Good', u'Awesome', u'Pretty nice', u'Pretty good', u'Pretty awesome']
	nominal = [u'', u' one', u' pic', u' picture', u' photo']
	punctuation = [u'', u'!']
	comment = u'{0}{1}{2}'.format(epithet[random.randint(0, len(epithet)-1)], nominal[random.randint(0, len(nominal)-1)], punctuation[random.randint(0, len(punctuation)-1)])
	#if there is an emoji hashtag, wee add it to the comment
	if emojiHashtag != None:
		emojiHashtagDict = utilsOs.openJsonFileAsDict(emojiHashtagDictPath)
		emojiList = emojiHashtagDict[emojiHashtag]
		#if there are multiple possible emojis, choose one at random
		if len(emojiList) != 1:
			emoji = emojiList[random.randint(0, len(emojiList)-1)]
		#if there is only one possible emoji, capture it
		else: emoji = emojiList[0]
		#add emoji to comment
		comment = u'{0} {1}{2}'.format(comment.replace(u'!', u''), emoji, punctuation[random.randint(0, len(punctuation)-1)])
	return comment


####################################################################################
#SELENIUM GENERAL FUNCTIONS
####################################################################################

def waitForPageToLoad(driver, xpathToElem, maxWaitTimeSeconds=25):
	''' waits for the page to load and returns the element '''
	element = WebDriverWait(driver, maxWaitTimeSeconds).until(EC.presence_of_element_located((By.XPATH, xpathToElem)))
	return element


def scrollPageWithInfiniteLoading(driver, limit=float('inf')):
	'''
	scroll social networks with infinite loading
	from https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
	'''
	counter = 0
	# Get scroll height
	last_height = driver.execute_script('return document.body.scrollHeight')
	#loop
	while counter <= limit:
		# Scroll down to bottom
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
		# Wait to load page
		time.sleep(random.uniform(0.5, 0.8))
		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script('return document.body.scrollHeight')
		if new_height == last_height:
			break
		last_height = new_height
		counter += 1


def loadImageFromUrl(imageUrl, showImage=False):
	'''
	given an url it load the image ready to be used by openCV
	based on https://prateekvjoshi.com/2016/03/01/how-to-read-an-image-from-a-url-in-opencv-python/
	'''
	#get the url response
	urlResponse = urllib.request.urlopen(imageUrl)
	#convert it to an array
	imgArray = np.array(bytearray(urlResponse.read()), dtype=np.uint8)
	#decode the image
	img = cv2.imdecode(imgArray, -1)
	#show the image
	if showImage != False:
		cv2.imshow('URL Image', img)
		cv2.waitKey()
	return img


def detectFaces(imageUrl, showImage=False):
	'''
	uses opencv to recognize faces
	based on https://realpython.com/face-recognition-with-python/
	'''
	#Create the haar cascade
	faceCascade = cv2.CascadeClassifier('./faceDetection/haarcascade_frontalface_default.xml')
	#Read the image
	image = loadImageFromUrl(imageUrl)
	#transform the image to greyscale so openCv can work on it
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#Detect faces in the image by loading the face cascade to memory and processing the image
	faces = faceCascade.detectMultiScale(
		gray,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(30, 30),
		flags = cv2.CASCADE_SCALE_IMAGE) #faces is a list of rectangles in which it believes it found a face, each rectangle is 4 values: the x and y location of the rectangle, and the rectangle’s width and height (w , h)
	#show the image
	if showImage != False:
		for (x, y, w, h) in faces:
			cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
		cv2.imshow('Image with found faces', image)
		cv2.waitKey(0)
	return faces


####################################################################################
#INSTAGRAM SPECIFIC FUNCTIONS
####################################################################################

def posponeNotifications(driver):
	'''
	if it finds a notifications button, it clicks on 'Not Now'
	'''
	try:
		time.sleep(random.uniform(3.1, 4.4))
		#driver.find_element_by_xpath('//body/div[2]/div/div/div/div[3]/button[2]').click()
		driver.find_element_by_xpath('//body/div[3]/div/div/div/div[3]/button[2]').click()
	except Exception:
		pass


def instagramSearch(driver, hashtagWord):
	'''
	make a search in the instagram search page
	'''
	if hashtagWord[0] == u'#':
		hashtagWord = hashtagWord[1:]
	#get to the search page
	driver.get('https://www.instagram.com/explore/')
	#handle the search bar
	searchBar = driver.find_element_by_xpath('//nav/div[2]/div/div/div[2]/input')
	searchBar.send_keys(u'#{0}'.format(hashtagWord))
	time.sleep(random.uniform(0.6, 1.0))
	searchBar.send_keys(Keys.RETURN)
	searchBar.send_keys(Keys.RETURN)
	time.sleep(random.uniform(1.9, 2.4))
	driver.refresh()
	return driver


def popularRandomInstagramSearch(driver):
	'''
	searches for random hashtags bot only if they have more than 100 posts
	'''
	natureHashtagList = list(getCategorySpecificHashtagList(u'nature'))
	hashtagWord = natureHashtagList[random.randint(0, len(natureHashtagList))]
	#make a search in instagram
	driver = instagramSearch(driver, hashtagWord)
	#if there are no posts for the hashtag, start over
	try:
		nbOfPosts = int((driver.find_element_by_xpath('//header/div[2]/div[2]/span/span').text).replace(u',', u''))
		if nbOfPosts < 100:
			return popularRandomInstagramSearch(driver)
	except NoSuchElementException:
		return popularRandomInstagramSearch(driver)
	return driver, hashtagWord


def clickHeartIfEmpty(driver, xpathToHeart, totalLikes=0):
	'''
	looks if the heart isempty, if it is, it clicks (likes) if not, nothing happens
	it returns the total of likes, in case we need to limit thelikes ot a certain number
	'''
	try:
		heart = driver.find_element_by_xpath(xpathToHeart)
		typeOfHeart = driver.find_element_by_xpath('{0}/span'.format(xpathToHeart))
		#we only like if the heart is empty
		if u'outline' in typeOfHeart.get_attribute('class'):
			heart.click()
			#one more like
			totalLikes += 1
			time.sleep(random.uniform(0.8, 1.3))
	except Exception:
		pass
	return totalLikes


def getLikeScore(driver, xpathToLikeScore):
	'''
	given the xpath to the like score element,
	returns the likeScore as an integer
	'''
	likeScore = driver.find_element_by_xpath(xpathToLikeScore)
	likeScore = (likeScore.text).replace('likes', '').replace('like', '')
	likeScore = (likeScore.replace('views', '')).replace('view', '')
	likeScore = (likeScore.lower()).replace(u',', u'').replace(u'.', u'').replace(u'm', u'').replace(u' ', u'')
	if likeScore == 'like this':
		likeScore = False 
	return int(likeScore)


####################################################################################
#INSTABOT FUNCTIONS
####################################################################################

def logInInstagram(driver, instagramUsername, instagramPassword):
	'''
	opens the login page of instagram and logs in
	'''
	driver.get('https://www.instagram.com/accounts/login/')
	time.sleep(random.uniform(1.1, 3.1))
	#username
	userName = driver.find_element_by_xpath('//article/div/div/div/form/div/div/div/input')
	userName.send_keys(instagramUsername)
	#password
	password = driver.find_element_by_xpath('//article/div/div/div/form/div[2]/div/div/input') 
	password.send_keys(instagramPassword)
	#find element
	driver.find_element_by_xpath('//article/div/div/div/form/div[3]/button').click()
	return driver

def likePicsYouFollow(driver, likeLimit=random.randint(7, 41), goToHomePage=False):
	'''
	from your home page, start liking the 
	pictures proposed by instagram
	'''
	totalLikes = 0
	nextLike = 1
	#leave the page you're in and go to home page
	if goToHomePage != True:
		driver.get('https://www.instagram.com')
	#scroll down for the first page
	scrollPageWithInfiniteLoading(driver, limit=2)
	while totalLikes <= likeLimit:
		posts = driver.find_elements_by_xpath('//main/section/div/div/div/article'.format(nextLike))
		#start liking the first n pictures proposed
		for nextLike in range(1, len(posts)):
			totalLikes = clickHeartIfEmpty(driver, '//main/section/div/div/div/article[{0}]/div[2]/section[1]/span[1]/button'.format(nextLike), totalLikes)
		#scroll down every few pictures
		scrollPageWithInfiniteLoading(driver, limit=1)
		#	nextLike = 0
		time.sleep(random.uniform(0.8, 1.3))
	return driver


def likeRandomPics(driver, likeLimit=random.randint(850, 1045), hashtagWord=None, maxLikeScore=None):
	'''
	makes a search and starts liking pics with the searched tag
	'''
	#make a search in instagram with random hashtags
	if hashtagWord == None:
		driver, hashtagWord = popularRandomInstagramSearch(driver)
	#make a search in instagram
	else:
		driver = instagramSearch(driver, hashtagWord)	
	#select all first appearing pictures
	picturesLink = driver.find_elements_by_class_name('eLAPa')
	#click on the first picture
	action = webdriver.common.action_chains.ActionChains(driver)
	action.move_to_element_with_offset(picturesLink[0], 5, 6) #move cursor to 5 pixels down the top left corner and 6 pixels to the right of the top left corner
	action.click()
	action.perform()
	#click pass the most popular pictures to the most recent pictures
	nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a')#click past the first popular picture
	nextPic.click()
	time.sleep(random.uniform(0.8, 1.5))
	#the xpath of the next button changes after the first picture
	for i in range(8):
		nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a[2]')
		nextPic.click()
		time.sleep(random.uniform(0.8, 1.5))
	#start liking 
	totalLikes = 0
	while totalLikes < likeLimit:
		#we like exclusively the pictures having a low like score (unless we give no max like score limit)
		try:
			likeScore = getLikeScore(driver, '//article/div[2]/section[2]/div/div/button')#for pictures
		except NoSuchElementException:
			likeScore = getLikeScore(driver, '//article/div[2]/section[2]/div/span')#for videos
		if maxLikeScore == None or likeScore < maxLikeScore:
			#like
			totalLikes = clickHeartIfEmpty(driver, '//article/div[2]/section[1]/span[1]/button', totalLikes)
		#click next
		nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a[2]')
		nextPic.click()
		time.sleep(random.uniform(0.8, 2.8))
	return driver


def likeRandomPicsInOneProfile(instagramUsername, instagramPassword, profileHandleToLike, driver=None, likeLimit=random.randint(4, 24), followProfile=True):
	'''given a profile handle, it randomly likes some of the pictures'''

	#open a new browser window
	if driver == None:
		handleDriver = webdriver.Firefox()
	else: handleDriver = driver
	#make sure we have the profile url, not only the profile name
	if u'www.instagram.com' not in profileHandleToLike:
		profileHandleToLike = profileHandleToLike.replace(u'@', u'').replace(u'/', u'').replace(u' ', u'_')
		profileHandleToLike = u'https://www.instagram.com/{0}/'.format(profileHandleToLike)
	#log to instagram
	driver = logInInstagram(handleDriver, instagramUsername, instagramPassword)
	time.sleep(random.uniform(0.5, 0.9))
	#open the profile page
	handleDriver.get(profileHandleToLike)
	#get a popularity score (nb of followers / (followers+following+posts) )
	posts = int( ((handleDriver.find_element_by_xpath('//header/section/ul/li[1]/span/span').text).replace(u'posts', u'')).replace(u'post', u'').replace(u',', u'') )
	followers = int( ((handleDriver.find_element_by_xpath('//header/section/ul/li[2]/a/span').text).replace(u'followers', u'')).replace(u'follower', u'').replace(u',', u'') )
	following = int( ((handleDriver.find_element_by_xpath('//header/section/ul/li[3]/a/span').text).replace(u' following', u'')).replace(u',', u'') )
	popularityScore = float(followers) / float(followers+following+posts)
	#click on the first picture
	action = webdriver.common.action_chains.ActionChains(handleDriver)
	action.move_to_element_with_offset(handleDriver.find_element_by_class_name('eLAPa'), 5, 6) #move cursor to 5 pixels down the top left corner and 6 pixels to the right of the top left corner
	action.click()
	action.perform()
	#like the first picture
	totalLikes = clickHeartIfEmpty(handleDriver, '//article/div[2]/section[1]/span[1]/button', totalLikes=0)
	#click to the next picture
	nextPic = handleDriver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a')#click past the first popular picture
	nextPic.click()
	time.sleep(random.uniform(0.8, 1.5))
	#click and like randomly (2/3 of the pics) until we get to the like limit, the xpath of the next button changes after the first picture
	while totalLikes < likeLimit:
		#only like 2/3 of the pictures, not all of them
		if random.randint(0,2) != 0:
			totalLikes = clickHeartIfEmpty(handleDriver, '//article/div[2]/section[1]/span[1]/button', totalLikes)
		#go to the next picture
		try:
			nextPic = handleDriver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a[2]')
			nextPic.click()
			###time.sleep(random.uniform(0.8, 1.5))
		#if there are no more pictures, stop the loop
		except NoSuchElementException: break
	#lastly, we follow the profile (if specified) to show involvement
	if followProfile == True:
		followButton = handleDriver.find_element_by_xpath('//header/div[2]/div[1]/div[2]/button')
		#if we don't follow them already
		if u'following' not in (followButton.text).lower():
			followButton.click()
			#dump the info in a csv File
			line = u'{0}\t{1}\t{2}\t{3}\t{4}'.format(instagramUsername, profileHandleToLike, popularityScore, str(datetime.datetime.today()).split()[0], str(datetime.datetime.today()).split()[1])
			utilsOs.dumpOneLineToExistingFile(line, u'./profilesBotFollowedBy{0}.csv'.format(instagramUsername), addNewline=True, headerLine=u'userName\thandleFollowed\tpopularityScore\tdate\ttime')
	#close the image
	exitButton = handleDriver.find_element_by_xpath('//body/div[3]/div/button')
	exitButton.click()
	#close the browser window
	handleDriver.close()
	return 


def likeAndCommentRandomPics(driver, likeLimit=random.randint(850, 1045), hashtagWord=None, personalUserInfo=None):
	'''
	makes a search and starts liking pics with the searched tag
	'''
	#make a search in instagram with random hashtags
	if hashtagWord == None:
		driver, hashtagWord = popularRandomInstagramSearch(driver)
	#make a search in instagram
	else:
		driver = instagramSearch(driver, hashtagWord)
	#click on the first picture
	action = webdriver.common.action_chains.ActionChains(driver)
	action.move_to_element_with_offset(driver.find_element_by_class_name('eLAPa'), 5, 6) #move cursor to 5 pixels down the top left corner and 6 pixels to the right of the top left corner
	action.click()
	action.perform()
	#click pass the most popular pictures to the most recent pictures
	nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a')#click past the first popular picture
	nextPic.click()
	time.sleep(random.uniform(0.8, 1.5))
	#click past the popular pictures, the xpath of the next button changes after the first picture
	for i in range(8):
		nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a[2]')
		nextPic.click()
		time.sleep(random.uniform(0.8, 1.5))
	#start liking and commenting
	totalLikes = 0
	while totalLikes < likeLimit:
		#like it
		totalLikes = clickHeartIfEmpty(driver, '//article/div[2]/section[1]/span[1]/button', totalLikes)
		#get image url and image content description
		try:
			imageElement = driver.find_element_by_xpath('//article/div[1]/div/div/div[1]/img')
			imageUrl = imageElement.get_attribute('src')
			#we only comment on pictures containing no persons
			imageContent = ( imageElement.get_attribute('alt').replace('Image may contain: ', '') ).split(', ')
			if u'person' not in u' '.join(imageContent):
				#comment it 
				comment = makeRandomComment(emojiHashtag=hashtagWord)
				#click on the comment button
				driver.find_element_by_xpath('//article/div[2]/section[1]/span[2]/button').click()
				#get the comment section and comment
				commentSection = driver.find_element_by_xpath('//article/div[2]/section[3]/div/form/textarea') 				
				#time.sleep(random.uniform(1.3, 2.4))
				commentSection.send_keys(comment)
				commentSection.send_keys(Keys.RETURN)
				#like some of the pictures of that profile
				profileHandleToLike = driver.find_element_by_xpath('//article/header/div[2]/div[1]/div[1]/h2/a').get_attribute(u'href')
				if personalUserInfo != None:
					emptyElem = likeRandomPicsInOneProfile(personalUserInfo[0], personalUserInfo[1], profileHandleToLike, driver=None, likeLimit=random.randint(4, 24), followProfile=True)
		#pass on the element if it's a video instead of a picture
		except NoSuchElementException: pass
		#click next
		nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a[2]')
		nextPic.click()
		time.sleep(random.uniform(0.8, 2.8))
	return
	

def oneHourOnAutoPilot(driver, instagramUsername, instagramPassword):
	'''
	likes, comments and follows for at least one hour
	'''
	actualTime = 0.0
	#get the starting time
	startTime = str(datetime.datetime.today()).split()[1].split(u':')
	startTime = float(u'{0}.{1}'.format(startTime[0], startTime[1]))
	#first like the pictures followed
	###likePicsYouFollow(driver)
	#verify that one hour has not passed yet
	while actualTime < (startTime+1.0):
		###likeRandomPics(driver, likeLimit=random.randint(12, 21), hashtagWord=None)
		likeAndCommentRandomPics(driver, likeLimit=random.randint(21, 52), hashtagWord=None, personalUserInfo=[instagramUsername, instagramPassword])
		#get actual time before potentially starting over
		actualTime = str(datetime.datetime.today()).split()[1].split(u':')
		actualTime = float(u'{0}.{1}'.format(actualTime[0], actualTime[1]))



####################################################################################
#COMMANDS
####################################################################################

#open the browser window
instagramUsername = 'the_vegetal_picture'
instagramPassword = 'N0recuerd0'

driver = webdriver.Firefox()
#log to instagram
logInInstagram(driver, instagramUsername, instagramPassword)
posponeNotifications(driver)
time.sleep(1.0)
####likePicsYouFollow(driver)
####likeRandomPics(driver, likeLimit=5, hashtagWord=None)
####likeAndCommentRandomPics(driver, likeLimit=5, hashtagWord=None, personalUserInfo=[instagramUsername, instagramPassword])
oneHourOnAutoPilot(driver, instagramUsername, instagramPassword)


#close the browser window
###driver.close()