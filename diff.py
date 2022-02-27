from difflib import SequenceMatcher, Differ, unified_diff
from pickletools import opcodes
import sys

def diff(file1, file2):
    a = open(file1, 'r', encoding='utf-8')
    b = open(file2, 'r', encoding='utf-8')
    differ = SequenceMatcher(isjunk=lambda x: x in " \t")
    differ.set_seqs(a.read(), b.read())

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

    a.close()
    b.close()

    return opcodes

def diffHtml(fileFrom, fileTo):
    opcodes = diff(fileFrom, fileTo)
    with open(fileFrom, 'r', encoding='utf-8') as f:
        textFrom = f.read()
    with open(fileTo, 'r', encoding='utf-8') as f:
        textTo = f.read()

    htmlBuild = ""

    for line in unified_diff(textFrom, textTo, fromfile='before.py', tofile='after.py'):
        sys.stdout.write(line)
    
    #for tag, i1, i2, j1, j2 in opcodes:
        #print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
     #           tag, i1, i2, j1, j2, textFrom[i1:i2], textTo[j1:j2]))

    index = 0
    for op in opcodes:
        if op[0] == 'replace':
            startTag = '<span style="color:blue"><b>'
            endTag = "</b></span>"
            start = op[3]
            end = op[4]
            text = textTo[start:end]
        elif op[0] == 'delete':
            startTag = '<span style="color:red"><b>'
            endTag = "</b></span>"
            text = "- deleted -"
        elif op[0] == 'insert':
            startTag = '<span style="color:green"><b>'
            endTag = "</b></span>"
            start = op[1]
            end = op[2]
            text = textFrom[start:end]
        elif op[0] == 'equal':
            startTag = ""
            endTag = ""
            start = op[1]
            end = op[2]
            text = textFrom[start:end]

        htmlBuild += startTag + text + endTag
        index = end
    
    return htmlBuild


fileA = "examples/reddit/general2018-03-21.txt"
fileB = "examples/reddit/general2018-06-08.txt"
fileC = "examples/reddit/general2018-09-24.txt"

with open("test/output.html", 'w', encoding='utf-8') as f:
    f.write(diffHtml(fileB, fileC))