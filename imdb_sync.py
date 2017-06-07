import logging
import sys
import re
import feedparser
import os
import datetime

####################### USER CONFIGURABLE VARS ########################## 
autodlCfgFilePath = "/media/sdl1/home/shyam2007/.autodl"
imdbWatchlistPath = "http://rss.imdb.com/user/ur30191084/watchlist"
matchCategories = "MovieHD"
matchSites = "ar"
minSize = "1GB"
maxSize = "10GB"
resolution = "720p, 1080p"
uploadType = "watchdir"
uploadWatchDir = "/media/sdl1/home/shyam2007/private/deluge/movies_watch/"
#########################################################################

autodlCfgFileName = "autodl.cfg"
oldWatchlistPath = autodlCfgFilePath 
oldWatchlistName = "oldWatchlist.txt"

def addCommonParamsToFile ( autodlCfgFileObject ):

	autodlCfgFileObject.write( "match-categories = " + matchCategories + "\n");
   	autodlCfgFileObject.write( "match-sites = " + matchSites + "\n");
   	autodlCfgFileObject.write( "min-size = " + minSize + "\n");
   	autodlCfgFileObject.write( "max-size = " + maxSize + "\n");
   	autodlCfgFileObject.write( "resolutions = " + resolution + "\n");
   	autodlCfgFileObject.write( "upload-type = " + uploadType + "\n");
   	autodlCfgFileObject.write( "upload-watch-dir = " + uploadWatchDir + "\n");

	return

def addTitleToFile( title, autodlCfgFileObject ):
	
	logging.debug("writing " + title + " to file " + autodlCfgFileObject.name)
	
	autodlCfgFileObject.write( "\n[filter " + title + "]\n");
   	autodlCfgFileObject.write( "shows = " + title + "\n");
   	addCommonParamsToFile(autodlCfgFileObject)

	return

def removeTitleFromFile (title, autodlCfgFileObject):

	logging.debug("trying to locate " + title + " in file " + autodlCfgFileObject.name)

	buffer = autodlCfgFileObject.read()
	regex = r'.*\n\[.*' + title + r'.*\]\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*'
	
	logging.debug("successfully removed " + title + "\n") if re.search(regex, buffer) else logging.debug("title " + title + " not found\n")
	buffer = re.sub(regex, '', buffer)

	autodlCfgFileObject.seek(0)
	autodlCfgFileObject.write(buffer)
	autodlCfgFileObject.truncate()

	return 

def isTitleAlreadyInAutodlCfg (title, autodlCfgFileObject):
	titleAlreadyPresent = 0
	autodlCfgFileObject.seek(0)
	buffer = autodlCfgFileObject.read()
	
	if re.search(title, buffer):
		titleAlreadyPresent = 1

	autodlCfgFileObject.seek(0, 2) # reset file pointer the end

	return titleAlreadyPresent

# returns array of processed titles
def fetchNewWatchlist():

	titleList = []
	regexTvSeries = r'\(.*Series.*\)'
	regexMetaInfo = r'\s+\(.*\)'
	regexYear = r'\((\d{4}).*\)'

	# get imdb watchlist
	imdbWatchlistParser =  feedparser.parse(imdbWatchlistPath)

	# remove TV series and remove year/metainfo from titles
	for post in imdbWatchlistParser.entries:
		logging.debug('Processing title ' + post.title)
		if re.search(regexTvSeries, post.title):
			logging.debug('Title ' + post.title + ' will not be addted to the list\n')
		else:
			titleYearGroup = re.search(regexYear, post.title)
			titleYear = int(titleYearGroup.group(1))
			now = datetime.datetime.now()

			if titleYear >= (now.year - 1):
				processedTitle = (re.sub(regexMetaInfo, '', post.title))
				titleList.append(processedTitle.encode('utf-8'))
				logging.debug('Title ' + processedTitle + ' will be added to the list\n')
			else:
				logging.debug('Title ' + post.title + ' will not be addted to the list\n')	

	return titleList

def compareOldWatchlistWithNew(newWatchlist, oldWatchlist):

	differenceList = list(set(newWatchlist) - set(oldWatchlist))

	return differenceList

def saveNewWatchlistAsOld(newWatchlist):

	with open(oldWatchlistPath + "/" + oldWatchlistName, "w") as oldWatchlistFileObject:
		oldWatchlistFileObject.seek(0)
		for title in newWatchlist:
			oldWatchlistFileObject.write(title.encode('utf-8') + '\n')
		oldWatchlistFileObject.truncate()

	return

def addNewTitlesToCfg(differenceList, autodlCfgFileObject):

	numberOfTitlesAdded = 0
	titlesAddedList = []

	for title in differenceList:
		if isTitleAlreadyInAutodlCfg(title, autodlCfgFileObject):
			logging.debug("Title " + title + " already in autodl cfg file")
		else:
			addTitleToFile(title, autodlCfgFileObject)
			numberOfTitlesAdded = numberOfTitlesAdded + 1
			titlesAddedList.append(title)

	logging.info(str(numberOfTitlesAdded) + ' titles were successfully added to ' + autodlCfgFileObject.name)
	logging.info('The following titles were added to ' + autodlCfgFileObject.name) 
	for title in titlesAddedList:
		logging.info(title)

	return

reload(sys)  
sys.setdefaultencoding('utf8')

oldWatchlist = []

logging.basicConfig(filename='imdb_sync_log.log', level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')

# get new watch list
print "==============================FETCHING NEW WATCH LIST==============================="
newTitleList = fetchNewWatchlist()
print "==============================FETCHED NEW WATCH LIST================================"

# if old watch list exists, read it
print "==============================LOADING OLD WATCHLIST================================="
if os.path.exists(oldWatchlistPath + "/" + oldWatchlistName):
	with open(oldWatchlistPath + "/" + oldWatchlistName, "r+") as oldWatchlistFileObject:
		oldWatchlist = oldWatchlistFileObject.read().splitlines()

# compute difference between the 2 lists
differenceList = compareOldWatchlistWithNew(newTitleList, oldWatchlist)

# add new titles from new watch list
print "=============================ADDING NEW TITLES TO AUTODL============================"
with open(autodlCfgFilePath + "/" + autodlCfgFileName, "a+") as autodlCfgFileObject:
	addNewTitlesToCfg(differenceList, autodlCfgFileObject)

# update old watch list
print "==============================UPDATING OLD WATCH LIST================================"
saveNewWatchlistAsOld(newTitleList)

