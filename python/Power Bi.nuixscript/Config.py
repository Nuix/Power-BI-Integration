'''
===========================
Tables:
=========

A Summary Of Case - For Case Summary, if compound there will be more than one row
A Summary Of Size - Overall Size summaries.
A Summary Of Domains - For Domain Summary
A Summary Of History - For Case Summary
A summary Of Languages - For Case Summary
A summary Of Irregular Items - For Case Summary
A Summary Of File Types - For Case Summary, including kind for gap analysis report
A Summary Of Irregular Items - For Case Summary
A Summary Of Item Dates - Time Line, for gap analysis... grouped by date, no time used to bucket this a bit better, may be worthwhile to customise the bucket size (purely for upload and granuality in the interface)
A Summary Of Tags - Tag breakdown, including Top Level Path Name and Evidence Name to provide reporting breakdowns.
A Summary Of Terms - Text term statistics, for word cloud tab... ~reminder to remove stop words~
Report Progress - Used to track the status of this report generation

===========================
Opt in, not used in report unless chosen explicitly by the user
=========

Items - Will be slow... ridiculously slow if all metadata is chosen, largely because of the time taken to post and not necessarily the time to generate in case.

===========================
Definitions:
=========

\u03A3 = Sum
\u03A3(U) = Unique Sum

'''

