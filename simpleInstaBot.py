#!/usr/bin/python
#-*- coding:utf-8 -*-


import utilsOs
import time, calendar, random, cv2, urllib.request, re
import numpy as np
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException, MoveTargetOutOfBoundsException




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
	epithet = [u'Nice', u'Good', u'Cool', u'Awesome', u'Pretty nice', u'Pretty good', u'Pretty awesome']
	nominal = [u'', u'', u' one', u' one', u' pic', u' pic', u' picture', u' picture', u' photo', u' photo', u' post', u' profile', u' account']
	punctuation = [u'', u'!']
	comment = u'{0}{1}{2}'.format(epithet[random.randint(0, len(epithet)-1)], nominal[random.randint(0, len(nominal)-1)], punctuation[random.randint(0, len(punctuation)-1)])
	#if there is an emoji hashtag, wee add it to the comment
	if emojiHashtag != None:
		emojiHashtagDict = utilsOs.openJsonFileAsDict(emojiHashtagDictPath)
		#if the emoji hashtag is in the dict
		if emojiHashtag in emojiHashtagDict:
			emojiList = emojiHashtagDict[emojiHashtag]
			#if there are multiple possible emojis, choose one at random
			if len(emojiList) != 1:
				emoji = emojiList[random.randint(0, len(emojiList)-1)]
			#if there is only one possible emoji, capture it
			else: emoji = emojiList[0]
			#add emoji to comment
			comment = u'{0} {1}{2}'.format(comment.replace(u'!', u''), emoji, punctuation[random.randint(0, len(punctuation)-1)])
	return comment


def addMonthsToDate(stringDate, months=1):
	sourcedate = datetime.strptime(stringDate, '%Y-%m-%d')
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return datetime(year,month,day)


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

def getNextPic(driver):
	''' gets the next picture when the picture is opened in the browser'''
	i = 1
	for n in reversed(range(4)):
		try:
			#click past the first popular picture
			nextPic = driver.find_element_by_xpath(u'//body/div[{0}]/div[1]/div/div/a[2]'.format(n)) #'//body/div[{0}]/div/div[1]/div/div/a[2]'
			if nextPic.text == u'Next':
				return nextPic
		except NoSuchElementException:
			#if there is no previous pic only next pic
			try:
				#click past the first popular picture
				nextPic = driver.find_element_by_xpath(u'//body/div[{0}]/div[1]/div/div/a'.format(n)) #'//body/div[{0}]/div/div[1]/div/div/a'
				if nextPic.text == u'Next':
					return nextPic
			except NoSuchElementException: pass
	return None


def getExitButton(driver):
	''' gets the exit button when the picture is opened in the browser'''
	i = 1
	for n in reversed(range(4)):
		try:
			exitButton = driver.find_element_by_xpath('//body/div[{0}]/div/button'.format(n))
			if u'Close' in exitButton.text:		
				return exitButton
		except NoSuchElementException:
			pass
	for n in reversed(range(4)):
		for nb in reversed(range(4)):
			try:
				exitButton = driver.find_element_by_xpath('//body/div[{0}]/div/button[{1}]'.format(n, nb))
				if u'Close' in exitButton.text:
					return exitButton
			except NoSuchElementException:
				try:
					exitButton = driver.find_element_by_xpath('//body/div[{0}]/button[{1}]'.format(n, nb))
					if u'Close' in exitButton.text:
						return exitButton
				except NoSuchElementException:
					pass
				pass


def logInInstagram(logDriver, instagramUsername, instagramPassword):
	'''
	opens the login page of instagram and logs in
	'''
	logDriver.get(u'https://www.instagram.com/accounts/login/')
	time.sleep(random.uniform(1.7, 2.7))
	#username
	userName = logDriver.find_element_by_name(u"username")
	#password
	password = logDriver.find_element_by_name(u"password")
	#actions
	userName.send_keys(instagramUsername)
	time.sleep(random.uniform(1.8, 3.4))
	password.send_keys(instagramPassword)
	time.sleep(random.uniform(1.1, 3.0))
	#find element
	for nb in range(1, 10):
		try:
			logInButtonLabel = logDriver.find_element_by_xpath(u'//article/div/div[1]/div/form/div[{0}]/button/div'.format(nb)).text.lower()
			if logInButtonLabel == u'log in':
				logInButton = logDriver.find_element_by_xpath(u'//article/div/div[1]/div/form/div[{0}]/button'.format(nb))
				logInButton.click()
				break
		except NoSuchElementException: pass
	return logDriver


