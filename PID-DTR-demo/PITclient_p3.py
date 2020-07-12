'''
  python client library for PIDs and PID Information Types 
  Created on 11.8.2016
  @author: Ulrich Schwardmann, GWDG, uschwar1@gwdg.de
  licence: CC BY-SA
'''

import os
import sys
import string
import io
import urllib.request as urllib2
from urllib.error import URLError, HTTPError
import csv
import json
import jsonschema
import datetime
import PIDclient_p3 as PIDclient

################
class typeID(PIDclient.PID):
    """
    used for PIDs pointing to types
    """

    def __init__(self,initID):
        self.id = initID
        self.ref = ""
        self.isValidPID = True
        self.content = {}
        self.content = self.getContent(self.url_hdl)
        if self.content == {}:
            self.isValidPID = False                                                    
        self.tcontent = {}
        self.DTRtype = ""
        self.isValidType = False
        if self.isType():
            self.isValidType = True
                

    def __getTypeAddressInRegistry(self,location):
        """
        gets the json address of this typeID in the HTML snippet of the location field in "10320/loc"

        @param location type string: HTML snippet of the location field in "10320/loc"
        @return href type string: href content 
        """
        for i in location.splitlines():
            if (i.find('view="json"') >= 0):
                href = i.split('href="')[1].split('"')[0]
        return href
    
    def getContentAddressOfTypeID(self):
        """
        gets the json address of this typeID. uses getTypeAddressInRegistry on "10320/loc".

        @return href type string: address of this typeID as href content in json
        """        
        # get type content address in type registry
        if self.ref == '':
            if self.isValidType:
                objCont = self.getContent(self.url_hdl)
                LocKey = "10320/loc"
                TypeLoc = ""
                for item in objCont["values"]:
                    if item["type"] == LocKey:
                        TypeLoc = item["data"]["value"]
                self.ref = self.__getTypeAddressInRegistry(TypeLoc)
        return self.ref
    
    def getFullContentOfTypeID(self):
        """
        gets the full json type content in type registry of this typeID, if available, else {}
        (dict with "id", "type" and "content" : getContentOfTypeID())

        @return TypeCont type json: content of this typeID 
        """        
        if self.isValidType:
            href = self.getContentAddressOfTypeID()
            href = href + "?full"
            TypeCont = self.getJSON4URL(href)
            return TypeCont
        else:
            return {}
    
    def getContentOfTypeID(self):
        """
        gets the json type content in type registry of this typeID, if available, else {}
        ("content" part of getFullContentOfTypeID())

        @return TypeCont type json: content of this typeID
        """        
        if self.isValidType:
            if self.tcontent == {}:
                full_tcontent = self.getFullContentOfTypeID()
                try:
                    self.tcontent = full_tcontent["content"]
                except:
                    self.tcontent = {}
                    self.isValidType = False
                try:
                    self.DTRtype = full_tcontent["type"]
                except:
                    self.DTRtype = {}
                    self.isValidType = False
        return self.tcontent
    
    def getPropertiesOfTypeID(self):
        """
        gets the json type properties in type registry of this typeID, if available, else {}

        @return TypeProp type json: properties of this typeID 
        """        
        if self.isValidType:
            TypeCont = self.getContentOfTypeID()
            return TypeCont["properties"]
        else:
            return {}

    def getNameOfTypeID(self):
        """
        gets the name in type registry of this typeID.

        @return TypeName type string: name of this typeID 
        """ 
        if self.isValidType:
            TypeCont = self.getContentOfTypeID()
            try: 
                return TypeCont["name"]
            except KeyError:
                return ""
        return ""
    
    def getDTRTypeOfTypeID(self):
        """
        gets the DTR type in type registry of this typeID.

        @return DTRTypeName type string: DTR type of this typeID 
        """ 
        if self.isValidType: 
            if self.DTRtype == "":
                self.content = self.getContentOfTypeID()
            return self.DTRtype
        return ""
    
    def getDescriptionOfTypeID(self):
        """
        gets the description in type registry of this typeID.

        @return TypeDescr type string: description of this typeID 
        """        
        if self.isValidType:
            TypeCont = self.getContentOfTypeID()
            return TypeCont["description"]
        else:
            return ""
    
    def getSchemaOfTypeID(self):
        """
        gets the schema in type registry of this typeID.

        @return tc_schema type json: schema of this typeID 
        """        
        if self.isValidType:
            TypeCont = self.getContentOfTypeID()
            tc_schema = TypeCont["validationSchema"]
            if (isinstance(tc_schema, str)):
                tc_schema = json.loads(tc_schema)
            return tc_schema
        else:
            return {}

    def hasValidSchema(self):
        """
        is the schema in type registry of this typeID a valid schema?

        @return SchemaValid type boolean: True if schema is valid
        """        

        # is schema of this typeID valid

        if self.isValidType:
            tSchema = self.getSchemaOfTypeID()
            try:
                jsonschema.validate({}, tSchema)
                SchemaValid = True
            except jsonschema.SchemaError as e:
                SchemaValid = False
            except jsonschema.exceptions.ValidationError:
                SchemaValid = True
            return SchemaValid
        else:
            return False

    def instanceValidatesAgainstSchema(self,typeInst):
        """
        validates type instance against schema

        @param typeInst type object or string: type instance to be verified
        @return typeValid type Boolean: True if TypeID value in this PID validates against schema of TypeID
        """
        if isinstance(typeInst, str):
            try:
                jValue = json.loads(typeInst)
            except ValueError:
                try:
                    jValue = json.loads(typeInst + "0") # json does not allow 1. for numbers
                except:
                    jValue = typeInst
        else:
            jValue = typeInst

        tSchema = self.getSchemaOfTypeID()
        if self.hasValidSchema():
            try:
                jsonschema.validate(jValue, tSchema)
                typeValid = True
            except jsonschema.ValidationError as e:
                typeValid = False
        else:
            typeValid = False
        return typeValid