nuixDefaultDataSetForReports='Nuix Default - Do not delete' 
datasetConfig={
	'defaultMode':'Push', #unclear, but community states that streaming is better resourced for 429 issues... Push and PushStream are the two options available to our solution.
	'name': nuixDefaultDataSetForReports,
	'tables': [
		{
			#===========================
			'name':'A Summary Of Case',
			#=========
			'columns':[
				{
					'name':'Case Name',
					'dataType':'string'
				},
				{
					'name':'Case GUID',
					'dataType':'string'
				},
				{
					'name':'Case Description',
					'dataType':'string'
				},
				{
					'name':'Investigator',
					'dataType':'string'
				},
				{
					'name':'Investigator TimeZone',
					'dataType':'string'
				},
				{
					'name':'Case Location',
					'dataType':'string'
				},
				{
					'name':'Compound',
					'dataType':'string'
				},
				{
					'name':'Earliest',
					'dataType':'string'
				},
				{
					'name':'Latest',
					'dataType':'string'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Size',
			#=========
			'columns':[
				{
					'name':'Summary Title',
					'dataType':'string'
				},
				{
					'name':'Items',
					'dataType':'Int64'
				},
				{
					'name':'(U) Items',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3 Size',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3(U) Size',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of History',
			#=========
			'columns':[{
					'name':'StartDate',
					'dataType':'DateTime'
				},
				{
					'name':'User',
					'dataType':'string'
				},
				{
					'name':'Action',
					'dataType':'string'
				},
				{
					'name':'Total Actions',
					'dataType':'Int64'
				},
				{
					'name':'Total Affected Items',
					'dataType':'Int64'
				},
				
			]
		},
		{
			#===========================
			'name':'A Summary Of File Types',
			#=========
			'columns':[
				{
					'name':'File Type Name',
					'dataType':'string'
				},
				{
					'name':'Kind Name',
					'dataType':'string'
				},
				{
					'name':u'\u03A3 Hits',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3(U) Hits',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Irregular Items',
			#=========
			'columns':[
				{
					'name':'Irregular Filter',
					'dataType':'string'
				},
				{
					'name':u'\u03A3 Hits',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3(U) Hits',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Languages',
			#=========
			'columns':[
				{
					'name':'Language Name',
					'dataType':'string'
				},
				{
					'name':u'\u03A3 Hits',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3(U) Hits',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Item Dates',
			#=========
			'columns':[
				{
					'name':'ItemDate (no time)',
					'dataType':'DateTime'
				},
				{
					'name':u'\u03A3 Items',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3(U) Items',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Domains',
			#=========
			'columns':[
				{
					'name':'Domain',
					'dataType':'string'
				},
				{
					'name':'SenderCount',
					'dataType':'Int64'
				},
				{
					'name':'RecipientCount',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Tags',
			#=========
			'columns':[
				{
					'name':'Tag Name',
					'dataType':'string'
				},
				{
					'name':'Top Level Path Name',
					'dataType':'string'
				},
				{
					'name':'Evidence Name',
					'dataType':'string'
				},
				{
					'name':u'\u03A3 Items',
					'dataType':'Int64'
				},
				{
					'name':u'\u03A3(U) Items',
					'dataType':'Int64'
				},
			]
		},
		{
			#===========================
			'name':'A Summary Of Entities for Focus Items',
			#=========
			'columns':[
				{
					'name':'Entity Name',
					'dataType':'string'
				},
				{
					'name':'Entity Value',
					'dataType':'string'
				},
				{
					'name':'MD5 (Latest)',
					'dataType':'string'
				},
				{
					'name':'Top Level Path Name',
					'dataType':'string'
				},
				{
					'name':'Evidence Name',
					'dataType':'string'
				},
				
			]
		},
		{
			#===========================
			'name':'Report Progress',
			#=========
			'columns':[
				{
					'name':'Current Stage',
					'dataType': 'string'
				},
				{
					'name':'Current Stage Number',
					'dataType': 'Int64'
				},
				{
					'name':'Total Stages',
					'dataType': 'Int64'
				},
				{
					'name':'Seconds taken',
					'dataType': 'Int64'
				},
			],
		},
		{
			#===========================
			'name':'Database Schema',
			#=========
			'columns':[
				{
					'name':'Table Name',
					'dataType': 'string'
				},
				{
					'name':'Column Name',
					'dataType': 'string'
				},
				{
					'name':'Column Type',
					'dataType': 'string'
				},
			],
		}
	]
}


defaultColumns=[
	#These will be removed if not found in metadata Profile supplied. Default is all and work back...
	{
		'name':'Binary Stored',
		'dataType': 'bool'
	},
	#MD5 Latest Digest
	{
		'name':'MD5 Digest (Latest)',
		'dataType': 'string'
	},
	#Communication Date
	{
		'name':'Communication Date',
		'dataType': 'DateTime'
	},
	#Entity.personal-id-num
	{
		'name':'Entity: Personal ID',
		'dataType': 'string'
	},
	#Digest Input Size
	{
		'name':'Digest Input Size',
		'dataType': 'Int64'
	},
	#Chained Near-Duplicate Guids
	{
		'name':'Chained Near-Duplicate GUIDs',
		'dataType': 'string'
	},
	#Top Level GUID
	{
		'name':'Top-level GUID',
		'dataType': 'string'
	},
	#Duplicate Count
	{
		'name':'Duplicate Count',
		'dataType': 'Int64'
	},
	#flag.deleted
	{
		'name':'Deleted',
		'dataType': 'bool'
	},
	#Entity.money
	{
		'name':'Entity: Money',
		'dataType': 'string'
	},
	#flag.text_not_processed
	{
		'name':'Text Not Processed',
		'dataType': 'bool'
	},
	#Tags
	{
		'name':'Tags',
		'dataType': 'string'
	},
	#flag.partially_recovered
	{
		'name':'Deleted File - Some Blocks Available',
		'dataType': 'bool'
	},
	#Parent Name
	{
		'name':'Parent Name',
		'dataType': 'string'
	},
	#Bcc
	{
		'name':'Bcc',
		'dataType': 'string'
	},
	#flag.file_data
	{
		'name':'File Data',
		'dataType': 'bool'
	},
	#flag.partially_processed
	{
		'name':'Partially Processed',
		'dataType': 'bool'
	},
	#Position
	{
		'name':'Position',
		'dataType': 'string'
	},
	#Entity.country
	{
		'name':'Entity: Country',
		'dataType': 'string'
	},
	#Audited Size
	{
		'name':'Audited Size',
		'dataType': 'Int64'
	},
	#File Type
	{
		'name':'File Type',
		'dataType': 'string'
	},
	#Text Path
	{
		'name':'Text Path',
		'dataType': 'string'
	},
	#Text Summary
	{
		'name':'Text Summary',
		'dataType': 'string'
	},
	#Item Set Duplicate Paths
	{
		'name':'Item Set Duplicate Paths',
		'dataType': 'string'
	},
	#ItemSets
	{
		'name':'Item Sets',
		'dataType': 'string'
	},
	#SHA-256 Original Digest
	{
		'name':'SHA-256 Digest (Original)',
		'dataType': 'string'
	},
	#flag.irregular_file_extension
	{
		'name':'Bad Extension',
		'dataType': 'bool'
	},
	#Entity.phone-number
	{
		'name':'Entity: Phone Number',
		'dataType': 'string'
	},
	#SkinTone
	{
		'name':'Skin-tone',
		'dataType': 'string'
	},
	#SSDeep Fuzzy Hash
	{
		'name':'SSDeep Fuzzy Hash',
		'dataType': 'string'
	},
	#Material Child Names
	{
		'name':'Material Child Names',
		'dataType': 'string'
	},
	#PhotoDNA Robust Hash
	{
		'name':'PhotoDNA Robust Hash',
		'dataType': 'string'
	},
	#flag.inline
	{
		'name':'Inlined',
		'dataType': 'bool'
	},
	#Top Level Item Date
	{
		'name':'Top-level Item Date',
		'dataType': 'DateTime'
	},
	#flag.unallocated_space
	{
		'name':'Unallocated Space',
		'dataType': 'bool'
	},
	#Child Material Count
	{
		'name':'Child Material Count',
		'dataType': 'Int64'
	},
	#Link
	{
		'name':'Linked Item',
		'dataType': 'string'
	},
	#AutomaticClassifierConfidence
	{
		'name':'Automatic Classifier Confidence',
		'dataType': 'string'
	},
	#Markup Sets
	{
		'name':'Markup Sets',
		'dataType': 'string'
	},
	#flag.physical_file
	{
		'name':'Physical File',
		'dataType': 'bool'
	},
	#Parent GUID
	{
		'name':'Parent GUID',
		'dataType': 'string'
	},
	#Duplicate Paths
	{
		'name':'Duplicate Paths',
		'dataType': 'string'
	},
	#flag.text_stripped
	{
		'name':'Text-stripped',
		'dataType': 'bool'
	},
	#ClusterPivots
	{
		'name':'Cluster Pivots',
		'dataType': 'string'
	},
	#Near-Duplicate Guids
	{
		'name':'Near-Duplicate GUIDs',
		'dataType': 'string'
	},
	#flag.identified_disabled
	{
		'name':'Identification Disabled',
		'dataType': 'bool'
	},
	#URI
	{
		'name':'URI',
		'dataType': 'string'
	},
	#File Size
	{
		'name':'File Size',
		'dataType': 'Int64'
	},
	#ClusterThreadIndexes
	{
		'name':'Cluster Thread Indexes',
		'dataType': 'string'
	},
	#Audited
	{
		'name':'Audited',
		'dataType': 'bool'
	},
	#Exclusion
	{
		'name':'Exclusion',
		'dataType': 'string'
	},
	#Deep Learning Classification
	{
		'name':'Deep Learning Classification',
		'dataType': 'string'
	},
	#PDF Page Count
	{
		'name':'mutexPrinted Image Page Count',
		'dataType': 'Int64'
	},
	#Binary Path
	{
		'name':'Binary Path',
		'dataType': 'string'
	},
	#flag.front_load_mutexPrinted_imaging_failed
	{
		'name':'Front Load mutexPrinted Imaging Failed',
		'dataType': 'bool'
	},
	#Item Set Duplicate Count
	{
		'name':'Item Set Duplicate Count',
		'dataType': 'Int64'
	},
	#Entity.url
	{
		'name':'Entity: URL',
		'dataType': 'string'
	},
	#ClusterPivotResemblances
	{
		'name':'Cluster Pivot Resemblances',
		'dataType': 'string'
	},
	#Chained Near-Duplicate Paths
	{
		'name':'Chained Near-Duplicate Paths',
		'dataType': 'string'
	},
	#Shannon Entropy
	{
		'name':'Shannon Entropy',
		'dataType': 'double'
	},
	#flag.licence_restricted
	{
		'name':'Licence Restricted',
		'dataType': 'bool'
	},
	#Entity.credit-card-num
	{
		'name':'Entity: Credit Card Number',
		'dataType': 'string'
	},
	#flag.failed
	{
		'name':'Failed',
		'dataType': 'bool'
	},
	#Item Set Duplicate Custodian Set
	{
		'name':'Item Set Duplicate Custodian Set',
		'dataType': 'string'
	},
	#Irregular Item
	{
		'name':'Irregular Item',
		'dataType': 'string'
	},
	#Entity.email
	{
		'name':'Entity: Email',
		'dataType': 'string'
	},
	#flag.not_audited
	{
		'name':'Unaudited',
		'dataType': 'bool'
	},
	#Graph Database
	{
		'name':'Graph Database',
		'dataType': 'bool'
	},
	#MD5 Digest
	{
		'name':'MD5 Digest',
		'dataType': 'string'
	},
	#flag.reloaded
	{
		'name':'Reloaded',
		'dataType': 'bool'
	},
	#AutomaticClassifications
	{
		'name':'Automatic Classifications',
		'dataType': 'string'
	},
	#MIME Type
	{
		'name':'MIME Type',
		'dataType': 'string'
	},
	#mutexPrinted Image Path
	{
		'name':'mutexPrinted Image Path',
		'dataType': 'string'
	},
	#Near-Duplicate Count
	{
		'name':'Near-Duplicate Count',
		'dataType': 'Int64'
	},
	#MD5 Original Digest
	{
		'name':'MD5 Digest (Original)',
		'dataType': 'string'
	},
	#flag.images_not_processed
	{
		'name':'Images Not Processed',
		'dataType': 'bool'
	},
	#Near-Duplicate Custodian Set
	{
		'name':'Near-Duplicate Custodian Set',
		'dataType': 'string'
	},
	#flag.carved
	{
		'name':'Carved',
		'dataType': 'bool'
	},
	#Cc
	{
		'name':'Cc',
		'dataType': 'string'
	},
	#PreviewText
	{
		'name':'Preview Text',
		'dataType': 'string'
	},
	#SHA-1 Original Digest
	{
		'name':'SHA-1 Digest (Original)',
		'dataType': 'string'
	},
	#Item Set Duplicate Guids
	{
		'name':'Item Set Duplicate GUIDs',
		'dataType': 'string'
	},
	#flag.family_inline
	{
		'name':'Family Inline',
		'dataType': 'bool'
	},
	#flag.text_indexed
	{
		'name':'Text Indexed',
		'dataType': 'bool'
	},
	#Entity.company
	{
		'name':'Entity: Company',
		'dataType': 'string'
	},
	#Name
	{
		'name':'Name',
		'dataType': 'string'
	},
	#flag.loose_file
	{
		'name':'Loose File',
		'dataType': 'bool'
	},
	#flag.ocr_failed
	{
		'name':'OCR Failed',
		'dataType': 'bool'
	},
	#Case Name
	{
		'name':'Case Name',
		'dataType': 'string'
	},
	#flag.metadata_export_failed
	{
		'name':'Metadata Export Failed',
		'dataType': 'bool'
	},
	#flag.not_failed
	{
		'name':'Not Failed',
		'dataType': 'bool'
	},
	#Kind
	{
		'name':'Kind',
		'dataType': 'string'
	},
	#flag.encrypted
	{
		'name':'Encrypted',
		'dataType': 'bool'
	},
	#To
	{
		'name':'To',
		'dataType': 'string'
	},
	#Entity.ip-address
	{
		'name':'Entity: IP Address',
		'dataType': 'string'
	},
	#Case Guid
	{
		'name':'Case GUID',
		'dataType': 'string'
	},
	#Batch Load GUID
	{
		'name':'Batch Load GUID',
		'dataType': 'string'
	},
	#File Extension (Corrected)
	{
		'name':'File Extension (Corrected)',
		'dataType': 'string'
	},
	#flag.poison
	{
		'name':'Poisoned',
		'dataType': 'bool'
	},
	#GUID
	{
		'name':'GUID',
		'dataType': 'string'
	},
	#ReviewedClassifications
	{
		'name':'Training Classifications',
		'dataType': 'string'
	},
	#flag.digest_mismatch
	{
		'name':'Digest Mismatch',
		'dataType': 'bool'
	},
	#flag.manually_added
	{
		'name':'Manually Added',
		'dataType': 'bool'
	},
	#SHA-256 Latest Digest
	{
		'name':'SHA-256 Digest (Latest)',
		'dataType': 'string'
	},
	#flag.suppressed_immaterial_item
	{
		'name':'Suppressed Immaterial Children',
		'dataType': 'bool'
	},
	#Item Category
	{
		'name':'Item Category',
		'dataType': 'string'
	},
	#flag.not_top_level
	{
		'name':'Not Top-level',
		'dataType': 'bool'
	},
	#SHA-1 Digest
	{
		'name':'SHA-1 Digest',
		'dataType': 'string'
	},
	#SHA-1 Latest Digest
	{
		'name':'SHA-1 Digest (Latest)',
		'dataType': 'string'
	},
	#Custodian
	{
		'name':'Custodian',
		'dataType': 'string'
	},
	#flag.fully_recovered
	{
		'name':'Deleted File - All Blocks Available',
		'dataType': 'bool'
	},
	#Item Set Duplicate Item Dates
	{
		'name':'Item Set Duplicate Item Dates',
		'dataType': 'string'
	},
	#flag.front_load_mutexPrinted_imaging_successful
	{
		'name':'Front Load mutexPrinted Imaging Successful',
		'dataType': 'bool'
	},
	#ItemSetsAsOriginal
	{
		'name':'Item Sets As Original',
		'dataType': 'string'
	},
	#Entity.person
	{
		'name':'Entity: Person',
		'dataType': 'string'
	},
	#ClusterIDs
	{
		'name':'Cluster IDs',
		'dataType': 'string'
	},
	#Chained Near-Duplicate Custodian Set
	{
		'name':'Chained Near-Duplicate Custodian Set',
		'dataType': 'string'
	},
	#AutomaticClassifierGainConfidence
	{
		'name':'Automatic Classifier Gain Confidence',
		'dataType': 'string'
	},
	#Child Names
	{
		'name':'Child Names',
		'dataType': 'string'
	},
	#Duplicate Custodian Set
	{
		'name':'Duplicate Custodian Set',
		'dataType': 'string'
	},
	#Path Name
	{
		'name':'Path Name',
		'dataType': 'string'
	},
	#flag.not_processed
	{
		'name':'Not Processed',
		'dataType': 'bool'
	},
	#ClusterEndpointStatus
	{
		'name':'Cluster Endpoint Status',
		'dataType': 'string'
	},
	#flag.decrypted
	{
		'name':'Decrypted',
		'dataType': 'bool'
	},
	#FileTypeTags
	{
		'name':'File Type Tags',
		'dataType': 'string'
	},
	#Top Level Path
	{
		'name':'Top-level Path Name',
		'dataType': 'string'
	},
	#PDF Generation Method
	{
		'name':'mutexPrinted Image Generation Method',
		'dataType': 'string'
	},
	#Deep Learning Confidence Values
	{
		'name':'Deep Learning Confidence Values',
		'dataType': 'string'
	},
	#Duplicate Guids
	{
		'name':'Duplicate GUIDs',
		'dataType': 'string'
	},
	#ItemNumber
	{
		'name':'Item Number',
		'dataType': 'string'
	},
	#Language
	{
		'name':'Language',
		'dataType': 'string'
	},
	#flag.metadata_export_successful
	{
		'name':'Metadata Export Successful',
		'dataType': 'bool'
	},
	#flag.text_not_indexed
	{
		'name':'Text Not Indexed',
		'dataType': 'bool'
	},
	#Decryption Password
	{
		'name':'Decryption Password',
		'dataType': 'string'
	},
	#Item Date
	{
		'name':'Item Date',
		'dataType': 'DateTime'
	},
	#flag.top_level
	{
		'name':'Top-level',
		'dataType': 'bool'
	},
	#Comment
	{
		'name':'Comment',
		'dataType': 'string'
	},
	#DocumentIds
	{
		'name':'Document IDs',
		'dataType': 'string'
	},
	#flag.ocr_successful
	{
		'name':'OCR Successful',
		'dataType': 'bool'
	},
	#flag.slack_space
	{
		'name':'Slack Space Region',
		'dataType': 'bool'
	},
	#Child Count
	{
		'name':'Child Count',
		'dataType': 'Int64'
	},
	#Near-Duplicate Paths
	{
		'name':'Near-Duplicate Paths',
		'dataType': 'string'
	},
	#flag.hidden_stream
	{
		'name':'Hidden Stream',
		'dataType': 'bool'
	},
	#File Extension (Original)
	{
		'name':'File Extension (Original)',
		'dataType': 'string'
	},
	#flag.metadata_recovered
	{
		'name':'Deleted File - Metadata Recovered',
		'dataType': 'bool'
	},
	#From
	{
		'name':'From',
		'dataType': 'string'
	},
	#ProductionSets
	{
		'name':'Production Sets',
		'dataType': 'string'
	},
	#SHA-256 Digest
	{
		'name':'SHA-256 Digest',
		'dataType': 'string'
	},
	#Chained Near-Duplicate Count
	{
		'name':'Chained Near-Duplicate Count',
		'dataType': 'Int64'
	},
	#flag.not_file_data
	{
		'name':'Not File Data',
		'dataType': 'bool'
	},
	#flag.not_loose_file
	{
		'name':'Not Loose File',
		'dataType': 'bool'
	},
	#ItemSetsAsDuplicate
	{
		'name':'Item Sets As Duplicate',
		'dataType': 'string'
	},
	#ClusterBranchIDs
	{
		'name':'Cluster Branch IDs',
		'dataType': 'string'
	},
	#Case Path
	{
		'name':'Case Path',
		'dataType': 'string'
	},
	#Duplicate Item Dates
	{
		'name':'Duplicate Item Dates',
		'dataType': 'string'
	},
	#Entity.password
	{
		'name':'Entity: password',
		'dataType': 'string'
	},
	#flag.not_physical_file
	{
		'name':'Not Physical File',
		'dataType': 'bool'
	}
]


irregularFilters=[
	{
		"name":"Corrupted Container",
		"query":"properties:FailureDetail AND NOT flag:encrypted AND has-text:0 AND ( has-embedded-data:1 OR kind:container OR kind:database )",
	},
	{
		"name":"Unsupported Container",
		"query":"kind:( container OR database ) AND NOT flag:encrypted AND has-embedded-data:0 AND NOT flag:partially_processed AND NOT flag:not_processed AND NOT properties:FailureDetail",
	},
	{
		"name":"Non-searchable PDFs",
		"query":"mime-type:application/pdf AND NOT content:*",
	},
	{
		"name":"Text Updated",
		"query":"modifications:text_updated",
	},
	{
		"name":"Bad Extension",
		"query":"flag:irregular_file_extension",
	},
	{
		"name":"Unrecognised",
		"query":"kind:unrecognised",
	},
	{
		"name":"Unsupported Items",
		"query":"NOT flag:encrypted AND has-embedded-data:0 AND ( ( has-text:0 AND has-image:0 AND NOT flag:not_processed AND NOT kind:multimedia AND NOT mime-type:application/vnd.ms-shortcut AND NOT mime-type:application/x-contact AND NOT kind:system AND NOT mime-type:( application/vnd.apache-error-log-entry OR application/vnd.git-logstash-log-entry OR application/vnd.linux-syslog-entry OR application/vnd.logstash-log-entry OR application/vnd.ms-iis-log-entry OR application/vnd.ms-windows-event-log-record OR application/vnd.ms-windows-event-logx-record OR application/vnd.ms-windows-setup-api-win7-win8-log-boot-entry OR application/vnd.ms-windows-setup-api-win7-win8-log-section-entry OR application/vnd.ms-windows-setup-api-xp-log-entry OR application/vnd.squid-access-log-entry OR application/vnd.tcpdump.record OR application/vnd.tcpdump.tcp.stream OR application/vnd.tcpdump.udp.stream OR application/vnd.twitter-logstash-log-entry OR application/x-pcapng-entry OR filesystem/x-linux-login-logfile-record OR filesystem/x-ntfs-logfile-record OR server/dropbox-log-event OR text/x-common-log-entry OR text/x-log-entry ) AND NOT kind:log AND NOT mime-type:application/vnd.ms-exchange-stm ) OR mime-type:application/vnd.lotus-notes )",
	},
	{
		"name":"Empty",
		"query":"mime-type:application/x-empty",
	},
	{
		"name":"Encrypted",
		"query":"flag:encrypted",
	},
	{
		"name":"Decrypted",
		"query":"flag:decrypted",
	},
	{
		"name":"Deleted",
		"query":"flag:deleted",
	},
	{
		"name":"Corrupted",
		"query":"properties:FailureDetail AND NOT flag:encrypted",
	},
	{
		"name":"Digest Mismatch",
		"query":"flag:digest_mismatch",
	},
	{
		"name":"Text Stripped",
		"query":"flag:text_stripped",
	},
	{
		"name":"Text Not Indexed",
		"query":"flag:text_not_indexed",
	},
	{
		"name":"Licence Restricted",
		"query":"flag:licence_restricted",
	},
	{
		"name":"Not Processed",
		"query":"flag:not_processed",
	},
	{
		"name":"Partially Processed",
		"query":"flag:partially_processed",
	},
	{
		"name":"Text Not Processed",
		"query":"flag:text_not_processed",
	},
	{
		"name":"Images Not Processed",
		"query":"flag:images_not_processed",
	},
	{
		"name":"Reloaded",
		"query":"flag:reloaded",
	},
	{
		"name":"Poisoned",
		"query":"flag:poison",
	},
	{
		"name":"Slack Space",
		"query":"flag:slack_space",
	},
	{
		"name":"Unallocated Space",
		"query":"flag:unallocated_space",
	},
	{
		"name":"Manually Added",
		"query":"flag:manually_added",
	},
	{
		"name":"Carved",
		"query":"flag:carved",
	},
	{
		"name":"Deleted File - All Blocks Available",
		"query":"flag:fully_recovered",
	},
	{
		"name":"Deleted File - Some Blocks Available",
		"query":"flag:partially_recovered",
	},
	{
		"name":"Deleted File - Metadata Recovered",
		"query":"flag:metadata_recovered",
	},
	{
		"name":"Hidden Stream",
		"query":"flag:hidden_stream",
	}
]

print('''Limitations:
======================
75 max columns
75 max tables
10,000 max rows per single POST rows request
1,000,000 rows added per hour per dataset
5 max pending POST rows requests per dataset
120 POST rows requests per minute per dataset
If table has 250,000 or more rows, 120 POST rows requests per hour per dataset
200,000 max rows stored per table in FIFO dataset
5,000,000 max rows stored per table in 'none retention policy' dataset
4,000 characters per value for string column in POST rows operation
Table name can't include any of these character: !\\"$%&\'()*+,./
======================
Reporting:
https://community.powerbi.com/t5/Developer/Is-it-possible-to-use-an-API-Bearer-to-load-a-report/m-p/913521#M22121
Both App owns data and user owns data require Web Server like IIS

 

Other option is to use Secure Embed : This option help you to embed in any of the apps (don't need any IIS) there are some limitations 

 

Limitations:

The user will need to sign-in to view the report whenever they open a new browser window.
Some browsers require you to refresh the page after sign-in, especially when using InPrivate or InCognito modes.
To achieve a single sign-on experience, use the Embed in SharePoint Online option, or build a custom integration using the User Owns Data approach. Learn more about User owns data
The automatic authentication capability provided with the Embed option does not work with the Power BI JavaScript API. For the Power BI JavaScript API, use the User Owns Data approach to embedding. Learn more about User owns data
Secure embed does not support paginated reports or dashboards.
Embedding in Portals for Azure B2B users is not yet supported.
 

Not sure you can override the autentication and provide the bearer token with this option.
======================
''')


def checkData():
	#checking data for issues
	import re
	invalidChars='!\\"$%&\'()*+,./'
	prog = re.compile('.*[' + invalidChars + '].*')
	errors=[]
	for table in datasetConfig['tables']:
		if(prog.match(table['name'])):
			errors.append('Table has invalid characters (' + invalidChars + '):' + table['name'])
		if(len(table['columns']) > 75):
			errors.append('Table has too many columns (' + table['name'] + '):' + str(len(table['columns'])))
	return(errors)