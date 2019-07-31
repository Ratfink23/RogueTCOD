import tcod as libtcod

from components import ai, fighter
from components.equipment import EquipmentSlots
from components.equippable import Equippable

from components.item import Item

from render_functions import RenderOrder
from entity import Entity

from game_messages import Message
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal
from randon_utils import from_dungeon_depth, random_choice_from_dict


def spawn_fighter(x,y, dungeon_depth=1, monster_type=None):
    """
    Returns a fighter Entity at x, y of monster_type if not None.
    Otherwise randomly assign a monster based on dungeon_depth
    :param x:
    :param y:
    :param dungeon_depth:
    :param monster:
    :return:
    """
    # TODO Pull attributes of monsters from a lookup
    monster_chances = {'orc': 80,
                       'troll': from_dungeon_depth([[15, 3], [30, 5], [60, 7]], dungeon_depth),
                       'ogre': from_dungeon_depth([[5,3], [10,5], [30, 7]], dungeon_depth)
                       }

    # If monster_type give ignore monster chances table
    if monster_type:
        monster_choice = monster_type
    else:
        monster_choice = random_choice_from_dict(monster_chances)

    if monster_choice == 'orc':
        fighter_component = fighter.Fighter(hp=20, defense=0, power=4, xp=35)
        ai_component = ai.BasicMonster()
        mob_char = 'o'
        mob_color = libtcod.light_green
        mob_name = 'Orc'
    elif monster_choice == 'troll':
        fighter_component = fighter.Fighter(hp=30, defense=2, power=8, xp=100)
        ai_component = ai.BasicMonster()
        mob_char = 'T'
        mob_color = libtcod.green
        mob_name = 'Troll'
    elif monster_choice == 'ogre':
        fighter_component = fighter.Fighter(hp=30, defense=5, power=10, xp=200)
        ai_component = ai.BasicMonster()
        mob_char = 'O'
        mob_color = libtcod.dark_red
        mob_name = 'Ogre'
    else:
        fighter_component = fighter.Fighter(hp=5, defense=0, power=2, xp=5)
        ai_component = ai.BreedingMonster()
        mob_char = 'w'
        mob_color = libtcod.white
        mob_name = 'Worm mass'

    spawned_fighter = Entity(x, y, mob_char, mob_color, mob_name, blocks=True,
                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

    return spawned_fighter


def spawn_item(x, y, dungeon_depth=1, item_type=None):
    """
        Returns a item Entity at x, y of item_type if not None.
        Otherwise randomly assign a item based on dungeon_depth
    :param x:
    :param y:
    :param dungeon_depth:
    :param item_type:
    :return:
    """

    item_chances = {'healing_potion': 35,
                    'sword': from_dungeon_depth([[5, 4]], dungeon_depth),
                    'shield': from_dungeon_depth([[15, 8]], dungeon_depth),
                    'lighting_scroll': from_dungeon_depth([[25, 4]], dungeon_depth),
                    'fireball_scroll': from_dungeon_depth([[25, 6]], dungeon_depth),
                    'confusion_scroll': from_dungeon_depth([[10, 2]], dungeon_depth)
                    }
    if item_type:
        item_choice = item_type
    else:
        item_choice = random_choice_from_dict(item_chances)

    if item_choice == 'healing_potion':
        item_component = Item(use_function=heal, amount=40)
        item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                      item=item_component, stackable=1)
    elif item_choice == 'sword':
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
        item = Entity(x, y, '/', libtcod.sky, 'Short Sword', equippable=equippable_component)
    elif item_choice == 'shield':
        equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
        item = Entity(x, y, '[', libtcod.dark_orange, 'Wood Shield', equippable=equippable_component)
    elif item_choice == 'fireball_scroll':
        item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
            'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                              damage=25, radius=3)
        item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                      item=item_component)
    elif item_choice == 'confusion_scroll':
        item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
            'Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan))
        item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,
                      item=item_component)
    elif item_choice == 'lighting_scroll':
        item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
        item = Entity(x, y, '#', libtcod.yellow, 'Lighting Scroll', render_order=RenderOrder.ITEM,
                      item=item_component)
    else:
        equipment_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
        item = Entity(x, y, '-', libtcod.sky, 'Dagger', equippable=equipment_component)

    return item