###############
class typeArray:
    """
    Used for example in the validation of arrays of instance arrays with equal type pattern (e.g. rows in CSV files).
    Avoids the reload of type and schema for each singular instance.
    """

    def __init__(self,initArray):
        self.typeID_list = []
        self.schema_list = []
        self.tcontent_list = []
        self.isValidTypeArray = True
        if isinstance(initArray, list):
            for item in initArray:
                tyid = typeID(item)
                self.typeID_list.append(tyid)
                self.tcontent_list.append(tyid.tcontent)
                if tyid.hasValidSchema():
                    self.schema_list.append(tyid.getSchemaOfTypeID())
                else:
                    self.isValidTypeArray = False
        else:
            self.isValidTypeArray = False

    def isValidTypeArray(self):
        return self.isValidTypeArray

###############
class typeRegistry:
    """
    represents a list of type registry. Is used for searching inside type registries
        Attributes:
           content:       Content of DTR obtained by a global search (e.g. self.searchDTR(\"*:*\")), used for caching to improve search performance
           searchContent: Content after a concrete search for further clients use

    """
    content = {} 
    searchContent = {} 

    def __init__(self,initURL):
        """ initURL is the registry URL """
        self.typeRegURL = initURL
        if self.typeRegURL[len(self.typeRegURL)-1] == "/": # strip ending "/"
            self.typeRegURL = self.typeRegURL[0:len(self.typeRegURL)-1]
        self.content = {} 
        self.searchContent = {}

    def contentDTR(self):
        """
        retrieves and if necesary initializes self.content
        """
        self.content = self.searchDTR("*:*")
        return self.content

    def searchDTR(self, searchStr):
        """                                                                                                                                                        
        Search for data types in DTR 
        allowed :
        http://dtr.pidconsortium.eu:8081/objects/?query=type:%22User%22
        http://dtr.pidconsortium.eu:8081/objects/?query=type:%22PID-InfoType%22
        http://dtr.pidconsortium.eu:8081/objects/?query=%22123/45-6789*%22
        http://dtr.pidconsortium.eu:8081/objects/?query=*:*
        http://dtr.pidconsortium.eu:8081/objects/?query=%22searchString%22
        param searchString type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        url_ext = "/objects/?query="
        # searchStr = searchString.replace('"','%22')
        try:
            proxy_url = self.typeRegURL + url_ext + searchStr
            content_stream = urllib2.urlopen(proxy_url)
            try:
                self.content = json.loads(content_stream.read())
            except KeyError:
                self.content = {}
        except HTTPError as err:
            self.httpError(err.code, proxy_url)
            self.content = {}
        self.searchContent = self.content
        return self.content

    def searchDTR4Key(self, searchStr, skey, skey2=None):
        """
        searches all types matching searchStr giving out the pid of the type and the key skey.
        a second key can be provided as optional parameter.
        param searchStr type string: string to be searched in DTR
        param skey type string: key wanted for output
        param skey2 type string: another key wanted for output
        @return result TYPE json: search result
        """
        searchObj = self.searchDTR(searchStr)
        slist = []
        k = 0
        for item in self.content["results"]:
            if skey2 != None:
                ilist = {}
                if skey2 == "type":
                    try:
                        ilist[item[skey]] = item[skey2]
                        slist.append(ilist)
                        k += 1
                    except KeyError:
                        print ('ERROR: item["' + skey + '"] or item["type"] not found for ' + item["id"])
                else:
                    try:
                        ilist[item["content"][skey]] = item["content"][skey2]
                        slist.append(ilist)
                        k += 1
                    except KeyError:
                        print ('ERROR: item["' + skey + '"] or item["' + skey2 + '"] not found for ' + item["id"])
            else:
                try:
                    slist.append(item["content"][skey])
                    k += 1
                except KeyError:
                    print ('ERROR: item["content"]["' + skey + '"] not found for ' + item["content"]["identifier"])
        searchObj["results"] = slist
        searchObj["size"] = k
        return searchObj

    def searchDTR4PID(self, searchStr):
        """
        searches all types matching searchStr giving out the pid of the type and the key "identifier"
        param searchStr type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        return self.searchDTR4Key(searchStr, "identifier")

    def searchDTR4NAME(self, searchStr):
        """
        searches all types matching searchStr giving out the pid of the type and the key "name"
        param searchStr type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        return self.searchDTR4Key(searchStr, "name")

    def searchDTR4SCHEMA(self, searchStr):
        """
        searches all types matching searchStr giving out the pid of the type and the key "validationSchema"
        param searchStr type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        return self.searchDTR4Key(searchStr, "validationSchema")

    def searchDTR4PIDNAME(self, searchStr):
        """
        searches all types matching searchStr giving out the pid of the type and the key "identifier"
        and "name" as second key
        param searchStr type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        return self.searchDTR4Key(searchStr, "identifier", "name")

    def searchDTR4PIDDESC(self, searchStr):
        """
        searches all types matching searchStr giving out the pid of the type and the key  "identifier"
        and "description" as second key
        param searchStr type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        return self.searchDTR4Key(searchStr, "identifier", "description")

    def searchDTR4PIDTYPE(self, searchStr):
        """
        searches all types matching searchStr giving out the pid of the type and the key  "identifier"
        and "type" as second key
        param searchStr type string: string to be searched in DTR
        @return result TYPE json: search result
        """
        return self.searchDTR4Key(searchStr, "id", "type")

    def get_changed(self,timeStart_hours, timeEnd_hours=0, schemaOfType=""):
        """
        list all types in a DTR that were changed during the last timeframe_hours hours
        @param timeStart_hours type int: hours from now that starts timeframe
        @param timeEnd_hours type int: optional hours from now that ends timeframe (default 0, now)
        @param schemaOfType type string: optional limits type to given schema
        @return changed_items type list: list of type PIDs changed in timeframe
        """
        if self.content == {}:
            self.contentDTR()
        currTime = datetime.datetime.today()
        changed_items = []
        for item in self.content["results"]:
            if schemaOfType != "" and item["type"] == schemaOfType:
                try:
                    lastModStr = item["content"]["provenance"]["lastModificationDate"]
                    modTime = datetime.datetime.strptime(lastModStr.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                    delta = (currTime - modTime).total_seconds()
                    if (delta < timeStart_hours*3600) and (delta > timeEnd_hours*3600):
                        changed_items.append(item)
                        if verbosity > 1:
                            print (item["id"] + " " + lastModStr + " " + str(delta) + " " + str(item["content"]["name"]))
                except:
                    do_nothing = True
        return changed_items

    def httpError(self,errCode, proxy_url):
        if   errCode == 400:
            sys.stderr.write(str(errCode) + " " + "Bad Request! " + proxy_url + "\n")
        elif errCode == 401:
            sys.stderr.write(str(errCode) + " " + "Unauthorized! "  + proxy_url + "\n")
        elif errCode == 403:
            sys.stderr.write(str(errCode) + " " + "Access denied! "  + proxy_url + "\n")
        elif errCode == 404:
            sys.stderr.write(str(errCode) + " " + "Page not found! "  + proxy_url + "\n")
        elif errCode == 405:
            sys.stderr.write(str(errCode) + " " + "Method Not Allowed! " + proxy_url + "\n")
        else:
            sys.stderr.write(str(errCode) + " " + "Something happened! " + proxy_url + "\n")

###############
def test():        
    """
    performs tests on PIDs with Types
    """     
    # xmpl_PID  = "11148/0000-0011-2AC8-D"            # ordinary PID
    xmpl_PID  = "11022/0000-0001-30FC-D"            # ordinary PID, contains oldTyID = "Authors"
    xmpl_PID  = "11022/0000-0001-30FE-B"            # ordinary PID, contains tyID = "21.T11148/21c5a7eba95c2e8f8bb8"
    xmpl_tyID = "21.T11148/21c5a7eba95c2e8f8bb8"    # type PID
    xmpl_oldTyID = "Authors"
    xmpl_TypeReg = "http://dtr-test.pidconsortium.eu/"
    orig0_NA = "0.NA/21.11101"
    tst_instance = { "Mandatory-Properties-DataCite" : {"creators" : [ {"creator" : {"creatorName": "m\u00fcller, hans-heinrich" } } ], "identifier" : { "identifier-Value" : "10.123/some_text" , "identifier-Attribute" : {"identifierType" : "DOI" } }, "publicationYear" : "2009", "publisher" : "(GWDG)", "resourceType" : { "resourceType-Value" : "some_text" , "resourceType-Attribute" : { "resourceTypeGeneral" : "Dataset" } }, "titles" : [ { "title": {"title-Value": "some title text" } } ] } }
    searchString = "previous"

    pid  = PIDclient.PID(xmpl_PID) 
    print ("pid.id:" + " " + str(pid.id))
    NApid = PIDclient.naPID(orig0_NA)
    print ("pid.id:" + " " + str(NApid.id))
    tpid = typeID(xmpl_PID) 
    print ("tpid.id:" + " " + str(tpid.id))
    tyid = typeID(xmpl_tyID) 
    print ("tyid.id:" + " " + str(tyid.id))
    tyReg = typeRegistry(xmpl_TypeReg)
    print ("tyReg.typeRegURL:" + " " + str(tyReg.typeRegURL))

    print (">>>> tyReg.searchDTR(typeID):\n" + json.dumps(tyReg.searchDTR("\"21.T11148/acf5d1883994cc9416f6\""), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyReg.searchDTR(Bad Request):\n" + json.dumps(tyReg.searchDTR("\"21.T11148/8a\"*"), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyReg.searchDTR4PIDNAME(searchString):\n" + json.dumps(tyReg.searchDTR4PIDNAME(searchString), sort_keys=True,indent=2, separators=(',', ' : ')))

    print (">>>> NApid.getLHSadresses():\n" + str(NApid.getLHSadresses()))
    print (">>>> NApid.getLHSinterfaces():\n" + json.dumps(NApid.getLHSinterfaces(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> NApid.getPrimaryLHSadresses():\n" + str(NApid.getPrimaryLHSadresses()))
    print (">>>> NApid.getMirrorLHSadresses():\n" + str(NApid.getMirrorLHSadresses()))
    print (">>>> NApid.gethasMultiPrimary():\n" + str(NApid.hasMultiPrimary()))
    
    print (">>>> pid.getContentFromProxy():\n" + json.dumps(pid.getContentFromProxy(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.isType():\n" + json.dumps(pid.isType(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getAllTypes():\n" + json.dumps(pid.getAllTypes(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.hasType(xmpl_tyID):\n" + json.dumps(pid.hasType(xmpl_tyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getTypeContentInPID(xmpl_tyID):\n" + json.dumps(pid.getTypeContentInPID(xmpl_tyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getTypeDataInPID(xmpl_tyID):\n" + json.dumps(pid.getTypeDataInPID(xmpl_tyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getTypeValueInPID(xmpl_tyID):\n" + json.dumps(pid.getTypeValueInPID(xmpl_tyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.hasType(xmpl_oldTyID):\n" + json.dumps(pid.hasType(xmpl_oldTyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getTypeContentInPID(xmpl_oldTyID):\n" + json.dumps(pid.getTypeContentInPID(xmpl_oldTyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getTypeDataInPID(xmpl_oldTyID):\n" + json.dumps(pid.getTypeDataInPID(xmpl_oldTyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.getTypeValueInPID(xmpl_oldTyID):\n" + json.dumps(pid.getTypeValueInPID(xmpl_oldTyID), sort_keys=True,indent=2, separators=(',', ' : ')))
    b = tpid.isType()
    print (">>>> tpid.isType():\n" + json.dumps(tpid.isType(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tpid.getContentAddressOfTypeID():\n" + json.dumps(tpid.getContentAddressOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tpid.getContentOfTypeID():\n" + json.dumps(tpid.getContentOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tpid.getPropertiesOfTypeID():\n" + json.dumps(tpid.getPropertiesOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tpid.getSchemaOfTypeID():\n" + json.dumps(tpid.getSchemaOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tpid.getNameOfTypeID():\n" + json.dumps(tpid.getNameOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tpid.getDescriptionOfTypeID():\n" + json.dumps(tpid.getDescriptionOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))

    print (">>>> tyid.isType():\n" + json.dumps(tyid.isType(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.getContentAddressOfTypeID():\n" + json.dumps(tyid.getContentAddressOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.getContentOfTypeID():\n" + json.dumps(tyid.getContentOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.getPropertiesOfTypeID():\n" + json.dumps(tyid.getPropertiesOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.hasValidSchema():\n" + json.dumps(tyid.hasValidSchema(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.getSchemaOfTypeID():\n" + json.dumps(tyid.getSchemaOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.instanceValidatesAgainstSchema():\n" + json.dumps(tyid.instanceValidatesAgainstSchema(json.dumps(tst_instance)), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.instanceValidatesAgainstSchema():\n" + json.dumps(tyid.instanceValidatesAgainstSchema(tst_instance), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> pid.typeInPidValidatesAgainstSchema():\n" + json.dumps(pid.typeInPidValidatesAgainstSchema(tyid), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.getNameOfTypeID():\n" + json.dumps(tyid.getNameOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print (">>>> tyid.getDescriptionOfTypeID():\n" + json.dumps(tyid.getDescriptionOfTypeID(), sort_keys=True,indent=2, separators=(',', ' : ')))


##############                                                                                                                                   
if __name__ == "__main__":

    test()
