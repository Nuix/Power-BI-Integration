import time
from time import sleep
from com.teamdev.jxbrowser.chromium import Browser
from com.teamdev.jxbrowser.chromium.swing import BrowserView
from javax.swing import JPanel
from java.awt import GridLayout
from com.teamdev.jxbrowser.chromium.events import LoadAdapter

powerBiUsername="!"
powerBiPassword="!"
powerBiClientId="!"
runningDir="!"
currentSelectedItems=[]
currentCase=None
class myLoadAdapter(LoadAdapter):
	def __init__(self,):
		self._status="init"
		self._expectedPrefx="http"
		self._lastURL=""

	def onDocumentLoadedInFrame(self,myFrameLoadEvent):
		self._status="DocumentLoadedInFrame"

	def onDocumentLoadedInMainFrame(self,myLoadEvent):
		self._status="DocumentLoadedInMainFrame"

	def onFailLoadingFrame(self,myFailLoadingEvent):
		self._status="FailLoadingFrame"

	def onFinishLoadingFrame(self,myFinishLoadingEvent):
		if (myFinishLoadingEvent.isMainFrame()):
			loadedURL=myFinishLoadingEvent.getBrowser().getURL()
			if(loadedURL.startswith(self._expectedPrefx)):
				self._lastURL=loadedURL
				self._status="FinishLoadingFrame"
		else:
			self._status="FinishLoadingAFrame"

	def onProvisionalLoadingFrame(self,myProvisionalLoadingEvent):
		self._status="ProvisionalLoadingFrame"

	def onStartLoadingFrame(self,myStartLoadingEvent):
		self._status="StartLoadingFrame"

	def waitUntilFinishedLoading(self):
		i=0
		while((self._status not in ["FailLoadingFrame","FinishLoadingFrame"]) & (i < 20)):
			i+=1
			sleep(0.2)
			print("Waiting for page to load... " + self._status)

		print("Finished loading with status:" + self._status)
		return(self._status=="FinishLoadingFrame")
	
	def setWaitCondition(self,prefix):
		self._expectedPrefx=prefix
		self._status="QueuedFrame"
		self._lastURL=""
		
	def getLastURL(self):
		return self._lastURL

initLoader=myLoadAdapter()
browser=Browser()
browser.addLoadListener(initLoader)

def showLoadingPage():
	global jsWindow,powerBiClientId,powerBiUsername,powerBiPassword,runningDir
	initLoader.setWaitCondition("file://")
	browser.loadURL(runningDir + '\LandingFilterPage.html')
	if(initLoader.waitUntilFinishedLoading()):
		jsWindow = browser.executeJavaScriptAndReturnValue("window")
		#so.... jxbrowser bridge is broken for scriptContext objects... so I'm forced to watch instead of proper method calls.
		jsWindow.asObject().setProperty("workspaceId","!")
		jsWindow.asObject().setProperty("clientId",powerBiClientId)
		jsWindow.asObject().setProperty("username",powerBiUsername)
		jsWindow.asObject().setProperty("password",powerBiPassword)
		jsWindow.asObject().setProperty("metadataProfile","!")
		jsWindow.asObject().setProperty("focusTag","!")
		return True
	else:
		return False

def showError(myObj):
	browser.executeJavaScript('showError("' + str(myObj).replace("'",'"').replace('\r','').replace('\n', '<br />').replace('\t', '    ').replace("\\","\\\\") +'")')
	print(myObj)
	



timeSinceLastMessage=time.time()
lastMessage=""
stageNumber=0
myDataSetId=None
pendingReportRows=[]
def updateMessage(message,additional):
	global lastMessage
	global timeSinceLastMessage
	global myDataSetId
	global stageNumber
	global pendingReportRows
	browser.executeJavaScript('hideDialog("' + message + '","' + additional +'")')
	if(lastMessage != message):
		"""elapsed_time = time.time() - timeSinceLastMessage
		if(lastMessage!=""):
			stageNumber=stageNumber+1
			totalStages=21
			if(totalStages <= stageNumber):
				totalStage=stageNumber
			pendingReportRows.append({
				'Current Stage':str(lastMessage),
				'Current Stage Number':str(stageNumber),
				'Total Stages':str(totalStages),
				'Seconds taken':str(int(elapsed_time))
			})
			if(myWorkspace is not None):
				if(myDataSetId is not None):
						if(stageNumber >= 9): #after table clear
							pushDataToTable(myDataSetId,'Report Progress',pendingReportRows)
							pendingReportRows=[]"""
		lastMessage=message
		timeSinceLastMessage=time.time()
	print(str(message) + "\t" + str(additional))

