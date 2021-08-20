from vantage import *
from proficiency import Proficiency

class Ability:
    def __init__(self, name, base_score):
        self.name = name
        self.base_score = base_score

        # numerical modifiers to the ability score
        self.numerical_modifiers = list()
        self.override = 0

        # ability check
        self.check_vantage = Vantage.NOTHING
        self.check_proficiency = Proficiency.NONE
        self.check_numerical_modifiers = list()

        # saving throws
        self.save_vantage = Vantage.NOTHING
        self.save_proficiency = Proficiency.NONE
        self.save_numerical_modifiers = list()

    def compute_score(self):
        score = max(self.base_score + sum(self.numerical_modifiers), self.override)
        return score

    def add_numerical_modifier(self, new_modifier):
        self.numerical_modifiers.append(new_modifier)
        return

    


ability_names = [
                    'Strength',
                    'Dexterity',
                    'Constitution',
                    'Intelligence',
                    'Wisdom',
                    'Charisma',
                ]
