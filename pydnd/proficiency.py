from enum import Enum

# from documentation :)
class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    
class Proficiency(OrderedEnum):
    NONE            = 0
    SEMIPROFICIENCY = 1
    PROFICIENCY     = 2
    EXPERTISE       = 3

    def color(self):
        if self is Proficiency.PROFICIENCY:
            return 'black'
        elif self is Proficiency.EXPERTISE:
            return 'expertise'
        else:
            return 'white'

def is_proficiency(string):
    return string.upper() in Proficiency.__members__.keys()

def proficiency(string):
    return Proficiency[string.upper()]

