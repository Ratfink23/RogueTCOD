import copy

from components import ai, fighter
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.item import Item

from render_functions import RenderOrder
from entity import Entity

from loader_functions.data_loaders import import_json
from game_messages import Message
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal
from randon_utils import from_dungeon_depth, random_choice_from_dict

fighter_base_dict = import_json('data/fighter_types.JSON')
item_base_dict = import_json('data/item_types.JSON')


def ai_factory(ai_name: dict):
    if ai_name == "MeleeMonster":
        return ai.MeleeMonster()
    if ai_name == "BreedingMonster":
        return ai.BreedingMonster()
    if ai_name == "CorpseMonster":
        return ai.CorpseMonster()
    if ai_name == "ArcherMonster":
        return ai.ArcherMonster()
    assert 0, "Bad AI" + ai_name


def equipable_factory(equipable_name: dict):
    if 'MAIN_HAND' == equipable_name['slot']: slot = EquipmentSlots.MAIN_HAND
    if 'OFF_HAND' == equipable_name['slot']: slot = EquipmentSlots.OFF_HAND
    equipable_name.pop('slot')

    return Equippable(slot, **equipable_name)


def use_factory(use_name: dict):
    kwargs = {}
    if 'heal' in use_name['function']:
        kwargs['use_function'] = heal
    if 'cast_lightning' in use_name['function']:
        kwargs['use_function'] = cast_lightning
    if 'cast_fireball' in use_name['function']:
        kwargs['use_function'] = cast_fireball
    if 'cast_confuse' in use_name['function']:
        kwargs['use_function'] = cast_confuse
    use_name.pop('function')

    if 'targeting_message' in use_name:
        kwargs['targeting_message'] = Message(use_name['targeting_message'], use_name['message_color'])
        use_name.pop('targeting_message')
        use_name.pop('message_color')

    if 'targeting' in use_name:
        kwargs['targeting'] = True
        use_name.pop('targeting')

    return Item(**kwargs, **use_name)


def spawn_fighter(x, y, dungeon_depth=1, fighter_type=None):
    """
    Returns a fighter Entity at x, y of monster_type if not None.
    Otherwise randomly assign a monster based on dungeon_depth
    :param x:
    :param y:
    :param dungeon_depth:
    :param fighter_type:
    :return:
    """

    fighter_chances = dict()

    for _f in fighter_base_dict:
        if fighter_base_dict[_f]['chance']:
            fighter_chances[_f] = from_dungeon_depth(fighter_base_dict[_f]['chance'], dungeon_depth)

    # If monster_type give ignore monster chances table
    if fighter_type:
        fighter_choice = fighter_type
    else:
        fighter_choice = random_choice_from_dict(fighter_chances)

    # Deepcopy the dict so it can be popped
    fighter_data = copy.deepcopy(fighter_base_dict[fighter_choice])

    mob_display_name = fighter_data['display_name']
    mob_char = fighter_data['char']
    mob_color = fighter_data['color']
    fighter_component = fighter.Fighter(hp=fighter_data['fighter']['hp'],
                                        defense=fighter_data['fighter']['defense'],
                                        power=fighter_data['fighter']['power'],
                                        xp=fighter_data['fighter']['xp'])
    ai_component = ai_factory(fighter_data['ai'])

    spawned_fighter = Entity(x, y, mob_char, mob_color, fighter_choice, display_name=mob_display_name, blocks=True,
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

    item_chances = dict()

    for _f in item_base_dict:
        if item_base_dict[_f]['chance']:
            item_chances[_f] = from_dungeon_depth(item_base_dict[_f]['chance'], dungeon_depth)

    if item_type:
        item_choice = item_type
    else:
        item_choice = random_choice_from_dict(item_chances)

    # Deepcopy the dict so it can be popped
    item_data = copy.deepcopy(item_base_dict[item_choice])

    item_displayname = item_data['display_name']
    item_char = item_data['char']
    item_color = item_data['color']

    if 'equipment' in item_data:
        equippable_component = equipable_factory(item_data['equipment'])
        item = Entity(x, y, item_char, item_color, item_choice, display_name=item_displayname,
                      equippable=equippable_component, render_order=RenderOrder.ITEM)
    elif 'use' in item_data:
        item_component = use_factory(item_data['use'])
        item = Entity(x, y, item_char, item_color, item_choice, display_name=item_displayname,
                      render_order=RenderOrder.ITEM, item=item_component)

    return item
