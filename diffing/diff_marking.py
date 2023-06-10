from xmldiff import main, formatting
from lxml import etree
import re
from bs4 import BeautifulSoup, NavigableString
import os

from .xml_utils import xml_add_class, xml_delete_contents, xml_get_text, xml_set_text, xml_delete_empty, xml_has_direct_text

class Differ:
    def __init__(self, old, new, 
                 F=0.5,
                 ratio_mode='accurate', 
                 use_replace=True):
        self._old_tree = Differ._get_tree(old)
        self._new_tree = Differ._get_tree(new)

        self._diff_options = {'F': F, 'ratio_mode': ratio_mode}
        self._formatter = formatting.XMLFormatter(normalize=formatting.WS_NONE, 
                                        pretty_print=False, 
                                        text_tags=['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'], 
                                        formatting_tags=['strong', 'b', 'i', 'br', 'em', 'u'], 
                                        use_replace=use_replace)

        self.make_diffs()
        for node in self._diff_soup.descendants:
            self._mark_node(node)
        xml_delete_empty(self._diff_soup, tags=['span', 'p', 
                                                 'diff:delete', 'diff:insert', 'diff:replace'])
        self._add_html_head()

    @staticmethod
    def _get_tree(source):
        if isinstance(source, str):
            if os.path.exists(source):
                with open(source, "r") as f:
                    text = f.read()
            else:
                text = source
            return etree.XML(text)
        elif isinstance(source, etree.XML):
            return source
        else:
            raise TypeError(f"XML source must be a path, XML string or etree.XML. Got {type(source)} instead")

    def make_diffs(self):
        self._diff_tree = main.diff_trees(self._old_tree, self._new_tree, 
                                          formatter=self._formatter, 
                                          diff_options=self._diff_options)
        self._diff_soup = BeautifulSoup(self._diff_tree, 'lxml')
        self._root = self._diff_soup

    def _mark_node(self, node):
        handled = False
        if isinstance(node, NavigableString):
            return
        # rename to span if diff is node name
        if node.name.startswith("diff:"):
            node.attrs[node.name] = ""
            node.name = "span"
        
        # insert, delete and replace
        if 'diff:insert' in node.attrs:
            if xml_has_direct_text(node):
                xml_add_class(node, ['InsertNode', 'PolicyDiff'])
            else:
                xml_add_class(node, ['InsertEmptyNode', 'PolicyDiff'])
            handled = True
        elif 'diff:delete' in node.attrs:
            if re.fullmatch("\s*", xml_get_text(node)):
                pass
            else:
                xml_add_class(node, ['DeleteNode', 'PolicyDiff'])
                _text = xml_get_text(node)
                xml_delete_contents(node)
                self._add_tooltip(node, f"Deleted '{_text}'")
                xml_set_text(node, "[...]")
            handled = True
        elif 'diff:replace' in node.attrs:
            xml_add_class(node, ['UpdateTextIn', 'PolicyDiff'])
            self._add_tooltip(node, f"Changed from '{node.attrs['old-text']}'")
            handled = True

        # others: rename, attributes, moved
        if 'diff:rename' in node.attrs:
            xml_add_class(node, ['RenameNode', 'PolicyDiff'])
            self._add_tooltip(node, f"This element was renamed from {node.attrs['diff:rename']} to {node.name}")
            handled = True
        if Differ._is_attr_modification(node):
            xml_add_class(node, ['AttribModification']) # 'PolicyDiff'
            #self._add_tooltip(node, 'Attributes were modified')
            handled = True
        if 'diff:move' in node.attrs:
            xml_add_class(node, ['MoveNode']) # 'PolicyDiff'
            self._add_tooltip(node, f'Was moved from {node.attrs["old_path"]}')
            handled = True

        # warn if unhandled
        if not handled:
            if 'diff:' in node.name:
                print(f"Unhandled diff node {node.name}")
            else:
                for attr in node.attrs:
                    if 'diff:' in attr:
                        print(f"Unhandled node '{node.name}' with attributes {node.attrs}")
                        break
    
    def xml_as_text(self):
        return self._diff_soup.prettify(encoding='utf-8').decode('utf-8')
    
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(self.xml_as_text())

    def _add_html_head(self):
        if not "html" in self._diff_soup:
            html_tag = self._diff_soup.new_tag("html")
            self._diff_soup.insert(0, html_tag)
        head_tag = self._diff_soup.new_tag("head")
        css_tag = self._diff_soup.new_tag("link")
        css_tag['rel'] = "stylesheet" 
        css_tag['type'] = "text/css"
        css_tag['href'] = "diff.css"
        head_tag.insert(0, css_tag)
        self._diff_soup.html.insert(0, head_tag)

    def _add_tooltip(self, node, tooltip_text):
        xml_add_class(node, ['tooltip'])
        tooltip_node = Differ._get_tooltip_child(node)
        if tooltip_node is not None:
            tooltip_node.string += "<br>" + tooltip_text
        else:
            tooltip_text_node = self._root.new_tag('span')
            tooltip_text_node.string = tooltip_text
            xml_add_class(tooltip_text_node, ['tooltiptext'])
            node.insert(0, tooltip_text_node)

    @staticmethod
    def _is_attr_modification(node):
        if 'diff:delete-attr' in node.attrs:
            return True
        if 'diff:add-attr' in node.attrs:
            return True
        if 'diff:update-attr' in node.attrs:
            return True
        if 'diff:rename-attr' in node.attrs:
            return True
    
    @staticmethod
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