#!/usr/bin/python
#-*- coding:utf-8 -*-

import utilsOs, time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException


def getEmojiAndName(browserElement, lowerCase=False):
	'''
	divide the element into emoji and label
	'''
	#get the emoji and prefered label
	titleList = (browserElement.text).split(u' ')
	#get the emoji
	emoji = titleList[0]
	#get the prefered label
	label = u' '.join(titleList[1:])
	#lower case if solicited
	if lowerCase != False:
		label = label.lower()
	return emoji, label


def emojiDictMaker(dumpTheDict=False):
	'''
	makes and dumps a dict of emojis with their name and alternative names
	'''
	emojiCharDict = {}
	emojiNameDict = {}
	emptyList = []
	#urls from emojipedia
	categoriesList = [u'https://emojipedia.org/people/', 
					u'https://emojipedia.org/nature/', 
					u'https://emojipedia.org/food-drink/', 
					u'https://emojipedia.org/activity/', 
					u'https://emojipedia.org/travel-places/', 
					u'https://emojipedia.org/objects/', 
					u'https://emojipedia.org/symbols/', 
					u'https://emojipedia.org/flags/']
	#browse all emojis category by category
	for categoryUrl in tqdm(categoriesList):
		#open the browser window
		driver = webdriver.Firefox()
		#get to the category url
		driver.get(categoryUrl)
		#get lists of emojis in each category
		emojiListSection = driver.find_element_by_class_name(u'emoji-list')
		emojiItems = emojiListSection.find_elements_by_tag_name(u'a')
		emojiUrlList = []
		#browse the list to get each individual emoji url
		for emojiItem in emojiItems:
			#get the url of the emoji page
			emojiUrl = emojiItem.get_attribute(u'href') #emojiUrl = u'{0}{0}'.format(categoryUrl, emoji.get_attribute(u'href')[1:] )
			emojiUrlList.append(emojiUrl)
		#close the browser
		driver.close()
		#go to each saved url page
		for emojiUrl in emojiUrlList:
			#open the browser window
			driver = webdriver.Firefox()
			#go to the emoji url page
			driver.get(emojiUrl)
			#get the emoji and prefered label
			emoji, prefLabel = getEmojiAndName(driver.find_element_by_xpath(u'//h1'), lowerCase=True)
			#get the hashtags
			hashtag = u'#{0}'.format(prefLabel.replace(u' ', u'').replace(u':', u''))
			hashtagWithEmoji = u'#{0}{1}'.format(prefLabel.replace(u' ', u'').replace(u':', u''), emoji)
			#save to the dicts
			emojiCharDict[emoji] = {u'preferedLabel': prefLabel, u'alternativeLabel':[], u'relatedEmojis':[], u'category':( categoryUrl.split(u'/') )[-2], u'hashtags':[hashtag, hashtagWithEmoji]}
			emojiNameDict[prefLabel] = emoji
			#get the alternative labels #############################################
			try:
				altLabelsSection = driver.find_element_by_class_name(u'aliases')
				altList = altLabelsSection.find_elements_by_tag_name(u'li')
				for altElement in altList:
					emojiAlt, altLabel = getEmojiAndName(altElement, lowerCase=True)
					#save to the dicts
					emojiCharDict[emoji][u'alternativeLabel'] = list(set(emojiCharDict[emoji].get(u'alternativeLabel')+[altLabel]))
					emojiNameDict[altLabel] = emoji
					#save the hashtags to the dict
					hashtag = u'#{0}'.format(altLabel.replace(u' ', u'').replace(u':', u''))
					hashtagWithEmoji = u'#{0}{1}'.format(altLabel.replace(u' ', u'').replace(u':', u''), emoji)
					emojiCharDict[emoji][u'hashtags'] = list(set( emojiCharDict[emoji].get(u'hashtags')+[hashtag, hashtagWithEmoji] ))
			except NoSuchElementException: pass
			#if there is a colon ':' we add a couple of alternative labels
			if u':' in prefLabel:
				columnSplitLabel = prefLabel.split(u': ')
				#we take only what's after the colon
				afterColonLabel = columnSplitLabel[1]
				#we get rid of the colon and inverse the order of the separated elements
				inversedLabel = u'{0} {1}'.format(columnSplitLabel[1], columnSplitLabel[0])
				#save to the dicts
				emojiCharDict[emoji][u'alternativeLabel'] = list(set(emojiCharDict[emoji].get(u'alternativeLabel')+[afterColonLabel, inversedLabel]))
				emojiNameDict[afterColonLabel] = emoji
				emojiNameDict[inversedLabel] = emoji
				#save the hashtags to the dict
				hashtag1 = u'#{0}'.format(afterColonLabel.replace(u' ', u'').replace(u':', u''))
				hashtagWithEmoji1 = u'#{0}{1}'.format(afterColonLabel.replace(u' ', u'').replace(u':', u''), emoji)
				hashtag2 = u'#{0}'.format(inversedLabel.replace(u' ', u'').replace(u':', u''))
				hashtagWithEmoji2 = u'#{0}{1}'.format(inversedLabel.replace(u' ', u'').replace(u':', u''), emoji)
				emojiCharDict[emoji][u'hashtags'] = list(set( emojiCharDict[emoji].get(u'hashtags')+[hashtag1, hashtagWithEmoji1, hashtag2, hashtagWithEmoji2] ))
			#get the apple name as an alternative label #############################
			try:
				appleLabelSection = driver.find_element_by_class_name(u'applenames')
				appleList = appleLabelSection.find_elements_by_tag_name(u'p')
				for appleElement in appleList:
					emojiAlt, altLabel = getEmojiAndName(appleElement, lowerCase=True)
					#save to the dicts
					emojiCharDict[emoji][u'alternativeLabel'] = list(set(emojiCharDict[emoji].get(u'alternativeLabel')+[altLabel]))
					emojiNameDict[altLabel] = emoji
					#save the hashtags to the dict
					hashtag = u'#{0}'.format(altLabel.replace(u' ', u'').replace(u':', u''))
					hashtagWithEmoji = u'#{0}{1}'.format(altLabel.replace(u' ', u'').replace(u':', u''), emoji)
					emojiCharDict[emoji][u'hashtags'] = list(set( emojiCharDict[emoji].get(u'hashtags')+[hashtag, hashtagWithEmoji] ))
			except NoSuchElementException: pass
			#get the unicode name as an alternative label ###########################
			try:
				unicodeLabelSection = driver.find_element_by_class_name(u'unicodename')
				unicodeList = unicodeLabelSection.find_elements_by_tag_name(u'p')
				for unicodeElement in unicodeList:
					emojiAlt, altLabel = getEmojiAndName(unicodeElement, lowerCase=True)
					#save to the dicts
					emojiCharDict[emoji][u'alternativeLabel'] = list(set(emojiCharDict[emoji].get(u'alternativeLabel')+[altLabel]))
					emojiNameDict[altLabel] = emoji
					#save the hashtags to the dict
					hashtag = u'#{0}'.format(altLabel.replace(u' ', u'').replace(u':', u''))
					hashtagWithEmoji = u'#{0}{1}'.format(altLabel.replace(u' ', u'').replace(u':', u''), emoji)
					emojiCharDict[emoji][u'hashtags'] = list(set( emojiCharDict[emoji].get(u'hashtags')+[hashtag, hashtagWithEmoji] ))
			except NoSuchElementException: pass
			#get the shortCodes name as an alternative label #########################
			try:
				shortcodeLabelSection = driver.find_element_by_class_name(u'shortcodes')
				shortcodeList = shortcodeLabelSection.find_elements_by_tag_name(u'li')
				for shortcodeElement in shortcodeList:
					shortCode = (shortcodeElement.text).lower().replace(u':', u'').replace(u'_', u' ')
					#save to the dicts
					emojiCharDict[emoji][u'alternativeLabel'] = list(set(emojiCharDict[emoji].get(u'alternativeLabel')+[shortCode]))
					emojiNameDict[shortCode] = emoji
					#save the hashtags to the dict
					hashtag = u'#{0}'.format(shortCode.replace(u' ', u'').replace(u':', u''))
					hashtagWithEmoji = u'#{0}{1}'.format(shortCode.replace(u' ', u'').replace(u':', u''), emoji)
					emojiCharDict[emoji][u'hashtags'] = list(set( emojiCharDict[emoji].get(u'hashtags')+[hashtag, hashtagWithEmoji] ))
			except NoSuchElementException: pass
			#get the related emojis ##################################################
			try:
				relatedLabelSection = driver.find_element_by_xpath(u'/html/body/div[3]/div[1]/article/ul[3]')
				relatedList = relatedLabelSection.find_elements_by_tag_name(u'a')
				for relatedElement in relatedList:
					relatedEmoji, relatedName = getEmojiAndName(relatedElement, lowerCase=True)
					#save to the dict
					emojiCharDict[emoji].get(u'relatedEmojis').append( [relatedEmoji, relatedName] )
			except NoSuchElementException: pass
			#close the browser
			driver.close()
	#dump the dicts to json files
	utilsOs.dumpDictToJsonFile(emojiCharDict, pathOutputFile=u'./emojiDict/emojiCharDict.json', overwrite=True)
	utilsOs.dumpDictToJsonFile(emojiNameDict, pathOutputFile=u'./emojiDict/emojiNameDict.json', overwrite=True)


def emojiHashtagDictMaker(emojiCharDictPath=u'./emojiDict/emojiCharDict.json'):
	'''
	given the emoji dict, makes a simple dict with key as hashtags and one emoji as value
	'''
	emojiHashtagDict = {}
	emptyList = []
	emojiCharDict = utilsOs.openJsonFileAsDict(emojiCharDictPath)
	for emoji, valDict in emojiCharDict.items():
		#avoid general or misleading categories
		if valDict[u'category'] not in [u'people', u'symbols', u'flags']:
			hashtagList = valDict[u'hashtags']
			#populate the hashtag dict
			for hashtag in hashtagList:
				emojiHashtagDict[hashtag] = list(set( emojiHashtagDict.get(hashtag, list(emptyList)) + [emoji] ))
	#dump the dicts to json files
	utilsOs.dumpDictToJsonFile(emojiHashtagDict, pathOutputFile=u'./emojiDict/emojiHashtagDict.json', overwrite=True)
