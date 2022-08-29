from parsetools import *

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

