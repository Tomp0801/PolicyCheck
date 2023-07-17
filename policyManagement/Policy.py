from datetime import datetime
import json
import requests
import hashlib
import re
import sys
from diff import diffHtml
from HtmlDoc import HtmlDoc

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
        policyObj.content = HtmlDoc.reduceToBody(jsonObj["content"])
        policyObj.plainText = jsonObj["plainText"]

        return policyObj
        
    def loadContentFromFile(self, filename):
        with open(filename, "r") as f:
            self.content = HtmlDoc.reduceToBody(f.read())

    def update(self):
        self.dateLastChecked = datetime.now()
        newPolicy = self.fetchPolicy()
        
        return self._update(newPolicy)

    def updateFromFile(self, filename):
        with open(filename, "r") as f:
            newPolicy = HtmlDoc.reduceToBody(f.read())
        
        return self._update(newPolicy)

    def _update(self, newPolicy):
        oldContent = self.content
        
        newHash = self.__getHash(newPolicy)
        if newHash != self.hash:
            print("The policy seems to have been updated!")
            self.hash = newHash
            self.content = HtmlDoc.removeJavaScript(HtmlDoc.reduceToBody(newPolicy))
            self.HtmlToPlain()

            self.lastDiff = diffHtml(oldContent, self.content)
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
        self.plainText = HtmlDoc.toPlainText(self.content)

    def toJsonFile(self, jsonFile):
        with open(jsonFile, "w") as f:
            f.write(self.toJson())

    def toHtml(self, htmlFile, markDiffs=True):
        with open(htmlFile, "w") as f:
            if markDiffs:
                f.write(self.lastDiff)
            else:
                f.write(self.content)

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



p = Policy.fromJsonFile("test/test.json")
p.loadContentFromFile("test/redditOld.html")
with open("tmp/testOri.txt", "w") as f:
    f.write(p.plainText)
#p.toHtml("tmp/testOri.html", markDiffs=False)
#p.toHtml("test/test.html")
#p.updateFromFile("test/test.html")
p.update()
p.toHtml("tmp/test2.html")



#p.toJsonFile("test/test2.json")
