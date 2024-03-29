import tcod as libtcod

from enum import Enum

from game_states import GameStates
from menus import character_screen, inventory_menu, level_up_menu


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4


def render_mouse(mouse_window, mouse, screen_width, screen_height, fov_map):
    """
    Create a 'X'in mouse_window under mouse while in FOV

    :param mouse_window:
    :param mouse:
    :param screen_width:
    :param screen_height:
    :param fov_map:
    :return:
    """
    #todo change map_is_in_fov
    if libtcod.map_is_in_fov(fov_map, mouse.cx, mouse.cy):
        #todo update all console to new tcod console commands
        libtcod.console_set_char_foreground(mouse_window, mouse.cx, mouse.cy, libtcod.yellow)
        libtcod.console_set_char(mouse_window, mouse.cx, mouse.cy, 'X')
        libtcod.console_blit(mouse_window, 0, 0, screen_width, screen_height, 0, 0, 0, 1, 0)
        libtcod.console.Console.clear(mouse_window)


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors, game_state):

    if fov_recompute:
        # Draw all the tiles
        for y in range(game_map.height):
            for x in range(game_map.width):
                #todo change map_is_in_fov
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        #todo change the console char setting
                        libtcod.console_set_char_foreground(con, x, y, colors.get('light_ground'))
                        libtcod.console_set_char(con, x, y, '=')
                        libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                    else:
                        #todo change the console char setting
                        libtcod.console_set_char_foreground(con, x, y, colors.get('light_wall'))
                        libtcod.console_set_char(con, x, y, '.')
                        libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        #todo change the console char setting
                        libtcod.console_set_char_foreground(con, x, y, colors.get('dark_ground'))
                        libtcod.console_set_char(con, x, y, '=')
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                    else:
                        #todo change the console char setting
                        libtcod.console_set_char_foreground(con, x, y, colors.get('dark_wall'))
                        libtcod.console_set_char(con, x, y, '.')
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)

    #todo update to new tcod commands
    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        #todo change the console char setting
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    # HP Bar
    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
    #todo change the console char setting
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon Depth: {0}'.format(game_map.dungeon_depth))

    # print output from entities under mouse
    #todo change the console char setting
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    # Inventory call
    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Select from Menu or Esc to cancel.\n'
        else:
            inventory_title = 'Select from Menu or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level Up! Choose a stat to raise:', player, 40, screen_width, screen_width)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)
    #todo update map_is_in_fov
    names = [entity.full_name for entity in entities if entity.x == x and entity.y == y and
             libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    #todo update all the console to new tcod
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
    """
    Draw entity within the fov_map or entity is stairs and explored
    :param con: Console
    :param entity: Entity
    :param fov_map: FOV Map
    :param game_map: Game Map
    :return:
    """
    #todo update map_is_in_fov and console commands
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        libtcod.console_set_default_foreground(con, entity.color)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    #todo update the console command to tcod
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
