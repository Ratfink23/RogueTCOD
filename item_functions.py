import tcod as libtcod

from components import ai
from game_messages import Message
from render_functions import RenderOrder

# TODO change function names

def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', 'minor_error')})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', 'effect_bonus')})

    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closet_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closet_distance:
                target = entity
                closet_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message(
            'A lighting bolt strikes the {0} with loud thunder! The damage is {1}'.format(target.name, damage),
            'effect_damage')})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append(
            {'consumed': False, 'target': None, 'message':
                Message('No enemy is close enough to strike.', 'minor_error')})

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', 'minor_error')})
        return results

    results.append({'consumed': True,
                    'message': Message('The fireball explodes, burning everything with {0} tiles'.format(radius),
                                       'minor_effect')})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage),
                                               'effect_damage')})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', 'minor_error')})
        return results

    for entity in entities:
        # Entity at location x,y with an ai and isn't a corpse
        if entity.x == target_x and entity.y == target_y and entity.ai and entity.render_order != RenderOrder.CORPSE:
            confused_ai = ai.ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True,
                            'message': Message('{0} looks confused, as they starts to stumble around!'
                                               .format(entity.full_name), 'minor_effect')})

            break
    else:
        results.append(
            {'consumed': False, 'message': Message('There is no enemy at that location.', 'minor_error')})

    return results
