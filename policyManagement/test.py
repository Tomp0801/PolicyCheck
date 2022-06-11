from diff import diffHtml, reduceOpcodes, diff
from Opcodes import Opcode
import re 
from lxml import html

def readToPlain(file):
    # read doc
    with open(file, 'r') as f:
        text0 = f.read()

    temp = text0
    temp = re.sub("<br>", "{{\n}}", temp)
    temp = re.sub("<.*?>", "", temp)
    temp = re.sub("\{\{\n\}\}", "<br>", temp, re.MULTILINE)
    return text0, temp

text0, plain0 = readToPlain("test/test0.txt")
text1, plain1 = readToPlain("test/test1.txt")

print(plain0)
print(plain1)

diff(plain0, plain1)

tree1 = html.document_fromstring(text1)


def printChildren(el, level=0):
    print(" "*level + "|_  " + el.tag, el.text)
    for child in el.getchildren():
        printChildren(child, level+1)


printChildren(tree1)