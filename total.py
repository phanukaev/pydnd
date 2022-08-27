from enum import Enum
from dataclasses import dataclass
import os
import sys

###############
#             #
# proficiency #
#             #
###############
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

###########
#         #
# vantage #
#         #
###########
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
        
#######################
#                     #
# ability / abilities #
#                     #
#######################
class Ability:
    def __init__(self):
        self.base_score = None

        # changes to the ability score
        self.numerical_modifier = 0
        self.override = 0

        # ability check
        self.check_vantage = Vantage.NOTHING
        self.check_proficiency = Proficiency.NONE
        self.check_numerical_modifier = 0

        # saving throws
        self.save_vantage = Vantage.NOTHING
        self.save_proficiency = Proficiency.NONE
        self.save_numerical_modifier = 0

    # computing end results
    # The get_* methods should only do "return x",
    # but these computations are simple enough,
    # and also tracking and updating what needs to be re-computed
    # and when is almost certainly more effort.
    # ... at least for now
    def get_score(self):
        if self.base_score is None:
            raise ValueError ("You forgot to add an ability score")
        score = max(self.base_score + self.numerical_modifier, self.override)
        return score
    
    def get_modifier(self):
        modifier = (self.get_score() - 10) // 2
        return modifier

    def get_check_modifier(self):
        return self.get_modifier() \
               + self.check_numerical_modifier \
               + added_proficiency_bonus(self.check_proficiency)

    def get_save_modifier(self):
        return self.get_modifier() \
               + self.save_numerical_modifier \
               + added_proficiency_bonus(self.save_proficiency)

    # modifying internals
    # base numbers
    def add_numerical_modifier(self, new_modifier):
        self.numerical_modifier += new_modifier
        return

    def add_override(self, new_override):
        if self.base_score is None:
            self.base_score = new_override
        else:
            self.override = max(self.override, new_override)

    # ability checks
    def add_check_vantage(self, new_vantage):
        self.check_vantage += new_vantage

    def add_check_proficiency(self, new_proficiency):
        self.check_proficiency = max(self.check_proficiency, new_proficiency)

    def add_check_numerical_modifier(self, modifier):
        self.check_numerical_modifier += modifier

    # saving throws (also copy pasta)
    def add_save_vantage(self, new_vantage):
        self.save_vantage += new_vantage

    def add_save_proficiency(self, new_proficiency):
        self.save_proficiency = max(self.save_proficiency, new_proficiency)

    def add_save_numerical_modifier(self, modifier):
        self.save_numerical_modifier += modifier

    def parse_input(self, string):
        if is_mod_literal(string):
            self.add_numerical_modifier(int(string))
            return

        if is_int(string):
            self.add_override(int(string))
            return

        keyword, argument = first_word(string)
        
        if keyword == 'checks':
            if is_mod_literal(argument):
                self.add_check_numerical_modifier(int(argument))
            else:
                if is_vantage(argument):
                    self.add_check_vantage(vantage(argument))
                if is_proficiency(argument):
                    self.add_check_proficiency(proficiency(argument))

        elif keyword == 'saves':
            if is_mod_literal(argument):
                self.add_save_numerical_modifier(int(argument))
            else:
                if is_vantage(argument):
                    self.add_save_vantage(vantage(argument))
                if is_proficiency(argument):
                    self.add_save_proficiency(proficiency(argument))
        else:
            pass
            # TODO: add logging of unrecognized lines ?

    def tex_make_mod_bullet(self):
        fill_color = self.check_proficiency.color()
        text_color = 'white' if fill_color == 'black' else 'black'

        contents   = str(self.get_check_modifier())
        return f'\\modbullet{{{fill_color}}}{{{text_color}}}' + '{' + contents + '}'
        # {{ }} produces a literal pair of braces when used in an fstring.

    def tex_make_save_bullet(self):
        fill_color = self.save_proficiency.color()
        draw_color = self.save_vantage.color()
        return f'\\xbullet{{{draw_color}}}{{{fill_color}}}'


##########
#        #
# skills #
#        #
##########
class Skill:
    def __init__(self, base_ability):
        self.ability = base_ability

        self.vantage = Vantage.NOTHING
        self.proficiency = Proficiency.NONE
        self.numerical_modifier = 0

    def add_vantage(self, new_vantage):
        self.vantage += new_vantage

    def add_proficiency(self, new_proficiency):
        self.proficiency = max(self.proficiency, new_proficiency)

    def add_numerical_modifier(self, new_modifier):
        self.numerical_modifier += new_modifier

    # as with the ability class, the get_* methods do actual computation (for now).
    def get_vantage(self):
        return self.vantage + self.ability.check_vantage

    def get_proficiency(self):
        return max(self.proficiency, self.ability.check_proficiency)

    def get_modifier(self):
        return self.ability.get_modifier() \
               + self.ability.check_numerical_modifier \
               + self.numerical_modifier \
               + added_proficiency_bonus(self.get_proficiency())

    def parse_input(self, string):
        if is_mod_literal(string):
            self.add_numerical_modifier(int(string))
        else:
            if is_vantage(string):
                self.add_vantage(vantage(string))
            elif is_proficiency(string):
                self.add_proficiency(proficiency(string))

    def passive_check(self):
        check = 10 + self.get_modifier()
        if (v := self.get_vantage()) is Vantage.ADVANTAGE:
            check += 5
        elif v is Vantage.DISADVANTAGE:
            check -= 5
        return check

    def tex_make_bullet(self):
        fill_color = self.proficiency.color()
        draw_color = self.vantage.color()
        return f'\\xbullet{{{draw_color}}}{{{fill_color}}}'
        