def posponeNotifications(notifDriver):
	'''
	if it finds a notifications button, it clicks on 'Not Now'
	'''
	for n in reversed(range(4)):
		try:
			time.sleep(random.uniform(2.1, 3.4))
			#driver.find_element_by_xpath('//body/div[2]/div/div/div/div[3]/button[2]').click()
			notifDriver.find_element_by_xpath('//body/div[{0}]/div/div/div/div[3]/button[2]'.format(n)).click()
			break
		except NoSuchElementException:
			try:
				notifDriver.find_element_by_xpath('//body/div[{0}]/div/div/div[3]/button[2]'.format(n)).click()
				break
			except NoSuchElementException:
				pass
	return notifDriver


def likeAndReplyToComments(driver, instagramUsername):
	'''
	goes through my posts, detect the new comments, likes and replies to them
	'''
	#get to the profile page
	driver.get('https://www.instagram.com/{0}/'.format(instagramUsername))
	#scroll to first image
	driver, picturesList = scrollToFirstImage(driver)
	#click on the first image
	driver, picturesList = clickOnFirstImage(driver, picturesList)
	######################################################
	#find number of comments, identify origin of comments, like, comment and thank


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
	time.sleep(random.uniform(1.1, 1.9))
	searchBar.send_keys(Keys.RETURN)
	searchBar.send_keys(Keys.RETURN)
	time.sleep(random.uniform(2.8, 4.4))
	driver.refresh()
	return driver


def popularRandomInstagramSearch(driver, domainHashtag=None):
	'''
	searches for random hashtags bot only if they have more than 100 posts
	'''
	domainHashtag = domainHashtag if domainHashtag != None else 'nature'
	natureHashtagList = list(getCategorySpecificHashtagList(domainHashtag))
	hashtagWord = natureHashtagList[random.randint(0, len(natureHashtagList)-1)]
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
			time.sleep(random.uniform(0.4, 0.9))
			heart.click()
			#one more like
			totalLikes += 1
			time.sleep(random.uniform(0.8, 1.3))
	except Exception:
		pass
	return totalLikes


def commentIfAvailable(driver, comment):
	''' find the comment button if we canm we make a comment '''
	#if there is a comment button (sometimes deactivated)
	buttonType = driver.find_element_by_xpath('//article/div[2]/section[1]/span[2]/button/span')
	if buttonType.get_attribute(u'aria-label') == u'Comment':
		#click on the comment button
		driver.find_element_by_xpath('//article/div[2]/section[1]/span[2]/button').click()
		#get the comment section and comment
		commentSection = driver.find_element_by_xpath('//article/div[2]/section[3]/div/form/textarea') 				
		time.sleep(random.uniform(0.6, 1.1))
		commentSection.send_keys(comment)
		time.sleep(random.uniform(0.3, 0.7)*len(comment))
		commentSection.send_keys(Keys.RETURN)
		commentSection.send_keys(Keys.RETURN)
	return driver


