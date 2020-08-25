# Simple json parser to understand the data structure 
import urllib2, json
url  = urllib2.urlopen('https://bionomia.net/0000-0001-7618-5230/specimens.json')
data = json.load(url)


# this is a list 
#print data["@reverse"].keys()

#this is a dict
#print data["@reverse"]['identified']
#print type(data["@reverse"]['identified'])

idf  = data["@reverse"]['identified']
i=0
while i < len(idf):
    #print(idf[i])
    for k , v in idf[i].items():
                     print str(k) + "->" + str(v)
    i += 1

#identified = data["@reverse"]['identified'][0]
#print type(data["@reverse"]['identified'][0])
#print data["@reverse"]['identified'][0]['occurrenceID']
#print type(data["@reverse"]['identified'][0]['occurrenceID'])

#for k, v in identified.items():
#	    print v 
