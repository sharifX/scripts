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
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import csv
import json
import jsonschema
import datetime
import six
from six.moves import range


class PID:
    """
    used for PIDs in general 
    """
    url_hdl = 'http://hdl.handle.net/api/handles/'
    noRedir = '?noredirect'

    def __init__(self,initID):
        self.id = initID
        self.isValidPID = True
        self.content = {}
        self.content = self.getContent(self.url_hdl)
        if self.content == {}:
            self.isValidPID = False
        else:
            self.contentSize = len(json.dumps(self.content))


    def getContentFromProxy(self):
        """
        gets content of PID in Handle database while using the default proxy Handle API
        Exits if ressource is not accessible for several reasons

        @param base_url type string: base url for resolution of this PID
        @return content TYPE json: content of PID
        """
        return self.getContent(self.url_hdl)
        

    def getContent(self,base_url):
        """
        gets content of PID in Handle database. 
        Used for content retrieval also from LHS, if known.
        Exits if ressource is not accessible for several reasons

        @param base_url type string: base url for resolution of this PID
        @return content TYPE json: content of PID
        """
        if self.content == None or self.content == {}:
            self.content = self.getJSON4URL(base_url)
        return self.content

    def getJSON4URL(self,base_url):
        """
        gets JSON content for URL. 
        Exits if ressource is not accessible for several reasons

        @param base_url type string: base url for resolution of this PID
        @return content TYPE json: content of PID
        """
        if base_url == self.url_hdl:
            app = str(self.id) + self.noRedir
        else: 
            app = ''
        try:
            proxy_url = base_url + app
            content_stream = urlopen(proxy_url)
            try:
                content = json.loads(content_stream.read())
            except ValueError:
                print("invalid JSON in content stream at " + proxy_url)
                content = {}
        except HTTPError as err:
            self.httpError(err.code, proxy_url)
            content = {}
            # raise
            # sys.exit(-1)
        except IOError as err: # no internet connection?
            print("error: failed to open: " + proxy_url)
            content = None
            # sys.exit(-1)
        return content

    def getContentSize(self):
        return self.contentSize
            
    def getAllTypes(self):
        """
        gets a list of all types in this PID.

        @return TypeList type array: list of all types
        """
        try:
            self.isValidPID
        except AttributeError:
            return {}
        objCont = self.getContent(self.url_hdl)
        # TypeList = []
        # for item in objCont["values"]:
        #     TypeList.append(item["type"])
        # return TypeList
        if objCont == None:
            return objCont
        try:
            objCont["values"]
        except KeyError:
            return {}
        return objCont["values"]
    
    def hasType(self,tyID):
        """
        contains this PID a type with TypeID 

        @param tyID type string or class typeID: TypeID to be verified
        @return hasType type Boolean: True if TypeID is in this PID
        """
        if isinstance(tyID, str):
           TypeIDstr = tyID
        else:
            try:
                TypeIDstr = tyID.id
            except:
                return False
        if not self.isValidPID:
            return False
        hasType = False
        objCont = self.getContent(self.url_hdl)
        if objCont == None:
            return objCont
        try:
            objCont["values"]
        except KeyError:
            return hasType
        for item in objCont["values"]:
            if (item["type"] == TypeIDstr):
                hasType = True
        return hasType
    
    def getTypeContentInPID(self,tyID):
        """
        get complete content of given type in this PID

        @param tyID type string or class typeID: TypeID to be verified
        @return typeContent type string: content of TypeID in this PID as JSON string        
        """
        objCont = self.getContent(self.url_hdl)
        if objCont == None:
            return objCont
        typeContent = ""
        if isinstance(tyID, str):
           TypeIDstr = tyID
        else:
            try:
                TypeIDstr = tyID.id
            except:
                return typeContent
        if not self.isValidPID:
            return {}
        try:
            objCont["values"]
        except KeyError:
            return typeContent
        for item in objCont["values"]:
            if item["type"] == TypeIDstr:
                typeContent = item
        return typeContent

    def getTypeContentInPIDbyIdx(self,tyIDX):
        """
        get complete content of type of given index in this PID

        @param tyID type integer: TypeID to be verified
        @return typeContent type string: content of TypeID of given index in this PID as JSON string        
        """
        objCont = self.getContent(self.url_hdl)
        if objCont == None:
            return objCont
        typeContent = ""
        if isinstance(tyIDX, int):
            TypeIDX = tyIDX
        else:
            TypeIDX = 0
        if not self.isValidPID:
            return {}
        try:
            objCont["values"]
        except KeyError:
            return typeContent
        for item in objCont["values"]:
            if item["index"] == tyIDX:
                typeContent = item
        return typeContent
    
    def getAllTypeContentInPID(self,tyID):
        """
        get complete content of all type of given type in this PID as list

        @param tyID type string or class typeID: TypeID to be verified
        @return AllTypes type list: content of all TypeID in this PID as JSON string        
        """
        typeContentList = []
        objCont = self.getContent(self.url_hdl)
        if objCont == None:
            return objCont
        typeContent = ""
        if isinstance(tyID, str):
           TypeIDstr = tyID
        else:
            try:
                TypeIDstr = tyID.id
            except:
                return typeContent
        if not self.isValidPID:
            return {}
        try:
            objCont["values"]
        except KeyError:
            return typeContent
        for item in objCont["values"]:
            if item["type"] == TypeIDstr:
                typeContent = item
                typeContentList.append(typeContent)
        return typeContentList
    
    def getTypeDataInPID(self,tyID):
        """
        get data for type tyID in this PID

        @param TypeID type string or class typeID: TypeID to be verified
        @return TypeData type json: data to type
        """
        if not self.isValidPID:
            return "Error: not valid PID"
        TypeData = {}
        objCont = self.getContent(self.url_hdl)
        if objCont == None:
            return objCont
        if isinstance(tyID, str):
           TypeIDstr = tyID
        else:
            try:
                TypeIDstr = tyID.id
            except:
                return {}
        if not self.isValidPID:
            return {}
        try:
            objCont["values"]
        except KeyError:
            return TypeData
        for item in objCont["values"]:
            if item["type"] == TypeIDstr:
                try:
                    TypeData = item["data"]
                except:
                    None
        return TypeData
        
    def getTypeValueInPID(self,tyID):
        """
        get value for type tyID in this PID

        @param TypeID type string or class typeID: TypeID to be verified
        @return TypeValue type json: value of type
        """
        if not self.isValidPID:
            return "Error: not valid PID"
        TypeData = self.getTypeDataInPID(tyID)
        if TypeData == None:
            return TypeData        
        try:
            TypeValue = TypeData["value"]
        except KeyError: 
            TypeValue = {}
        except TypeError:
            TypeError = "Error: not valid PID"        
        return TypeValue
    
    def getTypeFormatInPID(self,tyID):
        """
        get format of type value tyID in this PID

        @param TypeID type string or class typeID: TypeID to be verified
        @return TypeFormat type string: format of type value
        """
        if not self.isValidPID:
            return "Error: not valid PID"
        TypeData = self.getTypeDataInPID(tyID)
        if TypeData == None:
            return TypeData        
        try:
            TypeValue = TypeData["format"]
        except KeyError: 
            TypeValue = ""
        except TypeError:
            TypeError = "Error: not valid PID"
        return TypeValue
            
    def getLatestTimestamp(self,PIDtype=""):
        """
        get latest timestamp for all entries of specified type, 
        or for all types if type string is emty (not specified)
        @param PIDtype type string: selected type

        @return latestTimestamp type String: latest timestamp as standard time or empty string if type not found
        """
        latestTimestamp = ""
        for item in self.content["values"]:
            if item["type"] == PIDtype or PIDtype == "":
                if item["timestamp"] > latestTimestamp:
                    latestTimestamp = item["timestamp"]
        return latestTimestamp 

    def isType(self):
        """
        is PID a type

        @return isType type Boolean: True if this PID is Type
        """
        # peek for type: true if PID points to a type
        # try:
        #     if not self.isValidType:  # in case PID is invoked as a typeID
        #         return False
        # except AttributeError:
        #     return False
        if not self.isValidPID:
            return False
        objCont = self.getContentFromProxy()
        Type = "10320/loc"
        isType = False
        try:
            objCont["values"]
        except KeyError:
            return isType
        for item in objCont["values"]:
            if item["type"] == Type:
                isType = True
        return isType

    def hasValidType(self,tyID):
        """
        validates type in this PID against schema

        @param TypeID type string: TypeID to be verified
        @return typeValid type Boolean: True if TypeID value in this PID validates against schema of TypeID
        """
        return self.typeInPidValidatesAgainstSchema(tyID)

    def typeInPidValidatesAgainstSchema(self,tyID):
        """
        validates type in this PID against schema

        @param TypeID string or class TypeID: TypeID to be verified
        @return typeValid type Boolean: True if TypeID value in this PID validates against schema of TypeID
        """
        # 
        try:
            tValue = self.getTypeValueInPID(tyID)
        except:
            return False
        if isinstance(tyID, str):
           TypeID = typeID(tyID)
        else:
            try:
                TypeIDstr = tyID.id
                TypeID = tyID
            except:
                return False
        tSchema = TypeID.getSchemaOfTypeID()
        if True:#tyID.hasValidSchema():
            try:
                jsonschema.validate(tValue, tSchema)
                typeValid = True
            except jsonschema.ValidationError as e:
                typeValid = False
        else:
            typeValid = False
        return typeValid

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