def clickHeartIfEmptyAndCommentSparsely(driver, xpathToHeart, totalLikes=0, emojiCharDictPath=u'./emojiDict/emojiNameDict.json'):
	'''
	looks if the heart isempty, if it is, it clicks (likes) if not, nothing happens
	it returns the total of likes, in case we need to limit thelikes ot a certain number
	'''
	#get the emoji dict
	emojiNameDict = utilsOs.openJsonFileAsDict(emojiCharDictPath)
	#like the empty heart
	try:
		heart = driver.find_element_by_xpath(xpathToHeart)
	except NoSuchElementException:
		return totalLikes
	typeOfHeart = driver.find_element_by_xpath('{0}/span'.format(xpathToHeart))
	#we only like if the heart is empty
	if u'outline' in typeOfHeart.get_attribute('class'):
		time.sleep(random.uniform(0.4, 0.9))
		heart.click()
		#one more like
		totalLikes += 1
		#comment 1/3 of the liked
		if random.randint(0, 2) == 0:
			#look if one of the emoji key words appear in the picture description
			description = driver.find_element_by_xpath(u'//article/div[2]/div[1]/ul/li[1]/div/div/div/span').text.lower()
			for emojiKeyword, emojiList in emojiNameDict.items():
				#get the comment
				listOfComments = [u'{0}{0}{0}'.format(emojiList[0]), u'{0}'.format(emojiList[0]), u'{0}!'.format(emojiList[0]), u'😮{0}'.format(emojiList[0]), u'😮, {0}'.format(emojiList[0]), u'👍{0}'.format(emojiList[0]), u'👌{0}'.format(emojiList[0]), u'🙃{0}'.format(emojiList[0])]
				comment = listOfComments[ random.randint(0, len(listOfComments)-1) ]
				#match to unwanted words
				badEmoji = re.findall(r'angry|frown|sad|sob|confound|quiver|pouting|pain', emojiKeyword) 
				#if we find a match
				try:
					if emojiKeyword in description and len(emojiKeyword) > 4 and len(badEmoji) == 0:
						time.sleep(random.uniform(0.9, 1.3))
						#comment using the emoji
						driver = commentIfAvailable(driver, comment)
						time.sleep(random.uniform(3.1, 4.5))
						return totalLikes
				except StaleElementReferenceException: 
					pass
	return totalLikes


def getNbFromInstagramElement(textContent):
	''' given an insta text content, takes only the numbers'''
	textContent = textContent.lower()
	textContent = ( textContent.replace(u'likes', u'') ).replace(u'like', u'')
	textContent = ( textContent.replace(u'views', u'') ).replace(u'view', u'')
	textContent = ( textContent.replace(u'posts', u'') ).replace(u'post', u'')
	textContent = ( textContent.replace(u'followers', u'') ).replace(u'follower', u'')
	textContent = ( textContent.replace(u'following', u'') ).replace(u',', u'')
	textContent = ( textContent.replace(u'others', u'') ).replace(u'other', u'')
	if u'k' in textContent:
		textContent = ( textContent.replace(u'k', u'00') ).replace(u'.', u'')
	if u'm' in textContent:
		textContent = ( textContent.replace(u'k', u'00000') ).replace(u'.', u'')
	if textContent == ' this':
		textContent = 0 
	return int(textContent)


def subscribe(profileDriver, instagramUsername=None, instagramPassword=None, outputFilePath=None):
	''' follows a profile, given an instagram driver or profile url '''
	if type(profileDriver) is str:
		#get the url
		profileUrl = profileDriver
		#open a new browser window
		profileDriver = webdriver.Firefox()
		#make sure we have the profile url, not only the profile name
		if u'www.instagram.com' not in profileUrl:
			profileUrl = profileUrl.replace(u'@', u'').replace(u'/', u'').replace(u' ', u'_')
			profileUrl = u'https://www.instagram.com/{0}/'.format(profileUrl)
		#log to instagram
		if instagramUsername != None and instagramPassword != None:
			profileDriver = logInInstagram(handleDriver, instagramUsername, instagramPassword)
			profileDriver = posponeNotifications(handleDriver)
		time.sleep(random.uniform(0.8, 1.3))
		#open the profile page
		profileDriver.get(profileUrl)
	#get a popularity score (nb of followers / (followers+following+posts) )
	posts = int( getNbFromInstagramElement(handleDriver.find_element_by_xpath('//header/section/ul/li[1]/span/span').text) )
	followers = int( getNbFromInstagramElement(handleDriver.find_element_by_xpath('//header/section/ul/li[2]/a/span').text) )
	following = int( getNbFromInstagramElement(handleDriver.find_element_by_xpath('//header/section/ul/li[3]/a/span').text) )
	popularityScore = float(followers) / float(followers+following+posts)
	#get follow/unfollow button
	try:
		followButton = profileDriver.find_element_by_xpath('//header/section/div[1]/button')
	except NoSuchElementException:
		try:
			followButton = profileDriver.find_element_by_xpath('//header/section/div[1]/span/span[1]/button')
		except NoSuchElementException:
			followButton = profileDriver.find_element_by_xpath('//header/div[2]/div[1]/div[2]/button')
	#if we don't follow them already
	if u'following' not in (followButton.text).lower():
		followButton.click()
		#dump the info in a csv File
		if outputFilePath != None:
			line = u'{0}\t{1}\t{2}\t{3}\t{4}'.format(instagramUsername, profileHandleToLike, popularityScore, str(datetime.today()).split()[0], str(datetime.today()).split()[1])
			utilsOs.dumpOneLineToExistingFile(line, outputFilePath, addNewline=True, headerLine=u'userName\thandleFollowed\tpopularityScore\tdate\ttime')
	return profileDriver


