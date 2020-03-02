#Load Config.py dataSet with built in tables and columns
import inspect,os
runningDir = os.path.dirname(os.path.abspath(inspect.getfile(lambda: None)))
print(runningDir)
execfile(runningDir + '\Config.py')

#Import adal and requests, these aren't built into Nuix
import sys
sys.path.append(runningDir + '\site-packages')

from threading import Thread
from threading import Lock
from time import sleep
from java.util import Locale
from org.joda.time import DateTimeZone

import adal,requests,json,traceback,datetime,time,urllib2
requests.packages.urllib3.disable_warnings() 


printMutex = Lock()
databaseMutex = Lock()
debugMutex = Lock()
counterMutex = Lock()
postTime=0
jsonTime=0
databaseTime=0
postTimes=[]
postSizes=[]
debug=True
batchSize=100
fullItemsFilters=20 #this is really dependant on how many columns are coming through...
MinimumItemsFilters=200 #cut down metadata so should be ok at this size...
activeBatches=3
totalCompleted=0
threads=[]
workspaceId="!"
myWorkspace=""
myReportLocation=runningDir + '\Nuix_Case_Report.pbix'
safeMetadata=None
jsWindow=None
entityTypes=[]
myToken=""
myItemUtility=None

##inboundGlobalsDontTouch
currentCase=None
utilities=None
pushItems=None
focusMetadataProfile=None
powerBiUsername=None
powerBiPassword=None
powerBiClientId=None
powerBiTennantId=None
protectedMethods={}

def mutexPrint(myObj):
	with printMutex:
		print(myObj)

def safeJSONLoads(myDataString):
	try:
		return(json.loads(myDataString))
	except Exception as ex:
		mutexPrint("---- Can not decod json data from string -----\n" + myDataString)
		return(attemptTrimJSON(myDataString))
		
def attemptTrimJSON(myDataString): ### sometimes the rest service sends crap at the end of the content... 
	try:
		obj=json.loads(myDataString.rsplit('}',1)[0] + '}')
		print("Successful resolution to badly recieved content!!!!") 
		return(obj)
	except Exception as ex:
		mutexPrint("---- Can not decod json data from Trimmed string -----\n" + myDataString)
	return({})

def protectedCallback(method,args):
	global protectedMethods
	try:
		if(len(args) == 0):
			return protectedMethods[method]()
		elif(len(args)==1):
			return protectedMethods[method](args[0])
		elif(len(args)==2):
			return protectedMethods[method](args[0],args[1])
		elif(len(args)==3):
			return protectedMethods[method](args[0],args[1],args[2])
		else:
			#TODO too many args
			pass
	except:
		print("Method call failure... (" + method + ")")
		print(str(sys.exc_info()[1]))
		print(traceback.format_exc())


def getTennantId(domain):
	openIDConfig = 'https://login.microsoftonline.com/' + domain +'/.well-known/openid-configuration'
	header={}
	myRequest = requests.get(url=openIDConfig, headers=header)
	if(myRequest.ok):
		myObject=json.loads(myRequest.text)
		for obj in myObject:
			if(type(myObject[obj]) is unicode):
				if('/' in myObject[obj]):
					for section in myObject[obj].split('/'):
						if(section.count('-') == 4):
							return section
	else:
		return(None)
		
def getToken():
	global powerBiUsername,powerBiPassword,powerBiClientId,powerBiTennantId,myToken
	""" Microsoft recommends using the ADAL library so I have done so... however... a simple post will also achieve this result:
	#Bonus with this method is the json that returns also includes the scope permissions which may be helpful to check.
	r = requests.post('https://login.microsoftonline.com/common/oauth2/token', data = {
	'grant_type': 'password',
	'scope': 'openid',
	'resource': 'https://analysis.windows.net/powerbi/api',
	'client_id': xxxx,#your client_id
	'username': yyyy, #your username
	'password': zzzz, #your password
	})
	"""
	authority_url = 'https://login.windows.net/common'
	resource_url = 'https://analysis.windows.net/powerbi/api'
	
	context = adal.AuthenticationContext(authority=authority_url,validate_authority=True,api_version=None)
	try:
		tokenContext=(context.acquire_token_with_username_password(resource=resource_url,client_id=powerBiClientId,username=powerBiUsername,password=powerBiPassword))
		powerBiTennantId=tokenContext.get('tenantId')
		myToken=tokenContext.get('accessToken')
		return True
	except adal.adal_error.AdalError as ex:
		errorResponse=str(ex)
		try:
			errorResponse=ex.error_response["error_description"]
		except:
			pass
		if("Send an interactive authorization request for this user and resource." in errorResponse):
			powerBiTennantId=getTennantId(powerBiUsername.split('@')[1])
			if(powerBiTennantId is not None):
				redirectLink="https://app.powerbi.com/embedsetup/SignInRedirect"
				authenticationURL=("https://login.microsoftonline.com/" + powerBiTennantId + "/oauth2/authorize?client_id=" + powerBiClientId + "&response_type=code&redirect_uri=" + redirectLink + "&resource=https://analysis.windows.net/powerbi/api&prompt=consent")
				if(protectedCallback("handleInteractiveRequests",["User must approve access",authenticationURL,redirectLink])):
					return getToken()
			else:
				protectedCallback("showError",["Error Authenticating using provided credentials. Missing domain? e.g user@domain.com"])
		else:
			protectedCallback("showError",["Error Authenticating using provided credentials:\n\t" + errorResponse])
			return(None)
	except Exception as ex:
		errorResponse=ex
		try:
			errorResponse=ex.error_response["error_description"]
		except:
			pass
		protectedCallback("showError",["Error Authenticating using provided credentials:\n\t" + errorResponse])
		return(None)
	

def getWorkspaces():
	global myToken
	myWorkspacesURL = 'https://api.powerbi.com/v1.0/myorg/groups'
	header = {'Authorization': 'Bearer ' + myToken}
	myRequest = requests.get(url=myWorkspacesURL, headers=header)
	if(myRequest.ok):
		myWorkspaces=safeJSONLoads(myRequest.text).get('value')
		protectedCallback("updateMessage",["Getting workspaces",""])
		workspaceId=protectedCallback("workspaceChoooser",[myWorkspaces])
		if not (workspaceId == ""): #"" represents a 'my workspace'
			return ('groups/' + workspaceId)
		else:
			return ""
	else:
		printRestError(myRequest)
		return ""



def getDataSetIdbyName(myDataSetName):
	global myToken
	myDataSetsURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/datasets'
	header = {'Authorization': 'Bearer ' + myToken}
	myRequest = requests.get(url=myDataSetsURL, headers=header)
	if(myRequest.ok):
		for existingDataSet in (safeJSONLoads(myRequest.text).get('value')):
			if(existingDataSet.get('name') == myDataSetName):
				return(existingDataSet.get('id'))
	else:
		printRestError(myRequest)
		return(None)


def createDataSet(myData):
	global myToken
	myDataSetId=getDataSetIdbyName(myData.get('name'))
	if(myDataSetId is not None):
		mutexPrint("Data Set already exists:" + myData.get('name') + " (" + myDataSetId + ")")
		return myDataSetId
	else:
		mutexPrint("Creating new DataSet")
	
	myDataSetsURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/datasets'
	header = {'Authorization': 'Bearer ' + myToken}
	myRequest = requests.post(url=myDataSetsURL, headers=header,data=json.dumps(myData))
	if(myRequest.ok): #201 = Created
		myDataSetId=safeJSONLoads(myRequest.text).get('id')
		return(myDataSetId)
	else:
		printRestError(myRequest)
		return(None)

def getReports():
	global myToken
	myReportsURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/reports'
	header = {'Authorization': 'Bearer ' + myToken}
	try:
		myRequest = requests.get(url=myReportsURL, headers=header)
		if(myRequest.ok):
			myReports=safeJSONLoads(myRequest.text).get('value')
			return(myReports)
		else:
			printRestError(myRequest)
			return(None)
	except Exception as ex:
		mutexPrint("uncaught error #3")
		mutexPrint(ex)
		traceback.print_exc()
		req = urllib2.Request(myReportsURL)
		req.add_header('Authorization', 'Bearer ' + myToken)
		resp = urllib2.urlopen(req)
		content = resp.read()
		myReports=safeJSONLoads(content).get('value')
		return(myReports)
	return(None)
	
