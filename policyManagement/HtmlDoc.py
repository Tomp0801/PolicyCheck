import re

class HtmlDoc:


    @staticmethod
    def reduceToBody(content):
        start = re.search("<body.*>", content)
        end = re.search("</body>", content)

        if start and end:
            return content[start.end(0):end.start(0)]
        else:
            print("Error: html body not found")
            return content