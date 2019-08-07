import tcod as libtcod
from game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power, xp=0):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def health_display(self):
        health_index = ["Dying", "Near Death", "Near Death", "Bleeding", "Bleeding", "Bleeding",
                        "Wounded", "Wounded", "Wounded", "Healthy", "Healthy", "Healthy", "Healthy"]
        health_name = health_index[int(self.hp / self.max_hp * 10)]

        return health_name

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus

    def take_damage(self, amount):
        results= []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack_melee(self, target):
        # TODO different types of melee attacks?
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage)), 'combat_damage')})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name), 'combat_event')})

        return results

    def attack_range(self, target):
        # TODO different types of melee attacks?
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({'message': Message('{0} fires at {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage)), 'combat_damage')})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message('{0} fires at {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name), 'combat_event')})

        return results
