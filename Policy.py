from datetime import datetime
import json
from datetime import datetime
import requests
import hashlib
import re
import sys

class PolicyTypes:
    UserAgreement = "UserAgreement"
    PrivacyPolicy = "PrivacyPolicy"
    NotDetermined = "NotDetermined"

class Policy:
    dateFormat = "%Y-%m-%d %H:%M"

    def __init__(self, name, url, company="", type=PolicyTypes.NotDetermined):
        self.name = name
        self.company = company
        self.type = type
        self.source = url
        self.hash = ""
        self.datePublished = datetime(1970, 1, 1, 0, 0)         # TODO extract from content
        self.dateLastChecked = datetime.utcnow()
        self.content = ""
        self.plainText = ""

    @staticmethod
    def fromJsonFile(jsonFile):
        with open(jsonFile, "r") as f:
            jsonObj = json.load(f)

        return Policy.fromJson(jsonObj)

    @staticmethod
    def fromJson(jsonObj):
        policyObj = Policy(jsonObj["name"], jsonObj["source"], jsonObj["company"], jsonObj["type"])
        policyObj.hash = jsonObj["hash"]
        policyObj.datePublished = datetime.strptime(jsonObj["datePublished"], Policy.dateFormat)
        policyObj.dateLastChecked = datetime.strptime(jsonObj["dateLastChecked"], Policy.dateFormat)
        policyObj.content = jsonObj["content"]
        policyObj.plainText = jsonObj["plainText"]

        return policyObj
        

    def update(self):
        self.dateLastChecked = datetime.now()
        newPolicy = self.fetchPolicy()
        newHash = self.__getHash(newPolicy)
        if newHash != self.hash:
            print("The policy seems to have been updated!")
            self.hash = newHash
            self.content = newPolicy
            self.HtmlToPlain()
            return True
        else:
            print("Policy hasn't changed")
            return False

    def fetchPolicy(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
        r = requests.get(self.source, headers=headers)
        if r.status_code != 200:
            raise Exception("Couldn't reach URL %s (%i)" % (self.source, r.status_code))
        else:
            return r.text

    def HtmlToPlain(self):
        # TODO reduce to only interesting div
        temp = re.sub("<.*>", "", self.content)     # remove html tags
        self.plainText = re.sub("\s\s+", "", temp)  # remove 2+ whitespaces

    def toJsonFile(self, jsonFile):
        with open(jsonFile, "w") as f:
            f.write(self.toJson())

    def toJson(self):
        objDict = {}
        objDict["name"] = self.name
        objDict["source"] = self.source
        objDict["company"] = self.company
        objDict["type"] = self.type
        objDict["hash"] = self.hash
        objDict["content"] = self.content
        objDict["plainText"] = self.plainText
        objDict["datePublished"] = self.datePublished.strftime(Policy.dateFormat)
        objDict["dateLastChecked"] = self.dateLastChecked.strftime(Policy.dateFormat)
        return json.dumps(objDict, sort_keys=False, indent=4)

    @staticmethod
    def __getHash(text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()


#p = Policy("Reddit User Agreement", "https://www.redditinc.com/policies/user-agreement")


p = Policy.fromJsonFile("test.json")

p.update()

p.toJsonFile("test.json")