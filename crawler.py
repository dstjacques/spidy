'''
Python Web Crawler
Built by rivermont and FalconWarriorr
'''

print('[INIT]: Importing libraries...')

#Import required libraries
from lxml import html
import requests
import sys
import time as t

print('[INIT]: Creating variables...')

home = ['http://www.shodor.org/~wbennett/crawler-home.html']

counter = 0
errorCount = 0

print('[INIT]: Reading arguments...')

#

try:
	saveCount = int(sys.argv[1])
except:
	saveCount = 1000
	pass

try:
	todoFile = sys.argv[2]
except:
	todoFile = 'crawler_todo.txt'
	pass

try:
	doneFile = sys.argv[3]
except:
	doneFile = 'crawler_done.txt'
	pass

try:
	logFile = sys.argv[4]
except:
	logFile = 'crawler_log.txt'
	pass

print('[INIT]: Loading save files...')

#Open saved TODO file
with open(todoFile, 'r') as f:
	todo = f.readlines()
todo = [x.strip() for x in todo]

#Open saved done file
with open(doneFile, 'r') as f:
	done = f.readlines()
done = [x.strip() for x in done]

print('[INIT]: Creating functions...')

def check(item):
	'''
	Checks whether item has been checked, doesn't start with 'h' (must be http, https), or is less than 7 characters long (valid url).
	Returns True if item is not a valid url.
	Returns False if it passes all inspections (is valid url).
	'''
	if item in done:
		return True
	elif len(item) < 7:
		return True
	elif item[0:4] != 'http':
		return True
	else:
		return False

def files_save():
	'''
	Save
	'''
	#Open save files
	todoList = open(todoFile, 'w')
	doneList = open(doneFile, 'w')
	todoList.seek(0)
	doneList.seek(0)
	#Save
	for site in todo:
		todoList.write(str(site.encode('utf-8'))[2:-1] + '\n')
	print('[LOG]: Saved TODO list to {0}'.format(todoFile))
	for site in done:
		doneList.write(str(site.encode('utf-8'))[2:-1] + '\n')
	print('[LOG]: Saved finished list to {0}'.format(doneFile))
	#Close things
	todoList.close()
	doneList.close()

def info_log():
	time = t.strftime('%H:%M:%S')
	print('[LOG]: {0}'.format(time))
	print('[LOG]: URLs in TODO: {0}.'.format(len(todo)))
	print('[LOG]: URLs in done: {0}.'.format(len(done)))
	print('[LOG]: Errors thrown so far: {0}.'.format(errorCount))
	print('[LOG]: Likely next link: {0}'.format(todo[0]))
	pass

def err_log(error):
	'''
	Saves the triggering error to the log file.
	Format:
	SITE: todo[0]
	TIMER: Hr:Min:Sec, Weekday Month Year
	ERROR: error
	'''
	log = open(logFile, 'a') #Open the log file
	log.seek(0) #Go to the first line
	time = t.strftime('%H:%M:%S, %A %b %Y') #Get the current time
	try:
		log.write('\nSITE: {0}\nTIME: {1}\nERROR: {2}\n'.format(todo[0], time, str(error)))
	except: #If an error (usually UnicodeEncodeError), write encoded log
		log.write('\nSITE: {0}\nTIME: {1}\nERROR: {2}\n'.format(str(todo[0].encode('utf-8')), time, str(error)))
	log.close() #Save the log file
	todo.remove(todo[0]) #Remove unliked link from todo

def err_saved_message():
	print('[LOG]: Saved error message and timestamp to {0}'.format(logFile))

print('[INIT]: Pruning invalid links from TODO...')

before = len(todo)

for link in todo:
	if check(link):
		todo.remove(link)

if len(todo) == 0:
	todo += home

after = before - len(todo)
print('[INIT]: {0} invalid links removed from TODO.'.format(after))

print('[INIT]: TODO first value: {0}'.format(todo[0]))

print('[INIT]: Starting crawler...')

while len(todo) != 0: #While there are links to check
	#RUN
	try:
		if counter >= saveCount:
			print('[LOG]: Queried {0} links. Automatically saving files...'.format(str(counter)))
			#for link in todo:
			#	if check(link):
			#		todo.remove(link)
			files_save()
			info_log()
			counter = 0
		elif check(todo[0]):
			todo.remove(todo[0])
		else: #Otherwise it must be valid and new, so
			#print('[CRAWL]: Connecting to {0}'.format(todo[0]))
			#To Do: Create live line at bottom of console displaying current action.
			page = requests.get(todo[0]) #Scrape the link's full content
			tree = html.fromstring(page.content) #Get the link's XPath
			links = tree.xpath('//a/@href') #Grab all links inside anchor tags
			for item in list(links): #Encode each item to UTF-8 to minimize errors
				item = item.encode('utf-8')
			todo += list(links) #Add scraped links to the TODO list
			done.append(todo[0]) #Add crawled link to done list
			print('[CRAWL]: Successfully found {0} links on {1}'.format(len(links), todo[0])) #Announce which link was crawled
			todo.remove(todo[0]) #Remove crawled link from TODO list
		todo = list(set(todo)) #Convert TODO to set and back to list
							   #This both removes duplicates and mixes up the list, as sets are unordered collections without duplicates
		counter = counter + 1
	#ERROR HANDLING
	except KeyboardInterrupt as e: #If the user does ^C
		print('[ERR]: User performed a KeyboardInterrupt, saving files...')
		files_save()
		exit()
	except requests.exceptions.HTTPError as e:
		errorCount = errorCount + 1
		print('[ERR]: An HTTPError occured, there is probably something wrong with the link.')
		err_log(e)
		err_saved_message()
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
		errorCount = errorCount + 1
		print('[ERR]: A connection error occured, the link may be down.')
		err_log(e)
		err_saved_message()
	except UnicodeEncodeError as e:
		errorCount = errorCount + 1
		print('[ERR]: A UnicodeEncodeError occured, most likely a foreign character in the link title.')
		err_log(e)
		err_saved_message()
		continue
	except Exception as e: #If any other error is raised
		errorCount = errorCount + 1
		print('[ERR]: An error happened, probably HTTP related.')
		err_log(e)
		err_saved_message()
		continue #Keep going like nothing happened
	#finally: #For debugging purposes, to check one link and then stop
	#	files_save()
	#	exit()

print('[GOD]: How the hell did this happen? I think you\'ve managed to download the internet. I guess you\'ll want to save your files...')
files_save()
