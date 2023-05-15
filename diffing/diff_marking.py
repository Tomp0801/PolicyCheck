from xmldiff import main
from xmldiff import actions
from lxml import etree
import re
from copy import deepcopy

def _change_index(s):
    match = re.search("(.*)\[(\d+)\]$", s)
    if match:
        num = int(match.group(2))
        s = f"{match.group(1)}[{num+1}]"
    return s

def diff_mark_xml(old_tree, new_tree):
    edit_tree = deepcopy(old_tree)
    edit_script = main.diff_trees(old_tree, new_tree,
                    diff_options={'F': 0.5, 'ratio_mode': 'fast'})

    for action in edit_script:
        if isinstance(action, actions.DeleteNode):
            try:
                node = edit_tree.xpath(action.node)[0]
                node.attrib['class'] = 'DeleteNode'
            except Exception as e:
                print("DeleteNode", e, action.node, node)
        if isinstance(action, actions.UpdateTextIn):
            try:
                node = edit_tree.xpath(action.node)[0]
                node.attrib['class'] = 'UpdateTextIn'
            except Exception as e:
                print("UpdateTextIn", e, action.node, node)
        if isinstance(action, actions.InsertNode):
            try:
                node = edit_tree.xpath(action.target)[0]
                new_node = etree.SubElement(node, action.tag, attrib={'class':'InsertNode'})
                new_node.text = "NEW TEXT"
                node.insert(action.position, node[-1])
            except Exception as e:
                print("InsertNode", e, action.target)
    return edit_tree

def diff_mark_text(old_text, new_text):
    old_tree = etree.XML(old_text)
    new_tree = etree.XML(new_text)
    edit_tree = diff_mark_xml(old_tree, new_tree)
    return etree.tostring(edit_tree, pretty_print=True).decode('utf-8')

def diff_mark_file(old_file, new_file, save_file):
    with open(old_file, "r") as f:
        old_text = f.read()
    with open(new_file, "r") as f:
        new_text = f.read()
    edit_text = diff_mark_text(old_text, new_text)
    with open(save_file, "w") as f:
        f.write("<html>")
        f.write('<head><link rel="stylesheet" type="text/css" href="diff.css" /></head>\n')
        f.write("<body>")
        f.write(edit_text)
        f.write("</body></html>")