def makeTemporaryStorage(myDataSetName):
	global myToken
	bloblStorageURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/imports/createTemporaryUploadLocation'
	header = {'Authorization': 'Bearer ' + myToken}
	try:
		myRequest = requests.post(url=bloblStorageURL, headers=header)
		if(myRequest.ok):
			temporaryBlobStorage=safeJSONLoads(myRequest.text)
			print(temporaryBlobStorage)
			return(temporaryBlobStorage["url"])
		else:
			print('rest error')
			printRestError(myRequest)
			return(None)
	except requests.exceptions.Timeout:
		# socket Timeout... retrying...
		mutexPrint("socket Timeout")
	except requests.exceptions.TooManyRedirects:
		mutexPrint("Too many redirects??")
	except requests.exceptions.RequestException as e:
		mutexPrint("RequestException")
		print(e)
	return None

def importPBIX(myFileLocation,myDataSetName):
	global myToken
	print('importing:' + myFileLocation + '\ninto:' + myDataSetName)
	try:
		results=json.loads(jruby.eval("UploadPBIX('" + myToken + "','" + myWorkspace + "','"+ myFileLocation + "','" + myDataSetName + "')"))
		if "id" in results:
			return waitUntilImported(results["id"])
		else:
			reason=results['error']['pbi.error']['code']
			if(reason=="PowerBIModelNotFoundException"):
				print("PBIX file references a non existent dataset")
				protectedCallback("showError",["Could not generate default Report\nPBIX file references a non existent dataset\nPlease Open: " + myFileLocation + "\n\n With Power BI Desktop, hit [Edit] and choose the recently created Default:\n" + nuixDefaultDataSetForReports + "\n\nAfter doing the above save the pbix in the same directory and rerun this script"])
				return None
			elif(reason=="PowerBINotLicensedException"):
				if(protectedCallback("handleInteractiveRequests",["You do not have a Power BI Pro account, please sign up or try the free option","https://powerbi.microsoft.com/en-us/power-bi-pro/","https://app.powerbi.com/home"])):
					pass #possibly need to restart everything here...
			else:
				protectedCallback("showError",["Could not generate default Report\n" + reason])
				return None
	except ScriptException  as e:
		mutexPrint(e.getMessage() + "\nLine:" + str(e.getLineNumber()) + "\nStack:" + "\n".join(str(v) for v in e.getStackTrace()))
		return None
	
	

def waitUntilImported(myRequestId):
	global myToken
	print('waiting...')
	myRequestURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/imports/' + myRequestId
	header = {'Authorization': 'Bearer ' + myToken}
	myRequest = requests.get(url=myRequestURL, headers=header)
	if(myRequest.ok):
		obj=safeJSONLoads(myRequest.text)
		status=obj["importState"]
		print(status)
		if(status=="Succeeded"):
			return(obj["reports"][0])
		else:
			print("Report Status:" + status)
			sleep(0.5)
			return(waitUntilImported(myRequestId))
		print(myRequest)
	else:
		printRestError(myRequest)
		return(None)

#Not currently used
#def generateEmbeddedReportToken(myReportId,myDataSetId):
#	tokenURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/reports/' + myReportId + '/GenerateToken'
#	header = {'Authorization': 'Bearer ' + myToken,
#		'Content-Type': 'application/json'
#	}
#	myData={
#		"accessLevel":"View", #edit may be more appropriate?
#		"allowSaveAs":True
#	}
#	data=json.dumps(myData)
#	myRequest = requests.post(url=tokenURL, headers=header,data=data)
#	if(myRequest.ok): 
#		return(safeJSONLoads(myRequest.text))
#	else:
#		printRestError(myRequest)
#		return(None)

def cloneReport(myReportId,myReportName,myDataSetId):
	cloneURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/reports/' + myReportId + '/Clone'
	header = {'Authorization': 'Bearer ' + myToken,
		'Content-Type': 'application/json'
	}
	myData={
		"name":myReportName,
		"targetModelId":myDataSetId
	}
	data=json.dumps(myData)
	myRequest = requests.post(url=cloneURL, headers=header,data=data)
	if(myRequest.ok): 
		return(safeJSONLoads(myRequest.text))
	else:
		printRestError(myRequest)
		return(None)

def getTablesInDataSet(myDataSetId):
	global myToken
	try:
		myTablesURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/datasets/' + myDataSetId + '/tables'
		header = {'Authorization': 'Bearer ' + myToken}
		myRequest = requests.get(url=myTablesURL, headers=header)
		if(myRequest.ok):
			myTables=safeJSONLoads(myRequest.text).get('value')
			myTableNames=[]
			for myTable in myTables:
				myTableNames.append(myTable.get('name'))
			return(myTableNames)
		else:
			printRestError(myRequest)
	except requests.exceptions.Timeout:
		print("Socket Timeout")
	except requests.exceptions.TooManyRedirects:
		print("Too many redirects??")
	except requests.exceptions.RequestException as e:
		print("requestException:" + str(e))
	except Exception as ex:
		print("Uncaught Exception:" + str(ex))
	return([])
		
def deleteDataSet(myDataSetId):
	global myToken
	myDataSetsURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/datasets/' + myDataSetId
	header = {'Authorization': 'Bearer ' + myToken}
	myRequest = requests.delete(url=myDataSetsURL, headers=header)
	if(myRequest.ok):
		mutexPrint('DataSet Deleted')
	else:
		printRestError(myRequest)
		return(None)

def clearDataInTable(myDataSetId,tableName):
	global myToken
	myTablesURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/datasets/' + myDataSetId + '/tables/' + tableName +'/rows'	
	header = {'Authorization': 'Bearer ' + myToken}
	myRequest = requests.delete(url=myTablesURL, headers=header)
	if(myRequest.ok):
		mutexPrint('Table Cleared:' + tableName)
	else:
		if(myRequest.status_code==429):
			#too busy, retry!
			sleep(0.2)
			clearDataInTable(myDataSetId,tableName)
		else:
			printRestError(myRequest)
			return(None)

