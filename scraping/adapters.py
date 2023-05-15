import requests
from bs4 import BeautifulSoup, NavigableString


class Adapter:
    def __init__(self, file=None, url=None) -> None:
        if file is not None:
            self.file = file
        elif url is not None:
            self.file = "tmp.html"

        if url is not None:
            Adapter._download_file(url, self.file)

        with open(self.file, "r") as f:
            self._raw_content = f.read()
        self._prepare_soup()
        self._remove_non_text()
        self._remove_empty_wrappers(["div", "p"])

    def _prepare_soup(self):
        self._soup = BeautifulSoup(self._raw_content, "lxml")

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
    
    def save(self, file):
        with open(file, "w") as f:
            f.write(self._soup.prettify())

    def get_text_of_type(self, type):
        texts = []
        for d in self._soup.descendants:
            if d.name==type:
                texts.append(d.get_text())
        return texts

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
            n.decompose()

    def _remove_empty_wrappers(self, wrappers):
        # first collect nodes, then delete them
        divs = []
        for d in self._soup.descendants:
            if d.name in wrappers:
                if d.string is None:
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
    def __init__(self, file=None, url=None) -> None:
        super().__init__(file, url)

    def _prepare_soup(self):
        soup = BeautifulSoup(self._raw_content, "lxml")
        self._soup = soup.find(id="content")
        self._remove_types(["select"])
        self._class_to_type("h4", "h4")
        self._class_to_type("h3", "h3")


class GoogleAdapter(Adapter):
    def __init__(self, file=None, url=None) -> None:
        super().__init__(file, url)

    def _prepare_soup(self):
        soup = BeautifulSoup(self._raw_content, "lxml")
        self._soup = soup.find(attrs={"role": "article"})
        self._remove_empty_wrappers(["c-wiz"])