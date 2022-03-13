from datetime import datetime
from http.client import HTTPException
import json
from datetime import datetime
import requests
import hashlib
import re

class PolicyTypes:
    UserAgreement = "UserAgreement"
    PrivacyPolicy = "PrivacyPolicy"
    NotDetermined = "NotDetermined"

class Policy:
    def __init__(self, name, url, company="", type=PolicyTypes.NotDetermined):
        self.name = name
        self.company = company
        self.type = type
        self.source = url
        self.hash = ""
        self.datePublished = None
        self.dateLastChecked = datetime.now()
        self.content = ""
        self.plainText = ""

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
        self.plainText = re.sub("<.*>", "", self.content)

    def toJson(self):
        return json.dumps(self, default=lambda o: str(o), 
            sort_keys=True, indent=4)

    @staticmethod
    def __getHash(text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()


p = Policy("Reddit User Agreement", "https://www.redditinc.com/policies/user-agreement")

p.update()

with  open("test.json", "w") as f:
    f.write(p.toJson())