def pushDataToTable(myDataSetId,myTableName,rows):
	global debug
	global myToken
	global postTime
	global postTimes
	global jsonTime
	global postSizes
	myTablesURL = 'https://api.powerbi.com/v1.0/myorg/' + myWorkspace + '/datasets/' + myDataSetId + '/tables/' + myTableName +'/rows'	
	header = {'Authorization': 'Bearer ' + myToken}
	myData={
	  "rows": rows
	}
	repost=False
	start=0
	jsonDump=""
	tooBusy=True
	try:
		start = time.time()
		jsonDump=json.dumps(myData)
		end = time.time()
		with debugMutex:
			jsonTime+=(end-start)
		start = time.time()
		myRequest = requests.post(url=myTablesURL, headers=header,data=jsonDump)
		if(myRequest.ok):
			#with printMutex:
			#	print("Successful post")
			repost=False
		else:
			if(myRequest.status_code == 429):
				mutexPrint("Repost Required:" + str(myRequest.status_code) )
				repost=True
			elif(myRequest.status_code ==500):
				#429 too busy, retry.
				#500 timeout (could not process in the time provided), retry
				repost=False
				if(len(rows) > 1):
					half = len(rows) / 2
					mutexPrint("Repost Required:" + str(myRequest.status_code) + " Halving rows to :" + str(half))
					# perhaps the request is just too difficult ? Experimental... halving the rows to see if it goes any better
					pushDataToTable(myDataSetId,myTableName,rows[:half])
					pushDataToTable(myDataSetId,myTableName,rows[half:])
				else:
					mutexPrint("Giving up... the smallest chunk isn't getting through")
					print(json.dumps(rows))
			else:
				if(myRequest.reason=="Forbidden"):
					if(safeJSONLoads(myRequest.text).get('error').get('message')=="Access token has expired, resubmit with a new access token"):
						mutexPrint("getting new Token")
						if(getToken() is not None):
							mutexPrint('Gained Access Token')
							repost=True
						else:
							mutexPrint('Could not gain new Access Token')
					else:
						mutexPrint("(forbidden!) Could not do request (" + sys._getframe().f_back.f_code.co_name + "):" + myRequest.reason + "\n\t" + myRequest.url + "\n\t" + safeJSONLoads(myRequest.text).get('error').get('message'))
						for attr in dir(myRequest):
							mutexPrint("obj.%s = %r" % (attr, getattr(myRequest, attr)))
						print(rows)
						report=False
				else:
					mutexPrint("Could not do request (" + sys._getframe().f_back.f_code.co_name + "):" + myRequest.reason + "\n\t" + myRequest.url + "\n\t" + safeJSONLoads(myRequest.text).get('error').get('message'))
					for attr in dir(myRequest):
						mutexPrint("obj.%s = %r" % (attr, getattr(myRequest, attr)))
					print(rows)
					report=False
	except requests.exceptions.Timeout:
		# socket Timeout... retrying...
		if(debug):
			mutexPrint("socket Timeout")
		repost=True
	except requests.exceptions.TooManyRedirects:
		if(debug):
			mutexPrint("Too many redirects??")
	except requests.exceptions.RequestException as e:
		# Probably reached the max connections for this minute (120)
		# Alternatively... perhaps the network dropped out?
		# Alternatively... the network was really really slow
		repost=False
		if("BadStatusLine" in str(e)):
			if(len(rows) > 3):
				half = len(rows) / 2
				print("Bad Status Line (Disconnected?) Halving rows to :" + str(half))
				# perhaps the request is just too difficult ? Experimental... halving the rows to see if it goes any better
				pushDataToTable(myDataSetId,myTableName,rows[:half])
				pushDataToTable(myDataSetId,myTableName,rows[half:])
			else:
				mutexPrint("Giving up... the smallest chunk isn't getting through")
		else:
			if(debug):
				mutexPrint("RequestException")
				mutexPrint(e)
		
	finally:
		end = time.time()
		with debugMutex:
			postTime+=(end-start)
			postTimes.append(end-start)
			postSizes.append(len(jsonDump))
	if(repost):
		if(tooBusy):
			sleep(10)
			pushDataToTable(myDataSetId,myTableName,rows)
		myMethod=sys._getframe().f_back.f_code.co_name
		if(myMethod=="pushDataToTable"):
			mutexPrint("Giving up on retries...\n" + jsonDump) #came from pushDataToTable and is already a retry, I should probably retry more than once... but eh..
		else:
			sleep(5)
			pushDataToTable(myDataSetId,myTableName,rows)
	return(repost)

def printRestError(myRequest):
	myMethod=sys._getframe().f_back.f_code.co_name
	description=""
	try:
		description=safeJSONLoads(myRequest.text).get('error').get('message')
	except:
		pass
	if(str(description)=="User is not licensed for Power BI"):
		protectedCallback("showError",["Could not do request (" + str(myMethod) + "):" + str(myRequest.reason) + "\n\t" + str(myRequest.url) + "\n\t" + str(description)])
		if(protectedCallback("handleInteractiveRequests",["User is not licensed for Power BI","https://powerbi.microsoft.com/en-us/power-bi-pro/","https://app.powerbi.com/home"])):
			pass #possibly need to restart everything here...
	else:
		protectedCallback("showError",["Could not do request (" + str(myMethod) + "):" + str(myRequest.reason) + "\n\t" + str(myRequest.url) + "\n\t" + str(description)])
		for attr in dir(myRequest):
			mutexPrint("obj.%s = %r" % (attr, getattr(myRequest, attr)))
		
def getSizeRows():
	global currentCase, myItemUtility
	allItems=currentCase.searchUnsorted("*:*")
	uniqueCaseItems=myItemUtility.deduplicate(allItems)
	protectedCallback("updateMessage",["Updating Size Summary","Audited"])
	allAuditedItems=currentCase.searchUnsorted("flag:audited")
	uniqueAuditedItems=myItemUtility.deduplicate(allAuditedItems)
	allAuditedItemsSize=0
	for item in allAuditedItems:
		allAuditedItemsSize+=(item.getAuditedSize())
	uniqueAuditedItemsSize=0
	for item in uniqueAuditedItems:
		uniqueAuditedItemsSize+=(item.getAuditedSize())
	protectedCallback("updateMessage",["Updating Size Summary","File"])
	allFileItems=currentCase.searchUnsorted("flag:physical_file")
	uniqueFileItems=myItemUtility.deduplicate(allFileItems)
	allFileItemsSize=0
	for item in allFileItems:
		allFileItemsSize+=(item.getFileSize())
	uniqueFileItemsSize=0
	for item in uniqueFileItems:
		uniqueFileItemsSize+=(item.getFileSize())
	
	protectedCallback("updateMessage",["Updating Size Summary","Digests"])
	allDigestItems=currentCase.searchUnsorted("md5:*")
	uniqueDigestItems=myItemUtility.deduplicate(allDigestItems)
	allDigestItemsSize=0
	for item in allDigestItems:
		allDigestItemsSize+=(item.getDigests().getInputSize())
	uniqueDigestItemsSize=0
	for item in uniqueDigestItems:
		uniqueDigestItemsSize+=(item.getDigests().getInputSize())
	
	return [{
		'Summary Title':'All Items',
		'Items':str(len(allItems)),
		'(U) Items':str(len(uniqueCaseItems)),
		u'\u03A3 Size':"0", #nothing to operate on. See other types
		u'\u03A3(U) Size':"0", #nothing to operate on. See other types
	},
	{
		'Summary Title':'Audited',
		'Items':str(len(allAuditedItems)),
		'(U) Items':str(len(uniqueAuditedItems)),
		u'\u03A3 Size':str(allAuditedItemsSize),
		u'\u03A3(U) Size':str(uniqueAuditedItemsSize),
	},
	{
		'Summary Title':'File',
		'Items':str(len(allFileItems)),
		'(U) Items':str(len(uniqueFileItems)),
		u'\u03A3 Size':str(allFileItemsSize),
		u'\u03A3(U) Size':str(uniqueFileItemsSize),
	},
	{
		'Summary Title':'Digest',
		'Items':str(len(allDigestItems)),
		'(U) Items':str(len(uniqueDigestItems)),
		u'\u03A3 Size':str(allDigestItemsSize),
		u'\u03A3(U) Size':str(uniqueDigestItemsSize),
	},
	]

from javax.script import ScriptEngineManager
from javax.script import ScriptContext
from javax.script import ScriptException
from java.io import StringWriter
from java.lang import System

class ConsoleWriter (StringWriter):
	def __init__(self,initialSize,name):
		self.linePrefix=name
	
	def append(self,*args):
		if "".join(args[0]).strip(): #Skipping blanks
			mutexPrint(self.linePrefix +  "".join(args[0]).strip())

	def write(self,*args):
		if "".join(args[0]).strip(): #Skipping blanks
			mutexPrint(self.linePrefix +  "".join(args[0]).strip())

jruby = ScriptEngineManager().getEngineByName("jruby")
b = jruby.createBindings();
try:
	b.put("$currentCase", currentCase)
except:
	pass

try:
	b.put("currentCase", currentCase)
except:
	pass

jruby.setBindings(b, ScriptContext.ENGINE_SCOPE);
jruby.getContext().setWriter(ConsoleWriter(0,""));
jruby.getContext().setErrorWriter(ConsoleWriter(0,"ERROR:"));