def unsubscribe(profileUrl, profileDriver=None, instagramUsername=None, instagramPassword=None, outputFilePath=None, closeAfterwards=True):
	''' unfollows a profile, given an instagram driver or profile url '''
	#make sure we have the profile url, not only the profile name
	if u'www.instagram.com' not in profileUrl:
		profileUrl = profileUrl.replace(u'@', u'').replace(u'/', u'').replace(u' ', u'_')
		profileUrl = u'https://www.instagram.com/{0}/'.format(profileUrl)
	#following
	if profileDriver == None:
		#open a new browser window
		profileDriver = webdriver.Firefox()
		#log to instagram if needed
		if instagramUsername != None and instagramPassword != None:
			profileDriver = logInInstagram(profileDriver, instagramUsername, instagramPassword)
			profileDriver = posponeNotifications(profileDriver)
	time.sleep(random.uniform(1.6, 2.0))
	#open the profile page
	profileDriver.get(profileUrl)
	#get follow/unfollow button
	try:
		#select follow button
		try:
			followButton = profileDriver.find_element_by_xpath('//header/section/div[1]/span/span[1]/button')
		except NoSuchElementException:
			followButton = profileDriver.find_element_by_xpath('//header/section/div[1]/button')
		#if we don't follow them already
		if u'following' in (followButton.text).lower():
			followButton.click()
			#the stand of this button changes sometimes, so we adapt
			for nb in reversed(range(7)): #change the number of times the div element appears
				for n in reversed(range(10)): #change the number of element in the first div element
					try:
						verificationFollowButton = profileDriver.find_element_by_xpath('//body/div[{0}]/{1}div[3]/button[1]'.format(n, 'div/'*nb)) 
						#'//body/div[2]/div/div/div/div[3]/button[1]' #''//body/div[2]/div/div/div[3]/button[1]'' #'//body/div[3]/div/div/div[3]/button[1]'
					except NoSuchElementException:
						pass
			time.sleep(random.uniform(0.4, 1.0))
			verificationFollowButton.click()		
			time.sleep(random.uniform(0.7, 0.9))
	except NoSuchElementException:
		#if instagram excuses itself the profile was probably erased, if not, we got to see what hapens so we raise the same exception
		if u'Sorry' not in profileDriver.find_element_by_xpath('//body/div/div[1]/div/div/h2').text:
			raise NoSuchElementException
	#remove row from the csv File if we successfully unfollowed or if the profile doesn't exist anymore
	if outputFilePath != None:
		#get df
		followingDf = pd.read_csv(outputFilePath, sep=u'\t')
		#get rid of the row
		followingDf = followingDf.loc[~followingDf[u'handleFollowed'].isin([profileUrl])]
		#dump to file
		followingDf.to_csv(outputFilePath, sep='\t', index=False)
	#either close the browser or return the browser handle
	if closeAfterwards == True:
		profileDriver.close()
	else:
		return profileDriver


