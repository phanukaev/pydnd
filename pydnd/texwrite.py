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
                (lst.tex_print() for lst in (Action, Bonusaction, Reaction) if lst
                    ))))

        # equipment dump on next page
        outfile.write(make_new_command('EquipDump',
            '\\section*{Inventory}' +
            '\n'.join(
                (lst.tex_print(show_name = True) for lst in
                    (Attuned, Armor, Weapon, Equip, Item)
                    ))))