def navigateJythonIssues():
	mutexPrint("...\t navigating broken jython issue")
	try:
		results=jruby.eval("""
	def UploadPBIX(myToken,myWorkspace,filename,myDataSetName)
		require 'net/http'
		require 'uri'
		uri = URI("https://api.powerbi.com/v1.0/myorg/#{myWorkspace}/imports?datasetDisplayName=#{myDataSetName}&nameConflict=CreateOrOverwrite")
		request = Net::HTTP::Post.new(uri)
		request['Authorization'] = 'Bearer ' + myToken
		form_data = [['filePath', File.open(filename)]]
		
		request.set_form form_data, 'multipart/form-data'
		response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http| # pay attention to use_ssl if you need it
		  http.request(request)
		end
		return response.body
	end
		""")
	except ScriptException  as e:
		mutexPrint(e.getMessage() + "\nLine:" + str(e.getLineNumber()) + "\nStack:" + "\n".join(str(v) for v in e.getStackTrace()))
	mutexPrint("...\t\t Navigated")


def getChildCases(startingCase):
	global currentCase
	returnedList=[]
	returnedList.append(startingCase)
	if(currentCase.isCompound()):
		for case in startingCase.getChildCases():
			for case in getChildCases(case):
				returnedList.append(case)
	return returnedList

from java.sql import DriverManager
from org.apache.derby import jdbc
DriverManager.registerDriver(jdbc.EmbeddedDriver())
import os,sys,re

def getHistory():
	global currentCase
	bigHistoryQuery="""
	SELECT 
	{fn TIMESTAMPADD(SQL_TSI_SECOND, START_DATE, TIMESTAMP('1970-01-01-00.00.00.000000')) } as StartDate,
	Name as Username,
	typeString as Action,
	DETAIL_PARAMS as "AFFECTED_ITEMS"
	
	FROM
	(
	SELECT 
			(h.START_DATE / 1000 / 86400)*86400 as START_DATE,
			 u.NAME,
			(CASE
				 WHEN  TYPE = 1 THEN 'search'
				 WHEN  TYPE = 2 THEN 'loadData'
				 WHEN  TYPE = 3 THEN 'export'
				 WHEN  TYPE = 4 THEN 'annotation'
				 WHEN  TYPE = 5 THEN 'openSession'
				 WHEN  TYPE = 6 THEN 'closeSession'
				 WHEN  TYPE = 7 THEN 'script'
				 WHEN  TYPE = 8 THEN 'import'
				 WHEN  TYPE = 9 THEN 'delete'
				 WHEN  TYPE = 10 THEN 'printPreview'
				  ELSE 'unknown'
			   END) as typeString
				,
				DETAIL_PARAMS
			FROM 
				HISTORY_RECORDS h
			LEFT JOIN 
				USERS u
			ON
				u.ID=h.USER_ID
	) as b
	"""
	
	
	prog = re.compile("(?<=count>)\d+", re.IGNORECASE)
	
	results={}
	for thisCase in getChildCases(currentCase):
		expectedLocation=thisCase.getLocation().toString() + "/Stores/AnalysisDatabase"
		if not os.path.exists(expectedLocation):
			print("Analysis Database Expected but not found:\n" + expectedLocation)
		else:
			dbconnection=None
			try:
				dbconnection=DriverManager.getConnection("jdbc:derby:" + expectedLocation +";create=false", "", "")
				stmt=dbconnection.createStatement()
				rs = stmt.executeQuery(bigHistoryQuery)
				while(rs.next()):
					rscolumns=rs.getMetaData()
					result={}
					for i in range(1,rscolumns.getColumnCount()+1):
						columnTitle=rscolumns.getColumnName(i)
						value=rs.getString(i)
						if(value is None):
							value=""
						if(columnTitle=="AFFECTED_ITEMS"):
							if("count>" in value.lower()):
								matches=prog.search(value)
								if(matches is not None):
									value=matches.group(0)
								else:
									print("===")
									print(result["ACTION"])
									print(value)
									value=0
							else:
								value="0"
							columnTitle="Total Affected Items"
						if(columnTitle=="STARTDATE"):
							value=value[0:10]
						result[columnTitle]=value
					key=result["STARTDATE"] + result["USERNAME"] + result["ACTION"]
					if key not in results:
						default={
							'StartDate':result["STARTDATE"],
							'User':result["USERNAME"],
							'Action':result["ACTION"],
							'Total Actions':0,
							'Total Affected Items':0
						}
						results[key]=default
					results[key]["Total Actions"]+=1
					results[key]["Total Affected Items"]+=int(result["Total Affected Items"])
	
			except Exception as ex:
				print("exception getting history:" + ex.message)
				traceback.print_exc()
			finally:
				if(dbconnection):
					dbconnection.close()
	return (results.values())



def getFileTypeSummary():
	global currentCase,myItemUtility
	rows=[]
	for caseType in currentCase.getItemTypes():
		typeResults=currentCase.searchUnsorted('mime-type:"' + caseType.getName() + '"')
		typeUniqueCount=myItemUtility.deduplicate(typeResults)
		rows.append({
			'File Type Name':caseType.getLocalisedName(),
			'Kind Name':caseType.getKind().getLocalisedName(),
			u'\u03A3 Hits':len(typeResults),
			u'\u03A3(U) Hits':len(typeUniqueCount),
		})

	return(rows)
	
def getIrregularItemSummary():
	global currentCase,myItemUtility
	rows=[]
	for irregularFilter in irregularFilters:
		allMatches=currentCase.searchUnsorted(irregularFilter["query"])
		uniqueMatches=myItemUtility.deduplicate(allMatches)
		rows.append({
		'Irregular Filter':irregularFilter["name"],
		u'\u03A3 Hits':len(allMatches),
		u'\u03A3(U) Hits':len(uniqueMatches)
		})
	return rows
	
def getLanguageSummary():
	global currentCase,myItemUtility
	lookup={}

	for language in Locale.getAvailableLocales():
		lookup[str(language.getISO3Language())]=str(language.getDisplayLanguage())

	rows=[]
	for language in currentCase.getLanguages():
		languageDisplay=language
		if(language in lookup):
			languageDisplay=lookup[language]
		
		allMatches=currentCase.searchUnsorted('lang:"' + language + '"')
		uniqueMatches=myItemUtility.deduplicate(allMatches)
		rows.append({
		'Language Name':languageDisplay,
		u'\u03A3 Hits':len(allMatches),
		u'\u03A3(U) Hits':len(uniqueMatches)
		})
	return rows

def getItemDateSummary():
	global currentCase,myItemUtility
	allResults={}

	items=currentCase.searchUnsorted("flag:top_level") #this may be preferable to use has-communication:1 also...

	for item in items:
		myDateTime=item.getDate()
		if(myDateTime is not None):
			key=item.getDate().toDateTime(DateTimeZone.forID(currentCase.getInvestigationTimeZone())).toString("yyyyMMdd")
			if(key not in allResults):
				allResults[key]={"all":0,"unique":0}
		else:
			print("DateTime is none?\n\t" + item.getGuid())

	for date in allResults:
		allItems=currentCase.searchUnsorted("item-date:" + date)
		allResults[date]["all"]=len(allItems)
		allResults[date]["unique"]=len(myItemUtility.deduplicate(allItems))

	rows=[]
	for date in allResults:
		if(allResults[date]["all"] > 0):
			rows.append({
				'ItemDate (no time)':date[:4] +'-' + date[4:][:2] +'-' + date[6:][:2],
				u'\u03A3 Items':allResults[date]["all"],
				u'\u03A3(U) Items':allResults[date]["unique"],
			})
	return rows
	
def getNext(myIterator):
	obj=None
	with counterMutex:
		try:
			obj=next(myIterator)
		except StopIteration:
			pass #ran out of items
	return(obj)
	
def batchObjectForUpload(object,method,myDataSetId,myTableName):
	global totalCompleted
	totalCompleted=0
	myIterator=iter(object)
	thisBatchSize=batchSize
	if(myTableName=="Items"):
		thisBatchSize=fullItemsFilters
	if(myTableName=="Items Minimum"):
		thisBatchSize=MinimumItemsFilters
	for i in range(1,activeBatches+1):
		t=Thread(target=safeBatch, args=(i,myIterator,thisBatchSize,method,myDataSetId,myTableName,))
		t.start()
		threads.append(t)
		sleep(0.5) # every so slight offset... will help with sending activeBatches amount of posts at the first time the same time.
	for t in threads:
		t.join()
	return(totalCompleted)
	