def unsubscribeAfterOneMonth(instagramUsername, instagramPassword, outputFilePath, profileDriver=None):
	''' unsubscribes one month old profiles '''
	closeAfterwards = True if profileDriver == None else False
	try:
		#get df
		followingDf = pd.read_csv(outputFilePath, sep=u'\t')
	#if there is no file
	except FileNotFoundError:
		return None
	#get list of people to unsubscribe
	tempDf = followingDf
	tempDf[u'date'] = tempDf[u'date'].apply(addMonthsToDate)
	#make df of all elements from one month ago
	tempDf = tempDf.loc[tempDf[u'date'] < pd.Series(datetime.today() for e in range(len(tempDf)))]
	#make a list of the urls to unsubscribe
	urlsToUnfollow = tempDf[u'handleFollowed'].tolist()
	#go online and actually unsubscribe
	for index, url in enumerate(urlsToUnfollow):
		#unsubscribe (it will also remove the row from the tsv list one by onem after being sure we unsubscribed without any problem)
		if profileDriver == None:
			profileDriver = unsubscribe(url, profileDriver, instagramUsername, instagramPassword, outputFilePath, closeAfterwards=False)
		else:
			#do not close the profile drive if it's not the last
			if index+1 < len(urlsToUnfollow):
				profileDriver = unsubscribe(url, profileDriver, instagramUsername, instagramPassword, outputFilePath, closeAfterwards=False)
			#close if it's the last
			else:
				profileDriver = unsubscribe(url, profileDriver, instagramUsername, instagramPassword, outputFilePath, closeAfterwards=closeAfterwards)
	if closeAfterwards == True:
		profileDriver.close()
	else:
		return profileDriver


def scrollToFirstImage(driver, picturesList=None):
	''' based on the window heigh and the place of the 
	first image, scroll till the first image is visible'''
	if picturesList == None:
		picturesList = driver.find_elements_by_class_name('eLAPa')
	#scroll a little to see the images
	time.sleep(random.uniform(0.5, 0.8))
	imageVerticalLocation = (picturesList[0].location)[u'y']
	#image location
	if imageVerticalLocation < 405:
		pass
	elif imageVerticalLocation <= 450:	
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight/10);')
	elif imageVerticalLocation <= 700:
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight/8);')
	else:
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight/4);')
	time.sleep(random.uniform(0.3, 0.5))
	return driver, picturesList


def clickOnFirstImage(driver, picturesList=None):
	''' clicks ont the first picture of the list'''
	if picturesList == None:
		#list all pictures
		picturesList = handleDriver.find_elements_by_class_name('eLAPa')
	#move mouse to the first image and click
	action = webdriver.common.action_chains.ActionChains(driver)
	action.move_to_element_with_offset(picturesList[0], 120, 6) #move cursor to 5 pixels down the top left corner and 6 pixels to the right of the top left corner
	action.click()
	action.perform()
	time.sleep(random.uniform(0.9, 1.3))
	return driver, picturesList


####################################################################################
#INSTABOT FUNCTIONS
####################################################################################

def thank4Comments():
	''' from home page, looks at the comments in 
	profile's pictures and thanks for them '''


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


