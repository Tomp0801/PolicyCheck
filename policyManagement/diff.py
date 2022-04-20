from difflib import SequenceMatcher, Differ, unified_diff
from ntpath import join
import opcode
from pickletools import opcodes
import sys
from Opcodes import Opcode
from HtmlDoc import HtmlDoc


def diff(fileOld, fileNew, useFiles=False):
    if useFiles:
        fh_a = open(fileOld, 'r', encoding='utf-8')
        fh_b = open(fileNew, 'r', encoding='utf-8')
        a = fh_a.read()
        b = fh_b.read()
        fh_a.close()
        fh_b.close()
    else:
        a = fileOld
        b = fileNew
    differ = SequenceMatcher(isjunk=lambda x: x in " \t")
    differ.set_seqs(a, b)

    print("ratio: %.3f (%.3f)" % (differ.ratio(), differ.quick_ratio()))

    opcodes = differ.get_opcodes()

    ops = [0, 0, 0, 0]

    for op in opcodes:
        if op[0] == 'replace':
            ops[0] += op[2] - op[1]
        elif op[0] == 'delete':
            ops[1] += op[2] - op[1]
        elif op[0] == 'insert':
            ops[2] += op[4] - op[3]
        elif op[0] == 'equal':
            ops[3] += op[2] - op[1]

    print("%.3f %% equal" % (100* ops[3] / (ops[0] + ops[1] + ops[2] + ops[3])))
    print("%i opcodes, %i deletions, %i inserts, %i replacements, %i equal" % (len(opcodes), ops[1], ops[2], ops[0], ops[3]))

    return opcodes

def reduceOpcodes(opcodes):
    newCodes = []
    for oc in opcodes:
        if oc.type == 'equal':
            continue
        checkAndAppend(newCodes, oc)

    return newCodes

def checkAndAppend(opcodeArray, opcode):
    newOcs = opcode.expandToTag()
    for oc in newOcs:
        oc.expandReplace()
        if len(opcodeArray) == 0:
            opcodeArray.append(oc)
        joined = opcodeArray[-1].joinIfNeighbor(oc)
        if not joined:
            opcodeArray.append(oc)

def diffHtml(fileOld, fileNew, useFiles=False):
    opcodes = diff(fileOld, fileNew, useFiles=useFiles)

    if useFiles:
        with open(fileOld, 'r', encoding='utf-8') as f:
            textOld = f.read()
        with open(fileNew, 'r', encoding='utf-8') as f:
            textNew = f.read()
    else:
        textOld = fileOld
        textNew = fileNew

    oldLen = len(opcodes)
    opcodes = Opcode.getOpcodeArray(opcodes, textOld, textNew)
 
    opcodes = reduceOpcodes(opcodes)

    print("opcodes reduced from %i to %i" % (oldLen, len(opcodes)))

    for oc in opcodes:
        print(oc)

    htmlBuild = ""

    #for line in unified_diff(textOld, textNew, fromfile='before.py', tofile='after.py'):
    #    sys.stdout.write(line)
    
    #for tag, i1, i2, j1, j2 in opcodes:
        #print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
     #           tag, i1, i2, j1, j2, textFrom[i1:i2], textTo[j1:j2]))

    index = 0
    for op in opcodes:
        if op[0] == 'replace':
            tooltip = textOld[op[1]:op[2]]
            startTag = '<span style="color:blue" title="' + tooltip + '"><b>'
            endTag = "</b></span>"
            start = op[3]
            end = op[4]
            text = textNew[start:end]
        elif op[0] == 'delete':
            startTag = '<span style="color:red"><b>'
            endTag = "</b></span>"
            start = op[1]
            end = op[2]
            text = textOld[start:end]
        elif op[0] == 'insert':
            startTag = '<span style="color:green"><b>'
            endTag = "</b></span>"
            start = op[3]
            end = op[4]
            text = textNew[start:end]
        elif op[0] == 'equal':
            startTag = ""
            endTag = ""
            start = op[1]
            end = op[2]
            text = textOld[start:end]

        htmlBuild += startTag + text + endTag
        index = end
    
    return htmlBuild


#fileA = "examples/reddit/general2018-03-21.txt"
#fileB = "examples/reddit/general2018-06-08.txt"
#fileC = "examples/reddit/general2018-09-24.txt"
fileB = "test/test0.txt"
fileC = "test/test1.txt"

#with open("test/output.html", 'w', encoding='utf-8') as f:
#    f.write(diffHtml(fileB, fileC))