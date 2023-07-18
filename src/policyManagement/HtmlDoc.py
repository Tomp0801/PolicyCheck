import re

class HtmlDoc:
    @staticmethod
    def listAllTags(content):
        tag_pattern = re.compile("</?.*?>")
        name_pattern = re.compile("</?([\w_\d]+)")
        tags = set([])
        for match in re.findall(tag_pattern, content):
            name_match = re.search(name_pattern, match)
            if name_match:
                tags.add(name_match.group(1))
        return sorted(list(tags))
    
    @staticmethod
    def deleteTag(content, tag_name, with_content=False, if_empty=False):
        if if_empty:
            tag_pattern = re.compile(f"<{tag_name} ?.*?></{tag_name}>")
            temp = re.sub(tag_pattern, "", content)
            return temp
        if not with_content:
            tag_pattern = re.compile(f"<['a', 'aside', 'br', 'div', 'hr', 'option', 'p', 'select', 'strong', 'ul']/?{tag_name} ?.*?/?>")
            temp = re.sub(tag_pattern, "", content)
            return temp
        else:
            tag_pattern_a = re.compile(f"<{tag_name}.*?</{tag_name}>", re.MULTILINE + re.DOTALL)
            tag_pattern_b = re.compile(f"<{tag_name}.*?/>")
            match = re.search(tag_pattern_a, content)
            temp = re.sub(tag_pattern_a, "", content)
            #temp = re.sub(tag_pattern_b, "", temp)
            return temp

    @staticmethod
    def selectTag(content, tag_name):
        tag_pattern = re.compile(f"(<{tag_name} ?.*?>)(.*?)(</{tag_name}>)", re.MULTILINE + re.DOTALL)
        match = re.search(tag_pattern, content)
        if match:
            return match.group(2)
        else:
            return None


    @staticmethod
    def removeJavaScript(content):
        temp = re.sub("<script.*>.*</script>", "", content)
        temp = re.sub("<script.*/>", "", temp)
        temp = re.sub("\s\s+", "", temp)  # remove 2+ whitespaces
        return temp

    @staticmethod
    def toPlainText(content):
        temp = re.sub("<br ? /?>", "\n", content)  # replace <br> with \n

        htmlTags = re.compile("<.*?>")

        temp = re.sub(htmlTags, "", temp)     # remove html tags
        plainText = re.sub("\s\s+", " ", temp)  # remove 2+ whitespaces
        return plainText

    @staticmethod
    def reduceToBody(content):
        start = re.search("<body.*>", content)
        end = re.search("</body>", content)

        if start and end:
            return content[start.end(0):end.start(0)]
        else:
            print("Error: html body not found")
            return content

    @staticmethod
    def isInTag(content, index):
        start = index
        end = index
        while start > 0 and not content[start] in "<>":
            start -= 1
        while end < len(content) and not content[end] in "<>":
            end += 1

        if content[start] == '<' and content[end] == '>':
            return True
        elif content[start] == '>' and content[end] == '<':
            return False
        else:
            print("Error?")
            return False

