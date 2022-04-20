import re

class Opcode:
    def __init__(self, opcode, textOld=None, textNew=None):
        self.oc = opcode
        self.textOld = textOld
        self.textNew = textNew

        self.type = opcode[0]
        self.startOld = opcode[1]
        self.endOld = opcode[2]
        self.startNew = opcode[3]
        self.endNew = opcode[4]

    def joinIfNeighbor(self, otherOpcode):
        if self.isNeighboring(otherOpcode):
            return self.join(otherOpcode)
        else:
            return False

    def join(self, otherOpcode):
        if self.type != otherOpcode.type:
            return False

        self.startOld = min(self.startOld, otherOpcode.startOld)
        self.endOld = max(self.endOld, otherOpcode.endOld)

        self.startNew = min(self.startNew, otherOpcode.startNew)
        self.endNew = max(self.endNew, otherOpcode.endNew)

        return True

    def isNeighboring(self, otherOpcode):
        if self.type != otherOpcode.type:
            return False

        if self.type == 'delete':
            # empty space in new text same?
            if self.startNew == otherOpcode.startNew and self.endNew == otherOpcode.endNew:
                return True
        elif self.type == 'insert':
            # insertion point the same?
            if self.startOld == otherOpcode.startOld and self.endOld == otherOpcode.endOld:
                return True
        elif self.type == 'replace':
            # neighboring, if max. 1 space contained between both
            betweenStart = min(self.endOld, otherOpcode.endOld)
            betweenEnd = max(self.startOld, otherOpcode.startOld)
            betweenString = self.textOld[betweenStart:betweenEnd]

            if re.fullmatch("[a-zA-Z]* ?[a-zA-Z]*", betweenString):
                return True

        elif self.type == 'equal':
            if self.endNew == otherOpcode.startNew or otherOpcode.endNew == self.startNew:
                return True

        return False

    def expandReplace(self):
        if self.type != 'replace':
            return
        
        while self.startNew >= 1 and self.textNew[self.startNew-1].isalpha():
            self.startNew -= 1
            self.startOld -= 1

        while self.endNew < len(self.textNew) and self.textNew[self.endNew].isalpha():
            self.endNew += 1
            self.endOld += 1

    def expandToTag(self):
        startsInTag, tagStart = self._startsInTag()
        endsInTag, tagEnd = self._endsInTag()

        # entirely within a tag
        if endsInTag and startsInTag:
            print("Dropping opcode <%s>, because it is within a tag" % str(self))
            return []
        # partially in tag
        elif endsInTag:
            index = self.textNew.find('<')
            if index == -1:
                print("Error: expected to find tag start in text '%s'", self.textNew)
                return [self]
            else:
                self.endNew = index
                print("Clipped opcode <%s>, because it ended in a tag" % str(self))
                return [self]
        elif startsInTag:
            index = self.textNew.find('>') + 1
            if index == -1:
                print("Error: expected to find tag end in text '%s'", self.textNew)
                return [self]
            else:
                self.startNew = index
                print("Clipped opcode <%s>, because it ended in a tag" % str(self))
                return [self]
        elif not endsInTag and not startsInTag:
            return [self]

        # TODO check if tag is within it and split?

    def _startsInTag(self):
        # find tag begin or end before start
        index = self.startNew
        while index > 0:
            if self.textNew[index - 1] == '<':
                return True, index
            elif self.textNew[index - 1] == '>':
                return False, index
            index -= 1
        return False, -1

    def _endsInTag(self):
        index = self.endNew
        while index < len(self.textNew):
            if self.textNew[index] == '>':
                return True, index
            elif self.textNew[index] == '<':
                return False, index
            index += 1
        return False, -1

    def __getitem__(self, item):
         return self.oc[item]

    def __repr__(self) -> str:
        return self.type + " [" + self.textOld[self.startOld:self.endOld] + "] -> [" +self.textNew[self.startNew:self.endNew] + "]"

    @staticmethod
    def getOpcodeArray(opcodes, textOld=None, textNew=None):
        opcodeObjects = []
        for oc in opcodes:
            opcodeObjects.append(Opcode(oc, textOld, textNew))
        return opcodeObjects