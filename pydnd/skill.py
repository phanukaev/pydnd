from vantage import *
from proficiency import *

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
        