################
class naPID(PID):
    """
    naming authority PIDs used under the prefix 0:NA
    """
    def __init__(self,initID):
        self.id = initID
        self.content = {}
        self.content = self.getContent(self.url_hdl)
        self.values = self.get_NA_Values()
        self.HS_SERV = self.get_HS_SERV()

    def get_HS_SERV(self):
        """
        gets reference to the Handle service server inside the naming authority PID if available, 
        refers to self.id otherwise

        @return HS_SERV_str type string: reference to the Handle service server
        """
        HS_SERV_str = ""
        for i in range(len(self.values)):
            if self.values[i]['type'] == "HS_SERV":
                HS_SERV_str = self.values[i]['data']['value']
                HS_SERV_PID = naPID(HS_SERV_str)
                self.values = HS_SERV_PID.values
        if HS_SERV_str == "":
            HS_SERV_str = self.id
        return HS_SERV_str
    
    def get_NA_Values(self):
        """
        gets values in the content of a naming authority PID if available, empty dict otherwise

        @return values type dict: values
        """
        if self.id.split("/")[0] == "0.NA":
            try:
                values = self.content['values']
            except KeyError:
                print("no values found for Handle 0.NA/" + prefix)
                print("does prefix actually exist ???")
                values = {}
        else:
            print(self.id + " is not a naming authority Handle (e.g. 0.NA/xyz)")
            values = {}
        return values
    
    def getLHSadresses(self):
        """
        gets LHS IP adresses in the content of a naming authority PID if available, empty list otherwise

        @return LHSadresses type list: LHS IP adresses
        """
        LHSadresses = []
        for i in range(len(self.values)):
            if type(self.values[i]['data']) is dict:
                if ('servers' in self.values[i]['data']['value'] and 'address' in self.values[i]['data']['value']['servers'][0]):
                    ipAddress = self.values[i]['data']['value']['servers'][0]['address']
                    LHSadresses.append(ipAddress)
        
        return LHSadresses
    
    def getLHSinterfaces(self):
        """
        gets LHS IP adresses and interfaces in the content of a naming authority PID if available, empty dict otherwise

        @return LHSinterfaces type dict: dict of LHS IP adresses and interfaces 
        """
        LHSinterfaces = {}
        for i in range(len(self.values)):
            if type(self.values[i]['data']) is dict:
                if ('servers' in self.values[i]['data']['value'] and 'address' in self.values[i]['data']['value']['servers'][0] and 'interfaces' in self.values[i]['data']['value']['servers'][0] ):
                    ipAddress = self.values[i]['data']['value']['servers'][0]['address']
                    ipInterfaces = self.values[i]['data']['value']['servers'][0]['interfaces']
                    LHSinterfaces[ipAddress] = ipInterfaces
        return LHSinterfaces
    
    def getPrimaryLHSadresses(self):
        """
        gets IP adresses of all primary LHS in the content of a naming authority PID if available, empty list otherwise

        @return LHSadresses type list: Primary LHS IP adresses
        """
        LHSadresses = []
        for i in range(len(self.values)):
            if type(self.values[i]['data']) is dict:
                if ('servers' in self.values[i]['data']['value'] and 'address' in self.values[i]['data']['value']['servers'][0]):
                    ipAddress = self.values[i]['data']['value']['servers'][0]['address']
                    if self.values[i]['data']['value']['primarySite']:
                        LHSadresses.append(ipAddress)
        return LHSadresses
    
    def getMirrorLHSadresses(self):
        """
        gets IP adresses of all mirror LHS in the content of a naming authority PID if available, empty list otherwise

        @return LHSadresses type list: Mirror LHS IP adresses
        """
        LHSadresses = []
        for i in range(len(self.values)):
            if type(self.values[i]['data']) is dict:
                if ('servers' in self.values[i]['data']['value'] and 'primarySite' in self.values[i]['data']['value'] and 'address' in self.values[i]['data']['value']['servers'][0]):
                    ipAddress = self.values[i]['data']['value']['servers'][0]['address']
                    if not self.values[i]['data']['value']['primarySite']:
                        LHSadresses.append(ipAddress)
        return LHSadresses
    
    def hasMultiPrimary(self):
        """
        True if the naming authority PID has MultiPrimaries, False otherwise

        @return multiPrim type boolean: has naPID MultiPrimaries
        """
        multiPrim = False
        for i in range(len(self.values)):
            if ('multiPrimary' in self.values[i]['data']['value']):
                multiPrim = self.values[i]['data']['value']['multiPrimary']
        return multiPrim