def likeRandomPics(driver, likeLimit=random.randint(850, 1045), hashtagWord=None, maxLikeScore=None, popularPicsHahstags=[]):
	'''
	makes a search and starts liking pics with the searched tag
	'''
	#make a search in instagram with random hashtags
	if hashtagWord == None:
		domainHashtag = [hashtag.replace('#', '') for hashtag in popularPicsHahstags if hashtag in ['people', 'nature', 'food-drink', 'activity', 'travel-places', 'objects', 'symbols', 'flags']]
		domainHashtag = domainHashtag[0] if len(domainHashtag) != 0 else 'nature'
		driver, hashtagWord = popularRandomInstagramSearch(driver, domainHashtag)
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
	time.sleep(random.uniform(0.7, 1.1))
	#click pass the most popular pictures to the most recent pictures
	nextPic = getNextPic(driver) #click past the first popular picture
	#if there is a next picture
	if nextPic != None:
		nextPic.click()
		time.sleep(random.uniform(0.8, 1.5))
		#the xpath of the next button changes after the first picture
		for i in range(8):
			nextPic = getNextPic(driver)
			#get a list of hashtags from the popular pictures
			try:
				picDescription = driver.find_element_by_xpath('//article/div[2]/div[1]/ul/li/div/div/div[2]/span').text
			except NoSuchElementException:
				picDescription = driver.find_element_by_xpath('//article/div[2]/div[1]/ul/li/div/div/div/span').text
			picDescription = picDescription.replace(u'\n', u' ').replace(u'\r', u' ').replace(u'\t', u' ')
			hashtags = [ tok for tok in picDescription.split(u' ') if tok != '']
			hashtags = [ tok for tok in hashtags if tok[0] == '#' ]
			for hasht in hashtags:
				popularPicsHahstags.append(hasht)
			#if there is a next picture
			if nextPic != None:
				nextPic.click()
				time.sleep(random.uniform(0.8, 1.5))
			else: return driver
		#start liking 
		totalLikes = 0
		while totalLikes < likeLimit:
			#we like exclusively the pictures having a low like score (unless we give no max like score limit)
			try:
				likeScore = getNbFromInstagramElement(driver.find_element_by_xpath(u'//article/div[2]/section[2]/div/div/button').text)#for pictures
			except NoSuchElementException:
				try:
					likeScore = getNbFromInstagramElement(driver.find_element_by_xpath(u'//article/div[2]/section[2]/div/span').text)#for videos
				except NoSuchElementException:
					likeScore = 0
			#if there is somebody we know that already liked the picture
			except ValueError:
				likeScore = getNbFromInstagramElement(driver.find_element_by_xpath(u'//article/div[2]/section[2]/div/div[2]/button').text)#for pictures
			if maxLikeScore == None or likeScore < maxLikeScore:
				#like
				###totalLikes = clickHeartIfEmpty(driver, u'//article/div[2]/section[1]/span[1]/button', totalLikes)
				totalLikes = clickHeartIfEmptyAndCommentSparsely(driver, u'//article/div[2]/section[1]/span[1]/button', totalLikes)
			#click next
			nextPic = getNextPic(driver)
			#if there is a next picture
			if nextPic != None:
				nextPic.click()
				time.sleep(random.uniform(0.9, 1.2))
	return driver, popularPicsHahstags