def safeBatch(i,myIterator,myBatchSize,transformMethod,myDataSetId,myTableName,):
	global totalCompleted
	global databaseTime
	global postTime
	global postTimes
	global postSizes
	totalCompletedByThisThread=0
	rows=[]
	row="undefined"
	with counterMutex:
		mutexPrint("Thread " + str(i) + " active")
	while row is not None:
		rows=[]
		start = time.time()
		while (len(rows) < myBatchSize) & (row is not None):
			row=getNext(myIterator)
			if(row is not None):
				results=None
				try:
					with databaseMutex:
						results=transformMethod(row)
				except Exception as ex:
					mutexPrint("Unknown error whilst Batching:" + ex.message)
					print(ex)
					return(None)
				finally:
					if(results is not None):
						if(isinstance(results,list)):
							#came back with multiple rows
							rows+=results
						else:
							rows.append(results)
			with counterMutex:
				if(totalCompleted > 250000):#There is a hard stop on performance at 250,000 items (120 posts per hour when over 250,000 items in a table)
					rows=[]
		end = time.time()
		with debugMutex:
			databaseTime+=(end-start)
			
		if(len(rows) > 0):
			closeWhenDone=pushDataToTable(myDataSetId,myTableName,rows)
			totalCompletedByThisThread+=len(rows)
			with counterMutex:
				mutexPrint("Thread " + str(i) + " Progress:" + str(totalCompletedByThisThread))
				totalCompleted+=len(rows)
				mutexPrint("Total Submitted:" + str(totalCompleted))
				protectedCallback("updateProgress",[totalCompleted])
			with debugMutex:
				mutexPrint("\tPost Time:\t" + str(postTime) + " seconds\n\tDatabase Time:\t" + str(databaseTime) + " seconds\n\tJSON Time:\t" + str(jsonTime) + " seconds\n\tAverage Post Time(" + str(len(postTimes))  +"):\t" + str(sum(postTimes) / len(postTimes) ) + " seconds\n\tAverage Post Size:\t" + str(sum(postSizes) / len(postSizes) ))
			#if(closeWhenDone):
			#	row=None
				#closing Thread because of Timeouts
			#	with counterMutex:
			#		mutexPrint("Thread " + str(i) + " Closing early for Timeout reasons")
			#	break;
		
	sleep(2)
	with counterMutex:
		mutexPrint("Total Records for " + str(i) + ":" + str(totalCompletedByThisThread))
		
def getSameObject(obj):
	return(obj)
	
def getDomains():
	global currentCase
	mutexPrint("Building Domain Summaries:")
	summaries={}
	for myCommItem in currentCase.searchUnsorted("has-communication:1 flag:top_level"):
		commData=myCommItem.getCommunication()
		if(commData is not None):
			myAddressList=[]
			myAddressList+=commData.getTo()
			myAddressList+=commData.getCc()
			myAddressList+=commData.getBcc()
			for myAddress in myAddressList:
				domain=myAddress.getAddress().rsplit('@',1)
				if(len(domain) > 1):
					domain=domain[1]
					if(domain not in summaries):
						summaries[domain]={
							"Domain":domain,
							"RecipientCount":0,
							"SenderCount":0
						}
					summaries[domain]["RecipientCount"]+=1
			for myAddress in commData.getFrom():
				domain=myAddress.getAddress().rsplit('@',1)
				if(len(domain) > 1):
					domain=domain[1]
					if(domain not in summaries):
						summaries[domain]={
							"Domain":domain,
							"RecipientCount":0,
							"SenderCount":0
						}
					summaries[domain]["SenderCount"]+=1
	listSummaries=[]
	for summary in summaries:
		listSummaries.append(summaries[summary])
	return(listSummaries)
	
def getTagResults():
	global currentCase,myItemUtility
	rows=[]
	
	aboveTopLevelItems=currentCase.searchUnsorted("NOT top-level-item-date:*")
	
	
	lowestPaths=[]

	for aboveTopLevelItem in aboveTopLevelItems:
		found=False
		index=0
		aboveTopLevelPathString='/'.join(aboveTopLevelItem.getLocalisedPathNames())
		for lowestPath in lowestPaths:
			if(len(aboveTopLevelPathString) > len(lowestPath)):
				if(aboveTopLevelPathString.startswith(lowestPath)):
					lowestPaths[index]=aboveTopLevelPathString
					found=True
			index+=1
		if(found==False):
			lowestPaths.append(aboveTopLevelPathString)
		
	for myTag in currentCase.getAllTags():
		total=currentCase.count('tag:"' + myTag + '"')
		for lowestPath in lowestPaths:
			if(total > 0):
				items=currentCase.searchUnsorted('tag:"' + myTag + '" AND path-name:"' + lowestPath + '"')
				if(len(items) > 0):
					rows.append({
						'Tag Name':myTag,
						'Top Level Path Name':lowestPath,
						'Evidence Name':items.iterator().next().getRoot().getName(),
						u'\u03A3 Items':len(items),
						u'\u03A3(U) Items':len(myItemUtility.deduplicate(items))
					})
				total=total-len(items)
	return rows

def getRowForMinimalFocusItem(myItem):
	return getRowForMinimal(myItem,True)

def getRowForMinimalItem(myItem):
	return getRowForMinimal(myItem,False)

def getRowForMinimal(myItem,myFocus):
	rowObject={
		"Focus Item":str(myFocus)
	}
	
	try:
		rowObject["Name"]=(myItem.getName() or "").encode('utf-8').strip()[0:4000]
		rowObject["File Size"]=str(myItem.getFileSize() or 0).encode('utf-8').strip()[0:4000]
		rowObject["Digest Input Size"]=str(myItem.getDigests().getInputSize() or 0).encode('utf-8').strip()[0:4000]
		rowObject["Audited Size"]=str(myItem.getAuditedSize() or 0).encode('utf-8').strip()[0:4000]
		rowObject["GUID"]=(str(myItem.getGuid()) or "").encode('utf-8').strip()[0:4000]
		rowObject["MD5 Digest (Latest)"]=(myItem.getDigests().getMd5() or "").encode('utf-8').strip()[0:4000]
		rowObject["Top-level"]=str(myItem.isTopLevel())
		rowObject["Audited"]=str(myItem.isAudited())
		topLevelItem=myItem.getTopLevelItem()
		if(topLevelItem is None):
			rowObject["Top-level Path Name"]=None
		else:
			if(topLevelItem.getParent() is None):
				rowObject["Top-level Path Name"]=None
			else:
				rowObject["Top-level Path Name"]=('/'.join(topLevelItem.getParent().getLocalisedPathNames() or [])).encode('utf-8').strip()[0:4000]
		if(myItem.getDate() is not None):
			rowObject["Item Date"]=str(myItem.getDate())
	except Exception as ex:
		mutexPrint('----')
		mutexPrint(ex)
		mutexPrint(myItem.getGuid())
	return rowObject

