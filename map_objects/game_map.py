import tcod as libtcod
from random import randint

from components.staris import Stairs

from render_functions import RenderOrder
from entity import Entity
from spawner import spawn_item, spawn_fighter
from game_messages import Message
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from randon_utils import random_choice_from_dict, from_dungeon_depth


class GameMap:
    def __init__(self, width, height, dungeon_depth=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_depth = dungeon_depth

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # paint it to the map tile
                self.create_room(new_room)

                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # this is the first room - where tbe player starts
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first
                    # connect it to the precious room with a tunnel

                    # center of prev room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin
                    if randint(0, 1) == 1:
                        # first move hori then vert
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vert then hori
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities)

                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_depth + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, ">", libtcod.white, 'Stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    def create_room(self, room):
        # go through the tile in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities):

        # max mobs based on dungeon depth
        max_monsters_per_room = from_dungeon_depth([[2, 1], [3, 4], [5, 6]], self.dungeon_depth)
        max_items_per_room = from_dungeon_depth([[1, 1], [2, 4]], self.dungeon_depth)

        # get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            # choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            # if there is no monster already on the location spawm a monster
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster = spawn_fighter(x, y, self.dungeon_depth)
                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            # if there is no entity already on the location spawn an item
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item = spawn_item(x, y, self.dungeon_depth)
                entities.append(item)

    def next_floor(self, player, message_log, constants):
        self.dungeon_depth += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

        return entities

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