##############
#            #
# armorclass #
#            #
##############
class Armorclass:
    def __init__(self):
        self.formulae = list()
        self.formulae.append('10 + DexMod')
        self.numerical_modifier = 0

    def add_numerical_modifier(self, new_modifier):
        self.numerical_modifier += new_modifier

    def add_formula(self, new_formula):
        self.formulae.append(new_formula)

    def get_armorclass(self):
        base_ac = max(map(eval_expr, self.formulae))
        return base_ac + self.numerical_modifier

    def parse_input(self, string):
        if is_mod_literal(string):
            self.add_numerical_modifier(int(string))
        elif is_expr(string):
            self.formulae.append(string)

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
    def __init__(self, name, datatype, iterable = ()):
        self.name = name
        self.type = datatype
        super().__init__(iterable)

    def append(self, item):
        if type(item) is not self.type:
            raise TypeError ("tried appending something of wrong type")
        else:
            super().append(item)

class Named_List_compact(Named_List):
    def __init__(self, name, iterable = ()):
        super().__init__(name, Thing, iterable)

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
        super().__init__(name, Thing_With_Description, iterable)

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
        known_hitdice = {
                'Barbarian' : 12,
                'Fighter'   : 10,
                'Paladin'   : 10,
                'Ranger'    : 10,
                'Warlock'   : 10,
                'Sorcerer'  :  6,
                'Wizard'    :  6
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



#################################
#                               #
# string operations and parsing #
#                               #
#################################
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def is_mod_literal(string):
    string = delete_whitespace(string)
    return string.startswith(('+', '-')) and is_int(string)

def words(string):
    return string.split()

def unwords(lst):
    return ' '.join(lst)

def lines(string):
    return string.split('\n')

def unlines(lst):
    stripped = map(lambda x : x.strip(), lst)
    return '\n'.join(stripped)

def first_word(string):
    first_and_rest = string.split(maxsplit = 1)
    if len(first_and_rest) == 1:
        first, rest = string, ''
    else:
        first, rest = first_and_rest
    return first, rest

def last_word(string):
    body, tail = string.rsplit(maxsplit = 1)
    return body, tail

def first_line(string):
    first_and_rest = string.split('\n', maxsplit = 1)
    if len(first_and_rest) == 1:
        first, rest = string, ''
    else:
        first, rest = first_and_rest
    return first, rest

def delete_whitespace(string):
    return ''.join(words(string))

def is_vantage(string):
    return string.upper() in Vantage.__members__.keys()

def vantage(string):
    return Vantage[string.upper()]

def is_proficiency(string):
    return string.upper() in Proficiency.__members__.keys()

def proficiency(string):
    return Proficiency[string.upper()]

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


###############################
#                             #
# Processing and parsing math #
#                             #
###############################
def is_math(string):
    # this function is bad
    allowed_chars = {str(i) for i in range(10)} | {'+','-','*','/','(',')'}
    chars = set(delete_whitespace(string))

    return chars.issubset(allowed_chars) 

def expand(string):
    for k, f in expandable.items():
        if string.find(k) != -1:
            string = string.replace(k, str(f()))

    return string

def is_expr(string):
    return is_math(expand(string))

def eval_expr(string):
    if is_expr(string):
        return(eval(expand(string)))
    else:
        return string

def proc_all_math(string):
    while (openbrack := string.find('[')) != -1:
        if openbrack < (closebrack := string.find(']')) != -1:
            mathblock = string[openbrack+1:closebrack]
            mathblock = str(eval_expr(mathblock))
            string = string[:openbrack] + mathblock + string[closebrack + 1:]
        else:
            break
    return string


######################
#                    #
# globals, lookup    #
#                    #
######################
Abilities = [Str, Dex, Con, Int, Wis, Cha] = \
            list(map(lambda _ : Ability(), range(6)))

Skills    = [
            Acrobatics    , AnimalHandling, Arcana        , Athletics     , 
            Deception     , History       , Insight       , Intimidation  , 
            Investigation , Medicine      , Nature        , Perception    , 
            Perfomrance   , Persuasion    , Religion      , SleightOfHand , 
            Stealth       , Survival
        ] = [
            Skill(Dex), Skill(Wis), Skill(Int), Skill(Str),
            Skill(Cha), Skill(Int), Skill(Wis), Skill(Cha),
            Skill(Int), Skill(Wis), Skill(Int), Skill(Wis),
            Skill(Cha), Skill(Cha), Skill(Int), Skill(Dex),
            Skill(Dex), Skill(Wis)
        ]

Initiative = Skill(Dex)
Class = Class_Level()
Speed = Movement()
AC = Armorclass()
HP = Maybe_Int()

Basic_Info = [Name, Race, Background, Alignment, Player, Experience] = \
        list(map(Named_String, (
            'Name', 'Race', 'Background', 'Alignment', 'Player', 'Experience'
            )
            ))

Attuned, Armor, Weapon, Equip, Item, Feature = \
        map(Named_List_with_descriptions,
            ('Attuned Items', 'Armor', 'Weapons', 'Equipment',
                'Other Items', 'Feats and Features')
            )

Action, Bonus, Reaction, Tool, Language = \
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
def make_new_command(command_name, contents):
    out = '\\newcommand{\\' + command_name + '}{' + contents + '}\n'
    return out

def tex_write_modifier(num):
    negative = (num < 0)
    if negative:
        num *= -1
    prefix = '\\minus' if negative else '\\plus'
    return prefix + str(num)

def make_multi_command(command_name, iterator):
    contents = '\n,'.join(iterator)
    return make_new_command(command_name, contents)

def print_to_tex():
    for class_, (lv, _) in Class.items():
        expandable[class_ + 'Lv'] = lambda : lv

    with open('./variables.tex', 'w') as outfile:
        # Character name and top right block except classes
        for info in Basic_Info:
            outfile.write(make_new_command(info.name, info.contents))

        # Classes
        outfile.write(make_new_command('ClassLevel',
            '/'.join(class_ + ' ' + str(lvl) for class_, (lvl, _) in Class.items())
            ))
        
        # ability modifiers
        outfile.write(make_multi_command('abilitymods',
                (tex_write_modifier(ability.get_modifier())
                    for ability in Abilities)))

        # ability scores
        outfile.write(make_multi_command('abilities',
                (str(ability.get_score()) for ability in Abilities
                )))

        # ability check modifiers
        outfile.write(make_multi_command('abilityCheckMods',
                (ability.tex_make_mod_bullet() for ability in Abilities
                )))

        # passive perception
        outfile.write(make_new_command('PassPerc',
            str(Perception.passive_check()
                )))

        # saving throw bullets
        outfile.write(make_multi_command('savebullets',
                (ability.tex_make_save_bullet() for ability in Abilities
                )))

        # saving throw modifiers
        outfile.write(make_multi_command('savemods',
            (tex_write_modifier(ability.get_save_modifier())
                for ability in Abilities)))

        # skill check bullets
        outfile.write(make_multi_command('skillbullets',
                (skill.tex_make_bullet() for skill in Skills)))

        # skill check modifiers
        outfile.write(make_multi_command('skillmods',
                (tex_write_modifier(skill.get_modifier())
                    for skill in Skills)))

        # proficiency bonus
        outfile.write(make_new_command('profBonus',
            tex_write_modifier(proficiency_bonus())))

        # armor class
        outfile.write(make_new_command('armorClass',
            str(AC.get_armorclass())))

        # initiative
        outfile.write(make_new_command('Initiative',
            tex_write_modifier(Initiative.get_modifier())))

        # movement
        outfile.write(make_new_command('movement',
            Speed.tex_make_movement()))

        # hitpoints
        outfile.write(make_new_command('hitPoints',
            str(HP.content if HP.content is not None else Class.get_auto_hitpoints())))

        # equipment
        outfile.write(make_new_command('Equipment',
            '\\spacer'.join(
                (lst.compact().tex_print() for lst in (Attuned, Armor, Weapon, Equip) if lst
                    ))))
        
        # features and traits
        outfile.write(make_new_command('Features',
            Feature.tex_print(show_name = False)))
        
        # other proficiencies
        outfile.write(make_new_command('Proficiencies',
            '\\spacer'.join(
                (lst.tex_print() for lst in (Tool, Language) if lst
                    ))))

        # actions / reactions / bonus actions
        outfile.write(make_new_command('Actions',
            '\\spacer'.join(
                (lst.tex_print() for lst in (Action, Bonus, Reaction) if lst
                    ))))

        # equipment dump on next page
        outfile.write(make_new_command('EquipDump',
            '\\section*{Inventory}' +
            '\n'.join(
                (lst.tex_print(show_name = True) for lst in
                    (Attuned, Armor, Weapon, Equip, Item)
                    ))))


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