def likeRandomPicsInOneProfile(instagramUsername, instagramPassword, profileHandleToLike, 
	handleDriver=None, likeLimit=random.randint(8, 24), followProfile=True, closeDriver=True):
	'''given a profile handle, it randomly likes some of the pictures'''
	if handleDriver == None:
		#open a new browser window
		handleDriver = webdriver.Firefox()
		#make sure we have the profile url, not only the profile name
		if u'www.instagram.com' not in profileHandleToLike:
			profileHandleToLike = profileHandleToLike.replace(u'@', u'').replace(u'/', u'').replace(u' ', u'_')
			profileHandleToLike = u'https://www.instagram.com/{0}/'.format(profileHandleToLike)
		#log to instagram
		handleDriver = logInInstagram(handleDriver, instagramUsername, instagramPassword)
		handleDriver = posponeNotifications(handleDriver)
	time.sleep(random.uniform(1.0, 1.5))
	#open the profile page
	handleDriver.get(profileHandleToLike)
	time.sleep(random.uniform(0.9, 1.2))
	#get a popularity score (nb of followers / (followers+following+posts) )
	posts = int( getNbFromInstagramElement(handleDriver.find_element_by_xpath('//header/section/ul/li[1]/span/span').text) )
	followers = int( getNbFromInstagramElement(handleDriver.find_element_by_xpath('//header/section/ul/li[2]/a/span').text) )
	following = int( getNbFromInstagramElement(handleDriver.find_element_by_xpath('//header/section/ul/li[3]/a/span').text) )
	popularityScore = float(followers) / float(followers+following+posts)
	#list all pictures
	picturesList = handleDriver.find_elements_by_class_name('eLAPa')
	#if there are no images immediately available
	if len(picturesList) == 0:
		handleDriver.close()
		return handleDriver
	#scroll a little to see the images
	handleDriver, picturesList = scrollToFirstImage(handleDriver, picturesList)
	try:
		#move mouse to the first image and click
		handleDriver, picturesList = clickOnFirstImage(handleDriver, picturesList)
	#if we overscroll, we close the window because getting it more right is a nightmare
	except MoveTargetOutOfBoundsException:
		#close the browser window
		handleDriver.close()
		return handleDriver
	#like the first picture
	totalLikes = clickHeartIfEmpty(handleDriver, '//article/div[2]/section[1]/span[1]/button', totalLikes=0)
	#click to the next picture
	nextPic = getNextPic(handleDriver)#click past the first popular picture
	#if there is a next picture
	if nextPic != None:
		nextPic.click()
		time.sleep(random.uniform(0.8, 1.3))
		#click and like randomly (2/3 of the pics) until we get to the like limit, the xpath of the next button changes after the first picture
		while totalLikes < likeLimit:
			#only like 2/3 of the pictures, not all of them
			if random.randint(0,2) != 0:
				###totalLikes = clickHeartIfEmpty(handleDriver, u'//article/div[2]/section[1]/span[1]/button', totalLikes)
				totalLikes = clickHeartIfEmptyAndCommentSparsely(handleDriver, u'//article/div[2]/section[1]/span[1]/button', totalLikes)
				time.sleep(random.uniform(0.4, 0.8))
			#go to the next picture
			nextPic = getNextPic(handleDriver)
			#if there is a next picture
			if nextPic != None:
				nextPic.click()
				time.sleep(random.uniform(0.8, 1.5))
			#if there are no more pictures, stop the loop
			totalLikes += 1
		#lastly, we follow the profile (if specified) to show involvement
		if followProfile == True:
			followButton = handleDriver.find_element_by_xpath('//header/div[2]/div[1]/div[2]/button')
			#if we don't follow them already
			if u'following' not in (followButton.text).lower():
				followButton.click()
				#dump the info in a csv File
				line = u'{0}\t{1}\t{2}\t{3}\t{4}'.format(instagramUsername, profileHandleToLike, popularityScore, str(datetime.today()).split()[0], str(datetime.today()).split()[1])
				utilsOs.dumpOneLineToExistingFile(line, u'./profilesBotFollowedBy{0}.tsv'.format(instagramUsername), addNewline=True, headerLine=u'userName\thandleFollowed\tpopularityScore\tdate\ttime')
	#close the image
	exitButton = getExitButton(handleDriver)
	if exitButton != None:
		exitButton.click()
	else:
		handleDriver.close()
		return None
	if closeDriver == True:
		time.sleep(random.uniform(1.0, 2.0))
		handleDriver.close()
		return None
	else: return handleDriver


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
	imageSearchPage = driver.current_url
	#click on the first picture
	action = webdriver.common.action_chains.ActionChains(driver)
	action.move_to_element_with_offset(driver.find_element_by_class_name('eLAPa'), 5, 6) #move cursor to 5 pixels down the top left corner and 6 pixels to the right of the top left corner
	action.click()
	action.perform()
	whereWeLeftOf = 0
	#click pass the most popular pictures to the most recent pictures
	nextPic = getNextPic(driver)
	#if there is a next picture
	if nextPic != None:
		nextPic.click()
		time.sleep(random.uniform(0.7, 1.1))
		#click past the popular pictures, the xpath of the next button changes after the first picture
		for i in range(8):
			nextPic = getNextPic(driver)
			#if there is a next picture
			if nextPic != None:
				nextPic.click()
				whereWeLeftOf += 1
				time.sleep(random.uniform(0.8, 1.5))
			else:
				return driver
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
					#if there is a comment button (sometimes deactivated)
					buttonType = driver.find_element_by_xpath('//article/div[2]/section[1]/span[2]/button/span')
					if buttonType.get_attribute(u'aria-label') == u'Comment':
						#click on the comment button
						driver.find_element_by_xpath('//article/div[2]/section[1]/span[2]/button').click()
						#get the comment section and comment
						commentSection = driver.find_element_by_xpath('//article/div[2]/section[3]/div/form/textarea') 				
						time.sleep(random.uniform(0.6, 1.1))
						commentSection.send_keys(comment)
						time.sleep(random.uniform(0.8, 1.3))
						try:
							commentSection.send_keys(Keys.RETURN)
						except StaleElementReferenceException:
							pass
						#like some of the pictures of that profile
						profileHandleToLike = driver.find_element_by_xpath('//article/header/div[2]/div[1]/div[1]/h2/a').get_attribute(u'href')
						#except if we already follow the profile
						followingStatus = driver.find_element_by_xpath('//header/div[2]/div[1]/div[2]/button').text
						if personalUserInfo != None and u'following' not in followingStatus.lower():
							driver = likeRandomPicsInOneProfile(personalUserInfo[0], personalUserInfo[1], profileHandleToLike, driver, random.randint(4, 24), followProfile=True, closeDriver=False)
							driver.get(imageSearchPage)
							#scroll to first image
							driver, picturesList = scrollToFirstImage(driver)
							#click on the first image
							driver, picturesList = clickOnFirstImage(driver, picturesList)
							#get to the picture where we left of
							for n in range(whereWeLeftOf):
								time.sleep(random.uniform(0.4, 0.9))
								#click next
								nextPic = getNextPic(driver)
								#if there is a next picture
								if nextPic != None:
									nextPic.click()
								else:
									return driver
						time.sleep(random.uniform(0.8, 1.3))
			#pass on the element if it's a video instead of a picture
			except NoSuchElementException:
				pass
			#click next
			nextPic = getNextPic(driver)
			#if there is a next picture
			if nextPic != None:
				nextPic.click()
				whereWeLeftOf += 1
				time.sleep(random.uniform(0.8, 1.3))
	return driver
	

