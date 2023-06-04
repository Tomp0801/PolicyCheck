from xmldiff import main, actions, formatting
from lxml import etree
import re
from copy import deepcopy
from bs4 import BeautifulSoup, NavigableString

def _change_index(s):
    match = re.search("(.*)\[(\d+)\]$", s)
    if match:
        num = int(match.group(2))
        s = f"{match.group(1)}[{num+1}]"
    return s

def diff_mark_xml(old_tree, new_tree, add_head=True):
    formatter = formatting.XMLFormatter(normalize=formatting.WS_NONE, pretty_print=False, 
                                        text_tags=['p', 'span', 'h1', 'h2', 'h3', 'h4'], 
                                        formatting_tags=['strong', 'b', 'i', 'br'], use_replace=True)
    diff_xml = main.diff_trees(old_tree, new_tree, formatter=formatter, diff_options={'F':0.5, 'ratio_mode': 'accurate'})
    diff_tree = BeautifulSoup(diff_xml, 'lxml')
    for node in diff_tree.descendants:
        _mark_node(diff_tree, node)
    if add_head:
        _add_html_head(diff_tree)
    return diff_tree

def diff_mark_text(old_text, new_text, add_head=True):
    old_tree = etree.XML(old_text)
    new_tree = etree.XML(new_text)
    diff_tree = diff_mark_xml(old_tree, new_tree, add_head)
    return diff_tree.prettify(encoding='utf-8').decode('utf-8')

def diff_mark_file(old_file, new_file, save_file, add_head=True):
    with open(old_file, "r") as f:
        old_text = f.read()
    with open(new_file, "r") as f:
        new_text = f.read()
    diff_xml = diff_mark_text(old_text, new_text, add_head)
    with open(save_file, "w") as f:
        f.write(diff_xml)

def _add_html_head(soup):
    if not "html" in soup:
        html_tag = soup.new_tag("html")
        soup.insert(0, html_tag)
    head_tag = soup.new_tag("head")
    css_tag = soup.new_tag("link")
    css_tag['rel'] = "stylesheet" 
    css_tag['type'] = "text/css"
    css_tag['href'] = "diff.css"
    head_tag.insert(0, css_tag)
    soup.html.insert(0, head_tag)

def _add_class(node, class_attrs):
    if not 'class' in node.attrs:
        node.attrs['class'] = []
    for attr in class_attrs:
        if not attr in node.attrs:
            node.attrs['class'].append(attr)

def _get_tooltip_child(node):
    for child in node.contents:
        if child.name != "span":
            continue
        if not child.has_attr('class'):
            continue
        if not 'tooltiptext' in child.attrs["class"]:
            continue
        return child
    return None

def _add_tooltip(root, node, tooltip_text):
    _add_class(node, ['tooltip'])
    tooltip_node = _get_tooltip_child(node)
    if tooltip_node is not None:
        tooltip_node.string += "<br>" + tooltip_text
    else:
        tooltip_text_node = root.new_tag('span')
        tooltip_text_node.string = tooltip_text
        _add_class(tooltip_text_node, ['tooltiptext'])
        node.insert(0, tooltip_text_node)

def _is_attr_modification(node):
    if 'diff:delete-attr' in node.attrs:
        return True
    if 'diff:add-attr' in node.attrs:
        return True
    if 'diff:update-attr' in node.attrs:
        return True
    if 'diff:rename-attr' in node.attrs:
        return True
    
def _delete_contents(node):
    node.string = ""

def _set_text(node, new_text):
    for c in node.contents:
        if isinstance(c, NavigableString):
            c.string.replace_with(new_text)

def _get_text(node):
    text = ""
    for c in node.descendants:
        if isinstance(c, NavigableString):
            text += c.string
    return text

def _mark_node(root, node):
    if isinstance(node, NavigableString):
        pass
    elif node.name=="diff:insert":
        node.name = "span"
        _add_class(node, ['InsertNode', 'PolicyDiff'])
    elif 'diff:insert' in node.attrs:
        _add_class(node, ['InsertNode', 'PolicyDiff'])
    elif node.name=="diff:delete":
        if re.fullmatch("\s*", _get_text(node)):
            pass
        else:
            node.name = "span"
            _add_class(node, ['DeleteNode', 'PolicyDiff'])
            _text = _get_text(node)
            _delete_contents(node)
            _add_tooltip(root, node, f"Deleted '{_text}'")
            _set_text(node, "[...]")
    elif 'diff:delete' in node.attrs:
        if re.fullmatch("\s*", _get_text(node)):
            pass
        else:
            _add_class(node, ['DeleteNode', 'PolicyDiff'])
            _text = _get_text(node)
            _delete_contents(node)
            _add_tooltip(root, node, f"Deleted '{_text}'")
            _set_text(node, "[...]")
    elif node.name=='diff:replace':
        node.name = "span"
        _add_class(node, ['UpdateTextIn', 'PolicyDiff'])
        _add_tooltip(root, node, f"Changed from '{node.attrs['old-text']}'")
    elif 'diff:replace' in node.attrs:
        _add_class(node, ['UpdateTextIn', 'PolicyDiff'])
        _add_tooltip(root, node, f"Changed from '{node.attrs['old-text']}'")
    elif 'diff:rename' in node.attrs:
        _add_class(node, ['RenameNode', 'PolicyDiff'])
        _add_tooltip(root, node, f"This element was renamed from {node.attrs['diff:rename']} to {node.name}")
    elif _is_attr_modification(node):
        _add_class(node, ['AttribModification']) # 'PolicyDiff'
        _add_tooltip(root, node, 'Attributes were modified')
    elif 'diff:' in node.name:
        print(f"Unhandled diff node {node.name}")
    else:
        for attr in node.attrs:
            if 'diff:' in attr:
                print(f"Unhandled node '{node.name}' with attributes {node.attrs}")
                break