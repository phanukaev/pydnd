from enum import Enum

class Vantage (Enum):
    NOTHING      = 'nothing'     
    ADVANTAGE    = 'advantage'   
    DISADVANTAGE = 'disadvantage'
    VANTAGE      = 'vantage'     

    def color(self):
        if self is Vantage.NOTHING:
            return 'black'
        else:
            return self.name.lower()

    def __add__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented

        if self == Vantage.NOTHING:
            return other
        elif other == Vantage.NOTHING:
            return self
        elif self == other:
            return self
        else: # neither argument is NOTHING and they are different.
            return Vantage.VANTAGE
        
def is_vantage(string):
    return string.upper() in Vantage.__members__.keys()

def vantage(string):
    return Vantage[string.upper()]

