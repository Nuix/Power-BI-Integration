## If any of these values are blank and you have an interactive case open you will be prompted.
## if any are blank and you don't have an interactive session... no prompt.
powerBiUsername="example@nuix.com" #TODO
powerBiPassword="" #TODO
powerBiClientId="0853dfd6-5564-4765-bbd2-8196fe6c89da" #TODO, nuix key should work for externals too
powerBiFocusItems=currentSelectedItems
metadataProfile="" #TODO
workspaceId="my" #TODO, leave as 'my' for my workspace setting

### do not touch below this line!!!!!!

import os,sys,inspect,traceback,time
from os import path
runningDir = os.path.dirname(os.path.abspath(inspect.getfile(lambda: None)))
print(runningDir)
sys.path.append(runningDir)
try:
	import Power_bi
	pass
except:
	print(str(sys.exc_info()[1]))
	print(traceback.format_exc())

#if any of the above values are "" and you are in an interactive session... you will be prompted!
successful=False
if(window):
	try:
		import PowerBiInteractive
	except:
		print(str(sys.exc_info()[1]))
		print(traceback.format_exc())
	Power_bi.defineCallbacks(
		PowerBiInteractive.showError,
		PowerBiInteractive.updateMessage,
		PowerBiInteractive.updateProgress,
		PowerBiInteractive.workspaceChoooser,
		PowerBiInteractive.handleInteractiveRequests
	)
	
	if(("" in [powerBiUsername,powerBiPassword,powerBiClientId])):
			if(PowerBiInteractive.init(window,runningDir,currentSelectedItems,currentCase,False)):
				powerBiUsername=PowerBiInteractive.powerBiUsername
				powerBiPassword=PowerBiInteractive.powerBiPassword
				powerBiClientId=PowerBiInteractive.powerBiClientId
				successful=True
	else:
		try:
			if(PowerBiInteractive.init(window,runningDir,currentSelectedItems,currentCase,True)):
				successful=True
		except:
			print(str(sys.exc_info()[1]))
			print(traceback.format_exc())
	if(successful):
		if (metadataProfile==""):
			metadataProfile=PowerBiInteractive.metadataProfileChooser()
		if(powerBiFocusItems is None): #to cope with some niche areas on console launching.
			powerBiFocusItems=[]
		if(len(powerBiFocusItems)==0):
			powerBiFocusItems=PowerBiInteractive.getFocusItems()
		if not (workspaceId=="my"):
			workspaceId=PowerBiInteractive.workspaceChoooser()
else:
	successful=True

if(successful):	
	if("" in [powerBiUsername,powerBiPassword,powerBiClientId,metadataProfile,workspaceId]):
		print("You are missing required fields...")
		for field in [powerBiUsername,powerBiPassword,powerBiClientId,metadataProfile,workspaceId]:
			print(field)
	else:
		if (workspaceId=="my"):
			workspaceId=""
		
		if(Power_bi.login(powerBiUsername,powerBiPassword,powerBiClientId)):
			Power_bi.export(currentCase,utilities,powerBiFocusItems,metadataProfile,workspaceId)
		#	pass