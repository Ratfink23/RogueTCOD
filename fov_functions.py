import tcod as libtcod

def initialize_fov(game_map):
    #todo change to be tcod.map
    fov_map = libtcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            #todo replace with map.Map.transparent and map.Map.walkable
            libtcod.map_set_properties(fov_map, x, y, not game_map.tiles[x][y].block_sight,
                                       not game_map.tiles[x][y].blocked)

    return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    #todo change to map.Map.compute_fov
    libtcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)