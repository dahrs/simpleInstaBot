#!/usr/bin/python
#-*- coding:utf-8 -*-


import time, random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


####################################################################################
#INSTAGRAM SPECIFIC FUNCTIONS
####################################################################################

def logInInstagram(driver, instagramUsername, instagramPassword):
	'''
	opens the login page of instagram and logs in
	'''
	driver.get('https://www.instagram.com/accounts/login/')
	time.sleep(random.uniform(0.8, 3.1))
	#username
	userName = driver.find_element_by_xpath('//article/div/div/div/form/div/div/div/input')
	userName.send_keys(instagramUsername)
	#password
	password = driver.find_element_by_xpath('//article/div/div/div/form/div[2]/div/div/input') 
	password.send_keys(instagramPassword)
	#find element
	driver.find_element_by_xpath('//article/div/div/div/form/div[3]/button').click()


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


def getLikeScore(driver, xpathToLikeScore):
	'''
	given the xpath to the like score element,
	returns the likeScore as an integer
	'''
	likeScore = driver.find_element_by_xpath(xpathToLikeScore)
	likeScore = (likeScore.text).replace(' likes', '')
	likeScore = (likeScore).replace(' like', '')
	if likeScore == 'like this':
		likeScore = False 
	return int(likeScore)


def likeRandomPics(driver, likeLimit=random.randint(850, 1045), hashtagWord=None, maxLikeScore=None):
	'''
	makes a search and starts liking pics with the searched tag
	'''
	if hashtagWord == None:
		hashtagWord = u'flower'
	#get to the search page
	driver.get('https://www.instagram.com/explore/')
	#handle the search bar
	searchBar = driver.find_element_by_xpath('//nav/div[2]/div/div/div[2]/input')
	searchBar.send_keys(u'#{0}'.format(hashtagWord))
	time.sleep(random.uniform(0.4, 0.8))
	searchBar.send_keys(Keys.RETURN)
	searchBar.send_keys(Keys.RETURN)
	time.sleep(random.uniform(1.9, 2.4))
	driver.refresh()	
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
		likeScore = getLikeScore(driver, '/html/body/div[3]/div/div[2]/div/article/div[2]/section[2]/div/div/button')
		if maxLikeScore == None or likeScore < maxLikeScore:
			#like
			totalLikes = clickHeartIfEmpty(driver, '//article/div[2]/section[1]/span[1]/button', totalLikes)
		#click next
		nextPic = driver.find_element_by_xpath('//body/div[3]/div/div[1]/div/div/a[2]')
		nextPic.click()
		time.sleep(random.uniform(0.8, 2.8))


def likeAndComment():
	''''''

#open the browser window
driver = webdriver.Firefox()
instagramUsername = 'the_vegetal_picture'
instagramPassword = 'N0recuerd0'
#log to instagram
logInInstagram(driver, instagramUsername, instagramPassword)
posponeNotifications(driver)
time.sleep(1.0)
####likePicsYouFollow(driver)
likeRandomPics(driver, likeLimit=5, hashtagWord=None)

#close the browser window
###driver.close()