def oneHourOnAutoPilot(driver, instagramUsername, instagramPassword, profilePreferedHashtags):
	'''
	likes, comments and follows for at least one hour
	'''
	actualTime = 0.0
	#get the starting time
	startTime = str(datetime.today()).split()[1].split(u':')
	startTime = float(u'{0}.{1}'.format(startTime[0], startTime[1]))
	#first unsubscribe from profiles after one month
	driver = unsubscribeAfterOneMonth(instagramUsername, instagramPassword, u'./profilesBotFollowedBy{0}.tsv'.format(instagramUsername), driver)
	#get back to the main page
	driver.get(u'https://www.instagram.com/')
	#then like the pictures followed
	driver = likePicsYouFollow(driver, 7) ########################################
	popularPicsHahstags = list(profilePreferedHashtags)
	#verify that one hour has not passed yet
	while actualTime < (startTime+1.0):
		#get a random index to get a random hashtag
		randomIndex = random.randint(0, len(popularPicsHahstags)-1)
		driver, popularPicsHahstags = likeRandomPics(driver, 
			likeLimit=random.randint(12, 21), 
			hashtagWord=popularPicsHahstags[randomIndex], 
			popularPicsHahstags=popularPicsHahstags)
		#delete the hashtag we just used
		del popularPicsHahstags[randomIndex]
		#get a random index to get a random hashtag
		randomIndex = random.randint(0, len(popularPicsHahstags)-1)
		likeAndCommentRandomPics(driver, 
			likeLimit=random.randint(21, 52), 
			hashtagWord=popularPicsHahstags[randomIndex], 
			personalUserInfo=[instagramUsername, instagramPassword])
		#delete the hashtag we just used
		del popularPicsHahstags[randomIndex]
		#get actual time before potentially starting over
		actualTime = str(datetime.today()).split()[1].split(u':')
		actualTime = float(u'{0}.{1}'.format(actualTime[0], actualTime[1]))
	driver.close()


####################################################################################
#COMMANDS
####################################################################################

#open the browser window
myData = utilsOs.openJsonFileAsDict(u'./keyAndPswrd.json') #place username and password in a file called keyAndPswrd.json in the following way: {"profile_name": "password"}

for instagramUsername, instagramData in myData.items():
	instagramPassword = instagramData[0]
	profilePreferedHashtags = instagramData[1]
	print(10000, instagramUsername)
	driver = webdriver.Firefox()
	#log to instagram
	logInInstagram(driver, instagramUsername, instagramPassword)
	posponeNotifications(driver)
	time.sleep(1.0)
	oneHourOnAutoPilot(driver, instagramUsername, instagramPassword, profilePreferedHashtags)