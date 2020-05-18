import json 
import requests

with open('myfile.json') as json_file:
    json_object = json.load(json_file)

for x in json_object:
    issuetitle   = x['FOR THIS I NEED ...']
    persona      = "As a "      + x['AS (POSITION)']
    iwanto       = " I want to " + x['I WANT TO ...']
    sothat       = " so that I can "   + x['SO THAT I ...']
    forthis      = " for this I need " + issuetitle
    ticketbody   =  persona + iwanto + sothat + forthis
    label1       =  x['USER CATEGORY (MAIN)']
    label2       =  x['DATA LEVEL']
    label3       =  x['USER ORGANISATION CATEGORY']
    label4       =  x['DATA MANAGEMENT CYCLE-PHASE']
    label5       = "USER-SURVEY"
    githuburl    = "https://api.github.com/repos/myrepo/my-user-stories/issues" 
    makecurlcmd = "curl -i -H 'Authorization: token mysecret' " + "-d " + "'{\"title\": \"" + issuetitle+"\"," + "\"body\": \"" + ticketbody+"\"," + "\"labels\": [\"" + label1 + "\",\"" + label2 + "\",\"" + label3 + "\",\"" + label4 + "\",\"" + label5 +"\"]}' "  + githuburl 
    print makecurlcmd

#example curl command
#curl -i -H 'Authorization: token mysecret' -d '{ "title": "user story title", "body": "As a User I want to do X so that I can accomplish Y for this I need Z", "labels": ["testlabel1","testlabe2"]}'
