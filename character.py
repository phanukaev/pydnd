from dataclasses import dataclass

@dataclass
class Item_compact:
    name: str

@dataclass
class Item_with_description:
    name : str
    description: str

    def to_item_compact(self):
        return Item_compact(self.name)

class Named_List:
    def __init__(self, name, datatype):
        self.name = name
        self.type = datatype
        self.internal_list = list()

    def __print_to_tex__(self):
        pass

    def __iter__(self):
        for item in self.internal_list:
            yield item

    def append(self, item):
        if item.__class__ is not self.type:
            raise TypeError ( "tried adding something other than an item with description")
        else:
            self.internal_list.append(item)


class Named_List_compact(Named_List):
    def __init__(self, name):
        super().__init__(name, Item_compact)

class Named_List_with_descriptions(Named_List):
    def __init__(self, name):
        super().__init__(name, Item_with_description)


class Character:
    def __init__(
                    self                ,
                    name        = ""    ,
                    background  = ""    ,
                    player_name = ""    ,
                    race        = ""    ,
                    alignment   = ""    ,
                    experience  = 0
                ):
        self.name = name
        self.background = background
        self.player_name = player_name
        self.race = race
        self.alignment = alignment
        self.experience = experience
