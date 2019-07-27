import tcod as libtcod

from components import ai, fighter
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.item import Item

from render_functions import RenderOrder
from entity import Entity

from game_messages import Message
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal


def spawn_fighter(x,y, monster_type='orc'):
    """ Spawn a fighter Entity at x, y of the class monster_type"""
    # TODO Pull attributes of monsters from a lookup
    if monster_type == 'orc':
        fighter_component = fighter.Fighter(hp=20, defense=0, power=4, xp=35)
        ai_component = ai.BasicMonster()
        mob_char = 'o'
        mob_color = libtcod.desaturated_green
        mob_name = 'Orc'
    elif monster_type == 'troll':
        fighter_component = fighter.Fighter(hp=30, defense=2, power=8, xp=100)
        ai_component = ai.BasicMonster()
        mob_char = 'T'
        mob_color = libtcod.darker_green
        mob_name = 'Troll'
    else:
        fighter_component = fighter.Fighter(hp=5, defense=0, power=2, xp=5)
        ai_component = ai.BreedingMonster()
        mob_char = 'w'
        mob_color = libtcod.white
        mob_name = 'Worm mass'

    monster = Entity(x, y, mob_char, mob_color, mob_name, blocks=True,
                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

    return monster


def spawn_item(x, y, item_type):
    """ Returns a item Entity with pos x, y of the class item_type"""
    if item_type == 'healing_potion':
        item_component = Item(use_function=heal, amount=40)
        item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                      item=item_component)
    elif item_type == 'sword':
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
        item = Entity(x, y, '/', libtcod.sky, 'Sword', equippable=equippable_component)
    elif item_type == 'shield':
        equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
        item = Entity(x, y, '[', libtcod.dark_orange, 'Shield', equippable=equippable_component)
    elif item_type == 'fireball_scroll':
        item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
            'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                              damage=25, radius=3)
        item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                      item=item_component)
    elif item_type == 'confusion_scroll':
        item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
            'Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan))
        item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,
                      item=item_component)
    else:
        item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
        item = Entity(x, y, '#', libtcod.yellow, 'Lighting Scroll', render_order=RenderOrder.ITEM,
                      item=item_component)

    return item