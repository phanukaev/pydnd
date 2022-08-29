from dataclasses import dataclass
import os
import sys

from proficiency import Proficiency
from parsetools import *
from texwrite import print_to_tex


def proficiency_bonus():
    return 2 + ((Class.get_total_level() - 1) // 4)

def added_proficiency_bonus(proficiency_status):
    bonus = proficiency_bonus()

    if proficiency_status == Proficiency.SEMIPROFICIENCY:
        return bonus // 2
    elif proficiency_status == Proficiency.PROFICIENCY:
        return bonus
    elif proficiency_status == Proficiency.EXPERTISE:
        return bonus * 2
    else:
        return 0

###############
#             #
# named lists #
#             #
###############
@dataclass
class Thing:
    name: str

@dataclass
class Thing_With_Description:
    name : str
    description: str

    def to_thing(self):
        return Thing(self.name)

    def __bool__(self):
        return self.description != ''

class Named_List(list):
    def __init__(self, name, iterable = ()):
        self.name = name
        super().__init__(iterable)

    def append(self, item):
        super().append(item)

class Named_List_compact(Named_List):
    def __init__(self, name, iterable = ()):
        super().__init__(name, iterable)

    def parse_input(self, string):
        string = unlines(string.split(','))
        for line in lines(string):
            if not line:
                continue
            self.append(Thing(line))
        # For the reasoning behind this implementation, see the comment at
        # Named_List_with_descriptions.parse_input
        # below.

    def tex_print(self):
        if len(self) == 0:
            return ''
        listcontents = ', '.join((x.name for x in self))
        out = f'\\headedtext{{\\bfseries}}{{{self.name}.}}{{{listcontents}}}{{\\par}}'
        return out


class Named_List_with_descriptions(Named_List):
    def __init__(self, name, iterable = ()):
        super().__init__(name, iterable)

    def parse_input(self, string):
        item_name, description = first_line(string)
        if item_name:
            self.append(Thing_With_Description(item_name, description))
        else:
            for l in lines(description):
                self.append(Thing_With_Description(l, ''))
            # this feels wrong in the context, but is intentional.
            # The intent here is that one should be able to provide
            # a list of things that do not have or need a description
            # without having to write a keywrod every time.
            # For this purpose one may enter something of the form
            #
            # >>> Equip
            # ...     Item1
            # ...     Item2
            #         ...
            #
            # and the interpreter should treat this as a list of
            # items with empty descriptions.

    def compact(self):
        return Named_List_compact(self.name, (x.to_thing() for x in self))

    def tex_print(self, show_name):
        out = ''
        if show_name:
            out += f'\\subsection*{{{self.name}}}\n'
        
        described = list(filter(None, self))
        undescribed = list(filter(lambda x : not x, self))
        out += '\\spacer'.join((
                f'\\headedtext{{\\bfseries}}{{{x.name}}}{{{proc_all_math(x.description)}}}{{\\hspace{{.5em}}}}'
                for x in described))

        if undescribed:
            if described:
                out += '\\spacer\n'
            out += ', '.join((x.name for x in undescribed))

        return out


########################
#                      #
# basic character info #
#                      #
########################

# this one should be used for Name, Race, Background, Alignment, Player
class Named_String:
    def __init__(self, name):
        self.name = name
        self.contents = str()

    def parse_input(self, string):
        self.contents = string

class Class_Level(dict):
    def __init__(self):
        self.first = None
        super().__init__()

    def find_hitdie(self, class_name):
        known_hitdice = \
            { 'Barbarian' : 12
            , 'Fighter'   : 10
            , 'Paladin'   : 10
            , 'Ranger'    : 10
            , 'Warlock'   : 10
            , 'Sorcerer'  :  6
            , 'Wizard'    :  6
            }

        if class_name in known_hitdice.keys():
            return known_hitdice[class_name]
        else:
            return 8 # The hit die for most classes is a d8.

    def parse_input(self, string):
        start, last = last_word(string)

        if last[0] == 'd' and is_int(last[1:]):
            # a hitdie has been specified explicitly.
            hitdie = int(last[1:])
            class_name, level = last_word(start)
        else:
            class_name, level = last_word(string)
            hitdie = self.find_hitdie(class_name)

        self[class_name] = (int(level), hitdie)
        if self.first is None:
            self.first = class_name

    def get_total_level(self):
        return sum(l for l, _ in self.values())

    def get_auto_hitpoints(self):
        total = self.get_total_level() * Con.get_modifier()
        for class_, (lvl, hitdie) in self.items():
            if class_ == self.first:
                lvl -= 1
                total += hitdie
            total += lvl * (1 + (hitdie // 2))
        return total
    
class Movement(dict):
    def __init__(self):
        super().__init__()
        self['walking'] = 0

    def parse_input(self, string):
        speed, mode = first_word(string)
        if mode:
            if mode in self.keys():
                self[mode] = max(int(speed), self[mode])
            else:
                self[mode] = int(speed)
        else:
            self['walking'] = max(int(speed), self['walking'])
    
    def tex_make_movement(self):
        walk_speed = self['walking']
        other_speeds = '\\[-1ex]'.join(
                (str(sped) + ' ' + mode for mode, sped in self.items() if mode != 'walking')
                )
        return f'\\headedtext{{\\Huge}}{{{walk_speed}}}{{{other_speeds}}}{{\\par}}'

class Maybe_Int():
    def __init__(self):
        self.content = None

    def parse_input(self, string):
        if is_int(string):
            self.contents = int (string)

def consume_line(lines):
    while lines:
        line = lines.pop(0).strip()
        if line.startswith('#'):
            continue
        if line:
            break
    else:
        return '', ''

    keyword, rest = first_word(line)
    extra = list()
    if keyword in multiline_keywords:
        while lines and (extra_line := lines.pop(0).strip()):
            extra.append(extra_line)

    out = unlines([rest] + extra)
    return keyword, out

def scanner(file_list):
    for filename in file_list:
        print(filename)
        f = open(filename, 'r')
        contents = f.readlines()
        f.close()
        while contents:
            keyword, args = consume_line(contents)
            exec_keyword(keyword, args)

def exec_keyword(keyword, args):
    if keyword in keywords.keys():
        keywords[keyword].parse_input(args)
    else:
        pass #TODO: add some kind of warning here.


######################
#                    #
# globals, lookup    #
#                    #
######################
Abilities = [Str, Dex, Con, Int, Wis, Cha] = \
            list(map(lambda _ : Ability(), range(6)))

Skills = (
    Acrobatics    , AnimalHandling, Arcana        , Athletics     , 
    Deception     , History       , Insight       , Intimidation  , 
    Investigation , Medicine      , Nature        , Perception    , 
    Perfomrance   , Persuasion    , Religion      , SleightOfHand , 
    Stealth       , Survival
        ) = (
    Skill(Dex)    , Skill(Wis)    , Skill(Int)    , Skill(Str)    ,
    Skill(Cha)    , Skill(Int)    , Skill(Wis)    , Skill(Cha)    ,
    Skill(Int)    , Skill(Wis)    , Skill(Int)    , Skill(Wis)    ,
    Skill(Cha)    , Skill(Cha)    , Skill(Int)    , Skill(Dex)    ,
    Skill(Dex)    , Skill(Wis)
    )

Initiative = Skill(Dex)
Class = Class_Level()
Speed = Movement()
AC = Armorclass()
HP = Maybe_Int()

Basic_Info = Name, Race, Background, Alignment, Player, Experience = \
        map(Named_String, (
            'Name', 'Race', 'Background', 'Alignment', 'Player', 'Experience'
            ))

Attuned, Armor, Weapon, Equip, Item, Feature = \
        map(Named_List_with_descriptions,
                ('Attuned Items', 'Armor', 'Weapons', 'Equipment',
                    'Other Items', 'Feats and Features')
                )

Action, Bonusaction, Reaction, Tool, Language = \
        map(Named_List_compact,
                ('Actions', 'Bonus Actions', 'Reactions', 'Tools', 'Languages')
                )

keywords = {
        k : v for k, v in globals().items() if type(v) in
        {Ability, Skill, Class_Level, Named_String, Movement, Armorclass,
            Named_List_with_descriptions, Named_List_compact, Maybe_Int
            }
        }

#multiline keywords are precisely the lists.
multiline_keywords = {
        k for k, v in keywords.items() if issubclass(type(v), Named_List)
        }

expandable = {
        (k + 'Mod') : v.get_modifier
        for k, v in keywords.items() if type(v) is Ability
        }
expandable['Level'] = Class.get_total_level

#############################
#                           #
# printing the tex document #
#                           #
#############################

def main():
    if len(sys.argv) <= 1:
        working_dir = input('Enter directory to operate on: ')
    else:
        working_dir = sys.argv[1]

    filelist = list(os.scandir(working_dir))
    filelist.sort(key = lambda f : f.name)
    scanner(filelist)

    print_to_tex()
    os.mkdir('.tmp')
    for _ in range(3):
        os.system('pdflatex -interaction nonstopmode -output-directory .tmp DnDtex_new.tex')
    os.rename('.tmp/DnDtex_new.pdf', './DnDtex_new.pdf')
    for f in os.scandir('.tmp'):
        os.remove(f)
    os.rmdir('.tmp')


if __name__ == '__main__':
    main()