def getRowForFocusItem(myItem):
	global safeMetadata
	rowObject={}
	for myMetadataItem in safeMetadata.getMetadata():
		try:
			val=None
			if(myMetadataItem.getName()=="Digest Input Size"):
				val=str(myItem.getDigests().getInputSize())
			elif(myMetadataItem.getName()=="File Size"):
				val=str(myItem.getFileSize())
			elif(myMetadataItem.getName()=="Audited Size"):
				val=str(myItem.getAuditedSize())
			elif(myMetadataItem.getName()=="File Type"):
				val=myMetadataItem.evaluate(myItem)
			elif(myMetadataItem.getName()=="Irregular Item"): #Nuix built in Irregular Item only has [Corrupted] and [Encrypted] which is a tad frustrating... 
				irregularItemList=[]
				for key in myItem.getCustomMetadata():
					if(key.startswith("power.bi.irregular.")):
						irregularItemList.append(key.rsplit('.',1)[1])
				irregularItemList.sort()
				val=','.join(irregularItemList)
			elif(myMetadataItem.getName()=="Language"):
				val=myMetadataItem.evaluate(myItem)
				if(val==""):
					val=None
			else:
				val=myMetadataItem.evaluateUnformatted(myItem)
			if(val.__class__.__name__=="MimeType"):
				val=str(val)
			elif(val.__class__.__name__=="bool"):
				val=str(val)
			elif(val.__class__.__name__=="int"):
				val=str(val)
			elif(val.__class__.__name__=="MultiValue"):
				val=myMetadataItem.evaluate(myItem)
			elif(val.__class__.__name__=="DateTime"):
				val=str(val)
			if(val is None):
				rowObject[myMetadataItem.getLocalisedName()]=None
			elif(val=='None'):
				rowObject[myMetadataItem.getLocalisedName()]=None
			else:
				#mutexPrint(myMetadataItem.getLocalisedName())
				#mutexPrint(val.__class__.__name__)
				#mutexPrint(val)
				new_val=val.encode('utf-8').strip()[0:4000]
				if(new_val==""):
					rowObject[myMetadataItem.getLocalisedName()]=None
				else:
					rowObject[myMetadataItem.getLocalisedName()]=new_val
		except Exception as ex:
			mutexPrint('----')
			mutexPrint(ex)
			mutexPrint(myItem.getGuid())
			mutexPrint(myMetadataItem.getName())
			mutexPrint(val)
			mutexPrint(val.__class__.__name__)
			raise "uggggh"
	return rowObject

def getEntitiesForRow(myItem):
	rows=[]
	if(myItem.getTopLevelItem() is not None):
		for entityType in entityTypes:
			entities=myItem.getEntities(entityType)
			for entityValue in entities:
				rows.append({
					'Entity Name':entityType,
					'Entity Value':entityValue,
					'MD5 (Latest)':myItem.getDigests().getMd5(),
					'Top Level Path Name':'/'.join(myItem.getTopLevelItem().getParent().getLocalisedPathNames()),
					'Evidence Name':myItem.getRoot().getName(),
				})
	return rows
	
def defaultShowError(myObj):
	print(myObj)
	
def defaultUpdateMessage(message,additional):
	print(str(message) + "\t" + str(additional))
	
def defaultWorkspaceChoooser(possibleWorkspaces):
	return ""
	
def defaultHandleInteractiveRequests(message,whereTheyWantYouToGo,whenYouKnowTheyHaveGoneThereTheyWillEndUpGoHere):
	print("INTERACTIVE REQUEST:\n\tWhere Power BI wants you to go:\n\t\t" + whereTheyWantYouToGo + "\n\tCondition for when user has successfully completed action\n\t\t" + whenYouKnowTheyHaveGoneThereTheyWillEndUpGoHere)

def defaultUpdateProgress(totalCompleted):
	print("Total Completed:" + str(totalCompleted))

protectedMethods["showError"]=defaultShowError
protectedMethods["updateMessage"]=defaultUpdateMessage
protectedMethods["workspaceChoooser"]=defaultWorkspaceChoooser
protectedMethods["handleInteractiveRequests"]=defaultHandleInteractiveRequests
protectedMethods["updateProgress"]=defaultUpdateProgress
def defineCallbacks(inboundShowError,inboundUpdateMessage,inboundUpdateProgress,inboundWorkspaceChoooser,inboundHandleInteractiveRequests):
	global protectedMethods
	protectedMethods["showError"]=inboundShowError
	protectedMethods["updateMessage"]=inboundUpdateMessage
	protectedMethods["workspaceChoooser"]=inboundWorkspaceChoooser
	protectedMethods["handleInteractiveRequests"]=inboundHandleInteractiveRequests
	protectedMethods["updateProgress"]=inboundUpdateProgress
	testCallback()
	
def testCallback():
	protectedCallback("updateMessage",["Callbacks Defined",""])

def login(inboundPowerBiUsername,inboundPowerBiPassword,inboundPowerBiClientId):
	global powerBiUsername,powerBiPassword,powerBiClientId
	protectedCallback("updateMessage",["Logging in",""])
	powerBiUsername=inboundPowerBiUsername
	powerBiPassword=inboundPowerBiPassword
	powerBiClientId=inboundPowerBiClientId
	if(getToken() is None):
		return False
	else:
		return True

