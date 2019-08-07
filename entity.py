import tcod as libtcod
import math
import random

from components.item import Item
from render_functions import RenderOrder


class Entity:
    # A generic object to represent players, enemies, items etc.
    def __init__(self, x, y, char, color, name, display_name=None, blocks=False, render_order=RenderOrder.CORPSE,
                 fighter=None, ai=None, item=None, inventory=None, stairs=None, level=None, equipment=None,
                 equippable=None, state_prefix=None, state_suffix=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.display_name = display_name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable
        self.state_prefix = state_prefix
        self.state_suffix = state_suffix

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

        if self.equipment:
            self.equipment.owner = self

        if self.equippable:
            self.equippable.owner = self
            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    @property
    def full_name(self):
        # Returns the full name of an entity
        if not self.state_suffix and not self.state_prefix:
            fullname = self.display_name
        elif self.state_suffix and self.state_prefix:
            fullname = self.state_prefix + ' ' + self.display_name + ' ' + self.state_suffix
        elif self.state_suffix:
            fullname = self.display_name + ' ' + self.state_suffix
        else:
            fullname = self.state_prefix + ' ' + self.display_name
        if self.fighter:
            fullname = fullname + ' (' + self.fighter.health_display + ')'

        return fullname

    def move(self, dx, dy):
        # Move entity one step in direction dx, dy
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, entities, game_map):
        """
        Move self one step towards target with a blocking check
        :param target_x: target pos x
        :param target_y: target pos y
        :param entities: entity list
        :param game_map: game map
        :return:
        """
        # Move entity one step in direction of target with block check
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_away(self, target_x, target_y, entities, game_map):
        """
        Move self one step away direction (best to worst) of target with blocking check
        :param target_x: target pos x
        :param target_y: target pos y
        :param entities: entity list
        :param game_map: game map
        :return:
        """
        # Best path for keyed for target direction (target_dx, target_dy)
        best_path = {}
        best_path[(0, -1)] = [(0, 1), (-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]
        best_path[(0, 1)] = [(0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        best_path[(-1, 0)] = [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, -1)]
        best_path[(1, 0)] = [(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 1), (1, -1)]
        best_path[(1, -1)] = [(-1, 1), (0, 1), (-1, 0), (-1, -1), (1, 1), (0, -1), (1, 0)]
        best_path[(1, 1)] = [(-1, -1), (0, 1), (1, 0), (-1, 1), (1, -1), (0, 1), (1, 0)]
        best_path[(-1, 1)] = [(1, -1), (1, 0), (0, -1), (-1, -1), (1, 1), (-1, 0), (0, 1)]
        best_path[(-1, -1)] = [(1, 1), (1, 0), (0, 1), (-1, 1), (1, -1), (-1, 0), (0, -1)]

        target_dx = target_x - self.x
        target_dy = target_y - self.y
        distance = math.sqrt(target_dx ** 2 + target_dy ** 2)

        target_dx = int(round(target_dx / distance))
        target_dy = int(round(target_dy / distance))
        direction = (target_dx,target_dy)

        flee_path = best_path.get(direction)

        for dx, dy in flee_path:
            if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
                self.move(dx, dy)
                break

    def flee(self, target_x, target_y, entities, game_map):
        """
        Move self one step randomly away of target with blocking check
        :param target_x: target pos x
        :param target_y: target pos y
        :param entities: entity list
        :param game_map: game map
        :return:
        """
        # Move entity one step randomly away  of target with block check
        directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]

        # find target direction
        target_dx = target_x - self.x
        target_dy = target_y - self.y
        distance = math.sqrt(target_dx ** 2 + target_dy ** 2)

        target_dx = int(round(target_dx / distance))
        target_dy = int(round(target_dy / distance))

        # remove standing still and target direction
        directions.remove((0, 0))
        directions.remove((target_dx, target_dy))

        # remove the direction towards the target
        if target_dx <= 0: directions.remove((1, target_dy))
        if target_dx >= 0: directions.remove((-1, target_dy))
        if target_dy <= 0: directions.remove((target_dx, 1))
        if target_dy >= 0: directions.remove((target_dx, -1))

        # Panic!
        random.shuffle(directions)

        for dx, dy in directions:
            if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
                self.move(dx, dy)
                break

    def move_astar(self, target, entities, game_map):
        # Astar movement code directly from Roguelike Tutorial (now with tcod)
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map.Map(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                if not game_map.tiles[x1][y1].block_sight:
                    fov.transparent[y1][x1] = True
                if not game_map.tiles[x1][y1].blocked:
                    fov.walkable[y1][x1] = True

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                fov.walkable[entity.y][entity.x] = False

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        astar_path_map = libtcod.path.AStar(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        my_path = astar_path_map.get_path(self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if my_path and len(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = my_path[0]
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, entities, game_map)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None
