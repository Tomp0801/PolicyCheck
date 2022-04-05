import re

class HtmlDoc:
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
        plainText = re.sub("\s\s+", "", temp)  # remove 2+ whitespaces
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