###############
def test():        
    """
    performs tests on PIDs with Types
    """     
    # xmpl_PID  = "11148/0000-0011-2AC8-D"            # ordinary PID
    xmpl_PID  = "11022/0000-0001-30FC-D"            # ordinary PID, contains oldTyID = "Authors"
    xmpl_PID  = "11022/0000-0001-30FE-B"            # ordinary PID, contains tyID = "21.T11148/21c5a7eba95c2e8f8bb8"
    xmpl_oldTyID = "Authors"
    xmpl_TypeReg = "http://dtr-test.pidconsortium.eu/"
    orig0_NA = "0.NA/21.11101"
    tst_instance = { "Mandatory-Properties-DataCite" : {"creators" : [ {"creator" : {"creatorName": "m\u00fcller, hans-heinrich" } } ], "identifier" : { "identifier-Value" : "10.123/some_text" , "identifier-Attribute" : {"identifierType" : "DOI" } }, "publicationYear" : "2009", "publisher" : "(GWDG)", "resourceType" : { "resourceType-Value" : "some_text" , "resourceType-Attribute" : { "resourceTypeGeneral" : "Dataset" } }, "titles" : [ { "title": {"title-Value": "some title text" } } ] } }
    searchString = "previous"

    pid  = PID(xmpl_PID) 
    print("pid.id:", pid.id)
    NApid = naPID(orig0_NA)
    print("pid.id:", NApid.id)

    print(">>>> NApid.getLHSadresses():\n" + str(NApid.getLHSadresses()))
    print(">>>> NApid.getLHSinterfaces():\n" + json.dumps(NApid.getLHSinterfaces(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print(">>>> NApid.getPrimaryLHSadresses():\n" + str(NApid.getPrimaryLHSadresses()))
    print(">>>> NApid.getMirrorLHSadresses():\n" + str(NApid.getMirrorLHSadresses()))
    print(">>>> NApid.gethasMultiPrimary():\n" + str(NApid.hasMultiPrimary()))
    
    print(">>>> pid.getContentFromProxy():\n" + json.dumps(pid.getContentFromProxy(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print(">>>> pid.isType():\n" + json.dumps(pid.isType(), sort_keys=True,indent=2, separators=(',', ' : ')))
    print(">>>> pid.getAllTypes():\n" + json.dumps(pid.getAllTypes(), sort_keys=True,indent=2, separators=(',', ' : ')))

##############                                                                                                                                   
if __name__ == "__main__":

    test()
