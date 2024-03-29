import tcod as libtcod

from render_functions import RenderOrder
from game_messages import Message
from game_states import GameStates
from components import ai


def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died!', 'major_death'), GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), 'minor_death')
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    dead_ai = ai.CorpseMonster()
    dead_ai.owner = monster
    monster.ai = dead_ai
    monster.state_prefix = None
    monster.state_suffix = "corpse"
    monster.render_order = RenderOrder.CORPSE

    return death_message