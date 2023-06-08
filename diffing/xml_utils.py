import re
from bs4 import NavigableString

def xml_change_index(s):
    match = re.search("(.*)\[(\d+)\]$", s)
    if match:
        num = int(match.group(2))
        s = f"{match.group(1)}[{num+1}]"
    return s

def xml_add_class(node, class_attrs):
    if not 'class' in node.attrs:
        node.attrs['class'] = []
    for attr in class_attrs:
        if not attr in node.attrs:
            node.attrs['class'].append(attr)
    
def xml_delete_contents(node):
    node.string = ""

def xml_set_text(node, new_text):
    for c in node.contents:
        if isinstance(c, NavigableString):
            c.string.replace_with(new_text)

def xml_get_text(node):
    text = ""
    for c in node.descendants:
        if isinstance(c, NavigableString):
            text += c.string
    return text

def xml_delete_empty(soup, tags=['span', 'p']):
    whitespace_pattern = re.compile("\s*", re.MULTILINE)
    del_nodes = []
    for d in soup.descendants:
        if isinstance(d, NavigableString):
            continue
        if d.name in tags:
            if re.fullmatch(whitespace_pattern, d.text):
                del_nodes.append(d)
    for n in del_nodes:
        n.decompose()