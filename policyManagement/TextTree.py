from HtmlDoc import HtmlDoc

class TreeElementTypes:
    ROOT = "root"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    ITEM = "item"

class TreeElement:
    def __init__(self, type, content, parent=None):
        self.parent = parent
        self.type = type
        self.content = content

    def get_level(self):
        level = 0
        p = self.parent
        while p is not None:
            level += 1
            p = p.parent
        return level
    
    @staticmethod
    def tree_from_html(html):
        root = TreeElement(TreeElementTypes.ROOT, None)
        tags = HtmlDoc.listAllTags(html)
        