def updateProgress(totalCompleted):
	browser.executeJavaScript('updateProgress("' + str(totalCompleted) + '")')
		
def workspaceChoooser(possibleWorkspaces):
	browser.executeJavaScript('showDialog("chooseWorkspace")')
	
	for myDiscoveredWorkspace in possibleWorkspaces:
		jscommand='addTableRow("workspaceFilter",["' + str(myDiscoveredWorkspace["name"]) + '","' + str(myDiscoveredWorkspace["isReadOnly"]) + '","' + str(myDiscoveredWorkspace["isOnDedicatedCapacity"]) + '","' + myDiscoveredWorkspace["id"] + '"])'
		browser.executeJavaScript(jscommand)
		
	
	workspaceId=str(jsWindow.asObject().getProperty("workspaceId"))
	while(workspaceId=="!"):
		sleep(0.2)
		workspaceId=str(jsWindow.asObject().getProperty("workspaceId"))
	return workspaceId

def metadataProfileChooser():
	for myMetadataProfile in currentCase.getMetadataProfileStore().getMetadataProfiles():
		jscommand='addTableRow("metadataFilter",["' + str(myMetadataProfile.getName()) + '"])'
		browser.executeJavaScript(jscommand)
	browser.executeJavaScript('showDialog("chooseMetadataProfile")')
	metadataProfile=str(jsWindow.asObject().getProperty("metadataProfile"))
	while(metadataProfile=="!"):
		sleep(0.2)
		metadataProfile=str(jsWindow.asObject().getProperty("metadataProfile"))
	return metadataProfile
	
def getFocusItems():
	global currentSelectedItems,currentCase
	pushItems=currentSelectedItems
	focusTag="!"
	if(pushItems is None):
		pushItems=[]
		focusTag="!"
	
	if(len(pushItems) > 0):
		updateMessage("Skipped Focus Items","")
		focusTag="Selected Items"
		print("Items selected for Focus Items")
	else:
		print("Tag choice to be presented Focus Items")
		updateMessage("Getting Tags","")
		for myDiscoveredTag in currentCase.getAllTags():
			jscommand='addTableRow("tagFilter",["' + str(myDiscoveredTag) + '"])'
			browser.executeJavaScript(jscommand)
		
		print("Tag choices showing")
		browser.executeJavaScript('showDialog("chooseTag")')
		
		focusTag=str(jsWindow.asObject().getProperty("focusTag"))
		while(focusTag=="!"):
			sleep(0.2)
			focusTag=str(jsWindow.asObject().getProperty("focusTag"))
		print("Ready to choose focus")
		updateMessage("Searching for tagged items","")
		pushItems=currentCase.searchUnsorted('tag:"' + focusTag + '"')
	return pushItems
	
def handleInteractiveRequests(message,whereTheyWantYouToGo,whenYouKnowTheyHaveGoneThereTheyWillEndUpGoHere):
	initLoader.setWaitCondition(whenYouKnowTheyHaveGoneThereTheyWillEndUpGoHere)
	browser.loadURL(whereTheyWantYouToGo)
	initLoader.waitUntilFinishedLoading()
	if not ("Your Report is prepared"==message):
		showLoadingPage()
	return True
	

def init(window,inboundRunningDir,inboundItems,inboundCase,preconfigured):
	global powerBiPassword,powerBiUsername,powerBiClientId,runningDir,currentCase
	currentCase=inboundCase
	currentSelectedItems=inboundItems
	runningDir=inboundRunningDir
	
	body=JPanel(GridLayout(0,1))
	print("popping tab")
	window.addTab("Power BI",body)
	#browser.cookieStorage.deleteAll()
	browserview=BrowserView(browser)
	body.add(browserview)

	if(preconfigured):
		if not (showLoadingPage()):
			showError("Error in loading Landing page... investigate that please")
			return True
		return False
	else:
		if(showLoadingPage()):
			browser.executeJavaScript('showDialog("loginDialog")')
			while(powerBiPassword=="!"):
				sleep(0.2)
				powerBiPassword=str(jsWindow.asObject().getProperty("password"))
				powerBiUsername=str(jsWindow.asObject().getProperty("username"))
				powerBiClientId=str(jsWindow.asObject().getProperty("clientId"))
			return True
		else:
			showError("Error in loading Landing page... investigate that please")
			return False
	return False