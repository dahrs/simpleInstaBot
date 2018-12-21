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
	last_height = driver.execute_script("return document.body.scrollHeight")
	#loop
	while counter <= limit:
		# Scroll down to bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		# Wait to load page
		time.sleep(random.uniform(0.5, 0.8))
		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")
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
	userName = driver.find_element_by_xpath("//article/div/div/div/form/div/div/div/input")
	userName.send_keys(instagramUsername)
	#password
	password = driver.find_element_by_xpath("//article/div/div/div/form/div[2]/div/div/input") 
	password.send_keys(instagramPassword)
	#find element
	driver.find_element_by_xpath("//article/div/div/div/form/div[3]/button").click()

def posponeNotifications(driver):
	'''
	if it finds a notifications button, it clicks on "Not Now"
	'''
	try:
		time.sleep(random.uniform(3.1, 4.4))
		#driver.find_element_by_xpath("//body/div[2]/div/div/div/div[3]/button[2]").click()
		driver.find_element_by_xpath("//body/div[3]/div/div/div/div[3]/button[2]").click()
	except Exception:
		pass


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
		posts = driver.find_elements_by_xpath("//main/section/div/div/div/article".format(nextLike))
		#star liking the first n pictures proposed
		for nextLike in range(1, len(posts)):
			try:
				heart = driver.find_element_by_xpath("//main/section/div/div/div/article[{0}]/div[2]/section[1]/span[1]/button".format(nextLike))
				typeOfHeart = driver.find_element_by_xpath("//main/section/div/div/div/article[{0}]/div[2]/section[1]/span[1]/button/span".format(nextLike))
				#we only like if the heart is empty
				if u'outline' in typeOfHeart.get_attribute("class"):
					heart.click()
					#one more like
					totalLikes += 1
					time.sleep(random.uniform(0.8, 1.3))
					print(11111, nextLike)
			except Exception:
				pass
		#scroll down every few pictures
		scrollPageWithInfiniteLoading(driver, limit=1)
		#	nextLike = 0
		time.sleep(random.uniform(0.8, 1.3))


def likeRandomPics(driver, likeLimit=random.randint(850, 1045), hashtagWord=None):
	'''
	makes a search and starts liking pics with the searched tag
	'''
	if hashtagWord == None:
		hashtagWord = u'flower'
	#get to the search page
	driver.get('https://www.instagram.com/explore/')
	#handle the search bar
	searchBar = driver.find_element_by_xpath("//nav/div[2]/div/div/div[2]/input")
	searchBar.send_keys(u'#{0}'.format(hashtagWord))
	time.sleep(random.uniform(0.4, 0.8))
	searchBar.send_keys(Keys.RETURN)
	searchBar.send_keys(Keys.RETURN)
	time.sleep(random.uniform(1.9, 2.4))
	driver.refresh()
	#scroll down a few pictures
	scrollPageWithInfiniteLoading(driver, limit=1)
	time.sleep(random.uniform(1.9, 2.4))
	#select the most recent pictures
	#firstRecentPic = waitForPageToLoad(driver, xpathToElem, maxWaitTimeSeconds=25)
	for i in range(1, 4):
		try:
			elem = driver.find_element_by_xpath("/html/body/span/section/main/article/div[2]/div/div[1]/div[{0}]/a".format(i))
			elem.click()
			print(i)
		except Exception:
			print(10000000000)

	#firstRecentPic.click()	



def likeRandomPicsLowLikesScore(driver, likeLimit=random.randint(850, 1045), hashtag=None):
	'''
	makes a search and starts liking pics with the searched tag
	'''
	

def likeAndComment():
	''''''


driver = webdriver.Firefox()
instagramUsername = 'the_vegetal_picture'
instagramPassword = 'N0recuerd0'

logInInstagram(driver, instagramUsername, instagramPassword)
posponeNotifications(driver)
time.sleep(1.0)
####likePicsYouFollow(driver)
likeRandomPics(driver, likeLimit=5, hashtagWord=None)