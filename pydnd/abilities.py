from proficiency import Proficiency
from vantage import Vantage
from parsetools import *

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

    #-- computing end results --#
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

    #-- modifying internals --#
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

    # saving throws
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


