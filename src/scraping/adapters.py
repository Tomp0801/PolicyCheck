import requests
from bs4 import BeautifulSoup, NavigableString, Comment
import itertools
import re


class Adapter:
    def __init__(self, file=None, url=None, 
                 sectionize=True, wrap_text=True) -> None:
        if file is not None:
            self.file = file
        elif url is not None:
            self.file = "tmp.html"

        if url is not None:
            Adapter._download_file(url, self.file)

        with open(self.file , "r", encoding='utf-8') as f:
            self._raw_content = f.read()
        self._root = BeautifulSoup(self._raw_content, "lxml-html")
        self._prepare_soup()
        self._remove_non_text()
        # remove formatting
        self._remove_wrappers(["div", "p"], only_if_empty=True)
        self._remove_wrappers(["strong", "b", "i", "u", "em", "span"])
        if sectionize:
            self._sectionize(depth=6)
        if wrap_text:
            self._wrap_naked_text("p")
        self._remove_classes()
        self._remove_links()
        # remove empty tags

    def _prepare_soup(self):
        self._soup = self._root

    def get_contained_types(self):
        names = set()
        for d in self._soup.descendants:
            names.add(d.name)
        return list(names)
    
    def get_contained_classes(self):
        classes = set()
        for d in self._soup.descendants:
            if not isinstance(d, NavigableString) and 'class' in d.attrs:
                for c in d['class']:
                    classes.add(c)
        return list(classes)
    
    def _remove_classes(self):
        for d in self._soup.descendants:
            if not isinstance(d, NavigableString) and 'class' in d.attrs:
                del d['class']
    
    def _remove_links(self):
        links = []
        for d in self._soup.descendants:
            if not isinstance(d, NavigableString) and d.name == "a":
                links.append(d)
        for l in links:
            l.replace_with(NavigableString(l.get_text()))

    def save(self, file):
        with open(file, "w") as f:
            f.write(self._soup.prettify())

    def get_text_of_type(self, type):
        texts = []
        for d in self._soup.descendants:
            if d.name==type:
                texts.append(d.get_text())
        return texts
    
    def _sectionize(self, soup=None, h_tag=1, depth=4):
        if soup is None:
            soup = self._soup
        elif isinstance(soup, NavigableString):
            return
        # wrap all headings and next siblings into sections
        section_tags = soup.find_all(f"h{h_tag}")
        while len(section_tags) == 0 and h_tag < depth:
            h_tag += 1
            section_tags = soup.find_all(f"h{h_tag}")

        n = 1
        for el in section_tags:
            section = self._wrap_with_siblings(el, "section", stop_tags={f"h{h_tag}"})
            section.attrs['level'] = f"{h_tag}"
            section.attrs['n'] = f"{n}"
            n += 1
            if depth >= h_tag:
                self._sectionize(section, h_tag + 1, depth)

    def _wrap_naked_text(self, wrap_with="p"):
        formatting_tags = ["em", "strong", "b", "i", "u", "span"]
        whitespace = re.compile("\s+", re.MULTILINE)
        stop_tags = set(["section", "div", "p", "ul"])
        stop_tags.add(wrap_with)
        # dont wrap, if inside one of these tags:
        dont_wrap_if_in = ["p", "a", "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "li", "ul"]
        for d in self._soup.descendants:
            if isinstance(d, NavigableString):
                # dont wrap whitespace
                if re.fullmatch(whitespace, d):
                    continue
                # treat formatting tags as if they arent there
                while d.parent.name in formatting_tags:
                    d = d.parent
                if not d.parent.name in dont_wrap_if_in:
                    self._wrap_with_siblings(d, wrap_with, stop_tags, stop_at_self=False)

    def _wrap_with_siblings(self, el, wrap_tag, stop_tags=[], stop_at_self=True):
        stop_tags = list(stop_tags)
        if stop_at_self:
            stop_tags.append(el.name)
        els = [i for i in itertools.takewhile(
                lambda x: x.name not in stop_tags,
                el.next_siblings)]
        wrap_el = self._root.new_tag(wrap_tag)
        el.wrap(wrap_el)
        for tag in els:
            wrap_el.append(tag)
        return wrap_el

    @staticmethod
    def _download_file(url, file_name):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Couldn't reach URL %s (%i)" % (url, r.status_code))
        else:
            with open(file_name, "w") as f:
                f.write(r.text)

    def _remove_non_text(self, exclude=["br"]):
        # first collect nodes, then delete them
        del_nodes = []
        for d in self._soup.descendants:
            if d.name in exclude:
                continue
            if d.get_text() is None or d.get_text()=="":
                del_nodes.append(d)
        for n in del_nodes:
            if isinstance(n, Comment):
                n.extract()
            else:
                n.decompose()

    def _remove_wrappers(self, wrappers, only_if_empty=False):
        # first collect nodes, then delete them
        divs = []
        for d in self._soup.descendants:
            if d.name in wrappers:
                if d.string is None or not only_if_empty:
                    divs.append(d)
        for d in divs:
            d.unwrap()

    def _remove_types(self, types):
        # first collect nodes, then delete them
        nodes = []
        for d in self._soup.descendants:
            if d.name in types:
                nodes.append(d)
        for d in nodes:
            d.decompose()

    def _class_to_type(self, class_name, type):
        bs = BeautifulSoup("")
        for d in self._soup.descendants:
            if not isinstance(d, NavigableString) and 'class' in d.attrs:
                if class_name in d['class']:
                    d.string.wrap(bs.new_tag(type))




class RedditAdapter(Adapter):
    def __init__(self, file=None, url=None, sectionize=True, wrap_text=True) -> None:
        super().__init__(file, url, sectionize, wrap_text)

    def _prepare_soup(self):
        self._soup = self._root.find(id="content")
        self._remove_types(["select"])
        self._class_to_type("h4", "h4")
        self._class_to_type("h3", "h3")

class GoogleAdapter(Adapter):
    def __init__(self, file=None, url=None, sectionize=True, wrap_text=True) -> None:
        super().__init__(file, url, sectionize, wrap_text)

    def _prepare_soup(self):
        self._soup = self._root.find(attrs={"role": "article"})
        self._remove_wrappers(["c-wiz"], only_if_empty=True)

class TwitterAdapter(Adapter):
    def __init__(self, file=None, url=None, sectionize=True, wrap_text=True) -> None:
        super().__init__(file, url, sectionize, wrap_text)

    def _prepare_soup(self):
        self._soup = self._root.find("main")


def get_adapter_by_name(name, file=None, url=None, sectionize=True, wrap_text=True):
    if name.lower()=="reddit":
        return RedditAdapter(file, url=url, sectionize=sectionize, wrap_text=wrap_text)
    elif name.lower()=="google":
        return GoogleAdapter(file, url=url, sectionize=sectionize, wrap_text=wrap_text)
    elif name.lower()=="twitter":
        return TwitterAdapter(file, url=url, sectionize=sectionize, wrap_text=wrap_text)
    else:
        return Adapter(file, url, sectionize=sectionize, wrap_text=wrap_text)