def export(inboundCase, inboundUtilities, inboundItems,inboundMetadataProfile,workspaceId):
	global currentCase, pushItems,focusMetadataProfile,myToken,utilities,powerBiTennantId,myItemUtility,safeMetadata
	if(myToken==""):
		protectedCallback("showError",["Login before using export features"])
		return
	currentCase=inboundCase
	pushItems=inboundItems
	utilities=inboundUtilities
	focusMetadataProfile=inboundMetadataProfile
	
	entityTypes=currentCase.getAllEntityTypes()
	
	myItemUtility=utilities.getItemUtility()
	
		
	allPossibilities=defaultColumns
	allPossibilitiesHash={}
	for possibility in allPossibilities:
		allPossibilitiesHash[possibility["name"]]=possibility["dataType"]
	if(len(pushItems) > 0):
		
		safeMetadata=utilities.getMetadataProfileStore().getMetadataProfile(focusMetadataProfile)
		
		
		myMetadata=["Name","File Size","Digest Input Size","Audited Size","GUID","MD5 Digest (Latest)","Top-level Path Name","Top-level","Audited","Item Date"]
		for myColumn in safeMetadata.getMetadata():
			myMetadata.append(myColumn.getLocalisedName())
		
		
		newColumns=[]
		for myColumn in set(myMetadata):
			if(myColumn in allPossibilitiesHash):
				newColumns.append({
					"name":myColumn,
					"dataType":allPossibilitiesHash[myColumn]
				})

		safeMetadata=safeMetadata.addMetadata("SPECIAL", "Name")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "File Size")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "Digest Input Size")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "Audited Size")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "GUID")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "MD5 Latest Digest")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "Top Level Path")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "flag.top_level")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "Audited")
		safeMetadata=safeMetadata.addMetadata("SPECIAL", "Item Date")
		datasetConfig["tables"].append({
			"name":"Items",
			"columns":newColumns
		})
		
	myMetadata=["Name","File Size","Digest Input Size","Audited Size","GUID","MD5 Digest (Latest)","Top-level Path Name","Top-level","Audited","Item Date"]
	newColumns=[]
	for myColumn in set(myMetadata):
		if(myColumn in allPossibilitiesHash):
			newColumns.append({
				"name":myColumn,
				"dataType":allPossibilitiesHash[myColumn]
			})
	
	newColumns.append({
		"name":"Focus Item",
		"dataType":"bool"
	})		
	
	datasetConfig["tables"].append({
			"name":"Items Minimum",
			"columns":newColumns
		})
	protectedCallback("updateMessage",["Validating dataset Configuration and metadata Profile",""])
	validationErrors=checkData()
	if(len(validationErrors) > 0):
		protectedCallback("showError",["\n".join(validationErrors)])
	else:
		protectedCallback("updateMessage",["initialising Export",""])
		navigateJythonIssues()
		protectedCallback("updateMessage",["Creating default dataset",""])
		defaultDataSet=createDataSet(datasetConfig)
		protectedCallback("updateMessage",["Creating this case dataset",""])
		datasetConfig["name"]=(currentCase.getName() + ":" + str(currentCase.getGuid())).replace(" ", "_")
		myDataSetId=createDataSet(datasetConfig)
		if(myDataSetId is not None):
			myTablesInDataSet=[]
			for myTable in datasetConfig["tables"]:
				myTablesInDataSet.append(myTable["name"])
			existingTables=getTablesInDataSet(myDataSetId)
			if((myTablesInDataSet==existingTables) == False):
				protectedCallback("updateMessage",["Deleting existing dataset",""])
				deleteDataSet(myDataSetId)
				protectedCallback("updateMessage",["Recreating this case dataset",""])
				myDataSetId=createDataSet(datasetConfig)
		if(myDataSetId is not None):
			protectedCallback("updateMessage",["Clearing this case dataset",""])
			purgeThreads=[]
			for myTable in myTablesInDataSet:
				#if(myTable not in ['A Summary Of History','Items Minimum']):
				t=Thread(target=clearDataInTable, args=(myDataSetId,myTable,))
				t.start()
				purgeThreads.append(t)
			for t in purgeThreads:
				t.join()
				
			mutexPrint("Pushing Database schema rows for debug tracing")
			rows=[]
			for table in datasetConfig["tables"]:
				for column in table["columns"]:
					rows.append({
						"Table Name":table["name"],
						"Column Name":column["name"],
						"Column Type":column["dataType"],
					})
			recordsUploaded=batchObjectForUpload(rows,getSameObject,myDataSetId,'Database Schema')
			
			protectedCallback("updateMessage",["Getting Reports",""])
			myReports=getReports()
			myReportNames=[]
			defaultReport=None
			myReport=None
			for myIteratingReport in myReports:
				myReportNames.append(myIteratingReport["name"])
				if(myIteratingReport["name"]==datasetConfig["name"]):
					myReport=myIteratingReport
				if(myIteratingReport["name"]==nuixDefaultDataSetForReports):
					defaultReport=myIteratingReport
				
			if(myReport is None):
				if(defaultReport is None):
					protectedCallback("updateMessage",["Preparing Default report","" + myReportLocation.replace("\\","\\\\")])
					defaultReport=importPBIX(myReportLocation,nuixDefaultDataSetForReports)
				if(defaultReport is not None):
					myReport=cloneReport(defaultReport["id"],datasetConfig["name"],myDataSetId)
			if(myReport is None):
				protectedCallback("showError",["Could not find or make default report and/or clone it?\n" + nuixDefaultDataSetForReports])
			else:
				protectedCallback("updateMessage",["Updating Case Summary",""])
				rows=[{
					'Case Name':currentCase.getName(),
					'Case GUID':currentCase.getGuid(),
					'Case Description':currentCase.getDescription(),
					'Investigator':currentCase.getInvestigator(),
					'Investigator TimeZone':currentCase.getInvestigationTimeZone(),
					'Case Location':str(currentCase.getLocation()),
					'Compound':str(currentCase.isCompound()),
					'Earliest':str(currentCase.getStatistics().getCaseDateRange().getEarliest()),
					'Latest':str(currentCase.getStatistics().getCaseDateRange().getLatest()),
				}]
				if(currentCase.isCompound()):
					for thisCase in currentCase.getChildCases():
						rows.append({
								'Case Name':thisCase.getName(),
								'Case GUID':thisCase.getGuid(),
								'Case Description':thisCase.getDescription(),
								'Investigator':thisCase.getInvestigator(),
								'Investigator TimeZone':thisCase.getInvestigationTimeZone(),
								'Case Location':str(thisCase.getLocation()),
								'Compound':str(thisCase.isCompound()),
								'Earliest':str(thisCase.getStatistics().getCaseDateRange().getEarliest()),
								'Latest':str(thisCase.getStatistics().getCaseDateRange().getLatest()),
						})
					
				pushDataToTable(myDataSetId,"A Summary Of Case",rows)
				
				
				protectedCallback("updateMessage",["Updating History Summary","Searching"])
				summaryResults=getHistory()
				
				protectedCallback("updateMessage",["Updating History Summary","Uploading"])
				recordsUploaded=batchObjectForUpload(summaryResults,getSameObject,myDataSetId,'A Summary Of History')
				
				protectedCallback("updateMessage",["Updating Entities Summary",""])
				recordsUploaded=batchObjectForUpload(pushItems,getEntitiesForRow,myDataSetId,'A Summary Of Entities for Focus Items')
				
				
				protectedCallback("updateMessage",["Updating Irregular Items Summary",""])
				
				pushDataToTable(myDataSetId,'A Summary Of Irregular Items',getIrregularItemSummary())
				
				protectedCallback("updateMessage",["Updating Tag Summary","Searching"])
				summaryResults=getTagResults()
				protectedCallback("updateMessage",["Updating Tag Summary","Uploading"])
				recordsUploaded=batchObjectForUpload(summaryResults,getSameObject,myDataSetId,'A Summary Of Tags')
				
				protectedCallback("updateMessage",["Updating Domain Commmunication Summary","Searching"])
				summaryResults=getDomains()
				protectedCallback("updateMessage",["Updating Domain Commmunication Summary","Uploading"])
				recordsUploaded=batchObjectForUpload(summaryResults,getSameObject,myDataSetId,'A Summary Of Domains')
				
				protectedCallback("updateMessage",["Updating Size Summary","All"])
				pushDataToTable(myDataSetId,"A Summary Of Size",getSizeRows())
				
				
				protectedCallback("updateMessage",["Updating File Type Summary",""])
				pushDataToTable(myDataSetId,'A Summary Of File Types',getFileTypeSummary())
				
				protectedCallback("updateMessage",["Updating Language Summary",""])
				pushDataToTable(myDataSetId,'A Summary Of Languages',getLanguageSummary())
				
				protectedCallback("updateMessage",["Updating Item Dates Summary","Searching"])
				summaryResults=getItemDateSummary()
				protectedCallback("updateMessage",["Updating Item Dates Summary","Uploading"])
				recordsUploaded=batchObjectForUpload(summaryResults,getSameObject,myDataSetId,'A Summary Of Item Dates')
				
				protectedCallback("updateMessage",["Focus Items","Uploading Focus items with minimum fields"])
				recordsUploaded=batchObjectForUpload(pushItems,getRowForMinimalFocusItem,myDataSetId,"Items Minimum")
				
				protectedCallback("updateMessage",["Focus Items","Uploading Focus items with full fields"])
				recordsUploaded=batchObjectForUpload(pushItems,getRowForFocusItem,myDataSetId,"Items")
				
				protectedCallback("updateMessage",["Minimum Items","Collecting GUIDs"])
				bigGuidQuery=[]
				for item in pushItems:
					digest=item.getDigests().getMd5()
					if(digest is not None):
						bigGuidQuery.append(digest)
					
				protectedCallback("updateMessage",["Minimum Items","Finding all non-focus items"])
				if(len(bigGuidQuery) > 0):
					allOtherItems=currentCase.searchUnsorted('NOT md5:("' + '" OR "'.join(bigGuidQuery) + '")')
				else:
					allOtherItems=currentCase.searchUnsorted('')
				
				if(len(allOtherItems) > 0):
					if(len(allOtherItems) > 250000):
						protectedCallback("updateMessage",["Minimum Items","Duplicating (attempting to get below 250,000 records"])
						allOtherItems=myItemUtility.deduplicate(allOtherItems)
					
				if(len(allOtherItems) > 0):
					if(len(allOtherItems) < 250000):
						protectedCallback("updateMessage",["Minimum Items","Uploading non-focus items with minimum fields"])
						recordsUploaded=batchObjectForUpload(allOtherItems,getRowForMinimalItem,myDataSetId,"Items Minimum")
					else:
						protectedCallback("updateMessage",["Minimum Items","Uploading 250,000 non-focus items with minimum fields"])
						recordsUploaded=batchObjectForUpload(allOtherItems,getRowForMinimalItem,myDataSetId,"Items Minimum")
					
				
				if(myReport is None):
					protectedCallback("updateMessage",["Something bad happened creating default/cloned report?",""])
				else:
					#SECURED REPORT LOCATION, will require sign in.
					reportLocation='https://app.powerbi.com/reportEmbed?reportId=' + str(myReport["id"]) + '&autoAuth=true&ctid=' + str(powerBiTennantId)
					protectedCallback("handleInteractiveRequests",["Your Report is prepared", reportLocation,"https://"])
					
					#This work was put aside because Secured Report seemed the better option.
					#print("Literal Report Location:\n" + reportLocation)
					#embeddedTokenContext=generateEmbeddedReportToken(myReport["id"],myDataSetId)
					#embeddedTokenContext={u'tokenId': u'955c14a0-29c3-4661-98c9-81d1ad0346e9', u'@odata.context': u'http://wabi-west-us-redirect.analysis.windows.net/v1.0/myorg/groups/c962ffe6-6a46-4bc7-a979-fee3836a4354/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.GenerateTokenResponse', u'token': u'H4sIAAAAAAAEAB2WtQ70CBKE3-VPfZJxDCdtYGZmZ6YxM3t1736zm3fQquqqr__-Y6VPP6XFn__-kY-0SkUWbVcgA0C3Jm2lKI-kAnaT852QNfXsaSesH0AjENxkbGTUvrOadkt1BJigjiMBGpKrgm_NZDFe6OFwsGen_MAp3_iZkw1joqnnpRHhokvMp5yZJEiAXFabzM33fBFD1pO4Yrh0eqieyfHWUyobsc7o8pyNVLstV22EKW3QorCQi9aRQZzhXOc3BV4BKbfqDauO9hqdTuoBkdM_oSqSkg1VLXvxnrqPFg8vC6lrit0bt2PErpN0AMZW5RnMhLY_oKyrQ_tCm_ORFb9SNoMRlQGaigydnrhKONBNrVYsHZVa1jbOi7CqygKDtOBI2bJJcFGw2e2dGvuzNcEoIYEIY_HGo19HgTiUv25mDtVu6CeDb8qzN3bi_PQ7aN2GcKb1wgXDVxMn9bcgiU0J7h1ORklNb-PSdmlDwO7XG_JLeiaDThZoLGgAW0kokR64KnTPl7yAafmw0mwbwceozw1pYtmCHyr01ioA-japOh6TeCBbCGMynWgySkMJbAO4epQTpcDJSKpZw3zVz-zwiy4VAKYkKb880iAbkfp9nW7jlG8MqQhZ7DybSzjLO8jRGLXH4qCZfORx10ajJJEsOrggGSGcmMuG3YTY71SUQNZ4C--wbDN9CaNF9NTlbpXnurpuEobX6QerDwuWmOOi8CyvN3S9joLBQACAt2gAe6RO3v16I_DRDPUuWghqFOYIErCIWrft1Z5snEgGMA1sN4yKW1TlefOvk2tda9g0JSbhiRnsYwoR4g6aUGsxfUYEfvkqhAeiHzrqgTGcdfXgyqhxxVnSwTK00JAvKMUtsncFxAOyPr3MTqH4UOQkZTTYrTxYi4VK3ditu3i6pL91BxUuazxCL6eSbl0mnz7nhxmdxo4LfLwh0L2IysP42280ghYnWyW_jLAmndZMuSSIWmcDGf-qx05oSsd37KDS_aTXwBBLEIqkul-yBKJV3k2HEolPFt1MrfIBylnCV5j4mj2hWciaHzCDeZuorhqOuCs-BkS21fnPADawc8ns7MU94kRvntaocGjAWWy--gcEwBK_KYt-cT0UAEvYfE-u1Z7iCk4IbEBZNGFMI4GhlMuldcnkv9f0vobwGSZvdi0DQpbW_bodOzIKVxsYKSGH3N9xTqnM46d5yz269a3ttQFxXVY3jWA1V5kj7zMTPytnKHmIo25nowq0Vky5voDX3XeWUjKCszROT7XKa08iMhE1Mc3aqGulSzGIqW8sElHathma3jphdJ4yGKesrhfsEhMbxEv-aS_-Ku8L2WYE_OxnjKyJr-rz5fohdhq8y1XGUOg1T7ca5ItUXf7C-bvPiI6UMHLbuxt5GjH0zgfIq2lHmzZVmxwzuGvHDq_BsxzT7NpahTbt-sFnbt1CI-0XKX1K2S6GFYv9p4TRirBtRDpV5rJy6PN0v3umztfaHNkFH81DZNC15l5z2nEAqNmKQmypfA1Cizlce88qJGl-0e2MSwzHA-8y3DCkj_UMA8P6kkDT0WbamBEt2YeQBiwDwNchxqumCC5DfrlT3yQ-mDBY2VoV4Q1nLMDTfU6i4aIv-ZgfA2N3uONzg5F2ULF2UDRL9tqkktpAoU8Psmsd5e3aVJyTJiQqZG2puRKF-uyhBeIzLl4SYgB7YCJ5psrBucnOYAVWFXZ9dln0qH3J7YgD5gLLg90F8u6RPs9KK5pINOojiUaN61N-kKCyvqf__aCFYjnha_LrhDwL08PkZpt0bUJJTTAXjH3LzfaKt8ZZlq676yQgdWVcgV7qb1N7-L1Cr6ixtyK1QBCFo8_IXqa2uNrpD8Ti6a3qDlAHb_mxV281IZpY67xCLy01d6PXp-741QF1rpzsjeQBNdpV0Mr4pA9acfuH1Ri4WBJWwrRWRTND-Or0_NLde3dy0cEo_T1z0Za-tES7tGAlH9aEhp7PRYF0YMnwC40nBMK_vgvu4P0W3JhC-orGJWgd-IasV10AsXK81Nby-r3_8kae0Bq1c-qNP4E1vG5SwpJJxGT46Zkcv1A5RGEy4cbFg4Cosv2MY8XmBx9lFN8p_p4v6tU9pEZJeisfuG0RuAtigaaguoqwHOIvbUz0AbE-ifa9wMxhB_eU1XPiV_KXieXFChyA7GoDKWaU531jy3JNtkei1xr3h90M-XKRV7PBJsWcFM4K-YnORb2qIsJYT2a4MmrJ-Y7Y9qRXVcF2-5cfwYA0S9wjlS5w4p5AVFLBtpIyyR8-_Dbq6ZBY09svLnIAvfsQmhaXRKgHemagpCDQeF-sS1LU9xKLV64rCaQm_Dm0og6o7WsoGsL-689__rDrM--TWj6_14fmE29wQMepyQcdpPeyHFL10XONIVQXE9-8xyxBXmvKZpXOJkQup7V3B3f3pR-4Ri9NsvXIvq26yDvL5FYrQRgqFZujype5tTyd5y32SeCX5W9t2_VGBLmz8EJbJ2x1IQ46eUentfrVGZZQx5VoYBP1B01lhrItUgVvppx6SmMl4zGgLje1LciRX6V0h8t4tk-sCEH8CYffr1J8URBaE6JaFJPUgYXvt4WqxV9Xuip-Z6LUd5Hmedovbgh5sCXVGjTjfr5me_54PKpbM5pT8JXU4sDxjSGVd5VenE9q1MAC4juP237IdOPQboPY5pfsJUvp1EswfiXcZ1rlsFMUA1uUktVf_8r8zHW5ysFP5eSb49Fq-T1DaryHGOCUOC7975TbVGO6H2v5G5vudWf96_RZ4pxs-PxSm3eiecIi8tT76uoGAPExDdi7QpcSL9y-F2IgiH2MacbjlRAzHeoXUJaU5l2VRN65jusyBtt-2uylbcz7hSgPP9ijQ0TBUXxwnk1WSfbw0sw64vdcf3o1AJ6aa0M--cqy8-EYOUwCtOp9RmNiMCZYwyrCqyMpMEToL9xcdhswrj0OOcan-TOhbxtj840Xvt-z5xop_vAYnhPXR0viaEdpZGn7jKJIsFpZID1AgyJlaCSab_5ULjEV1x3DVrDtGlF6TRQX1l5JKzLJshTyFP_MJmMbkKC5ujsyOZHCSIZA0o_-0LHLlZyn3GaFfl0ecGJRZWRj_8j8v_8Dpv5xQe4LAAA=', u'expiration': u'2020-01-21T20:54:21Z'}
					#print(embeddedTokenContext)
					#from com.teamdev.jxbrowser.chromium import LoadURLParams
					#browser.loadURL(LoadURLParams("https://app.powerbi.com/groups/c962ffe6-6a46-4bc7-a979-fee3836a4354/reports/a5a3bec9-8f98-4811-8256-ed905dad996d/ReportSection",json.dumps({'Authorization': 'Bearer ' + embeddedTokenContext["token"]}), "Content-Type: application/json"))
	print("Script Execution Complete")

print("Power BI Module loaded")