from enum import Enum

class Vantage (Enum):
    NOTHING      = 'nothing'     
    ADVANTAGE    = 'advantage'   
    DISADVANTAGE = 'disadvantage'
    VANTAGE      = 'vantage'     

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
