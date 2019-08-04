import tcod as libtcod

from random import randint
from game_messages import Message
from spawner import spawn_fighter

# TODO redo Breeding AI to add breeding

class BasicMonster:
    """
    Basic Melee attack AI that follow the target if within the player FOV.
    If sight if lost it will chase for three moves.
    """
    follow_turns = 0
    target_seen = False

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack_melee(target)
                results.extend(attack_results)
            # Target has been seen and can be followed
            self.target_seen = True

        elif self.target_seen:
            monster.move_astar(target, entities, game_map)
            self.follow_turns = self.follow_turns + 1

        # Target hasn't been seen for three turns.
        if self.follow_turns == 3:
            self.follow_turns = 0
            self.target_seen = False

        return results


class ArcherMonster:
    # TODO need at add maximum range as input
    # TODO move away is very basic as the mob directly away from player.
    #       needs to change at flee with weighted directions
    """
    Basic Archery attack AI that follow the target if within the player FOV.
    If sight if lost it will chase for three moves.
    """
    follow_turns = 0
    target_seen = False
    max_range = 5

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= self.max_range:
                monster.move_astar(target, entities, game_map)
            elif monster.distance_to(target) <= 1:
                print(target.x, target.y)
                monster.move_away(target.x, target.y, game_map, entities)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack_range(target)
                results.extend(attack_results)
            # Target has been seen and can be followed
            self.target_seen = True

        elif self.target_seen:
            monster.move_astar(target, entities, game_map)
            self.follow_turns = self.follow_turns + 1

        # Target hasn't been seen for three turns.
        if self.follow_turns == 3:
            self.follow_turns = 0
            self.target_seen = False

        return results


class BreedingMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


class CorpseMonster:
    # TODO investigate if this should be done with enumarate
    corpse_labels = ['corpse', 'skeleton', 'bones', 'skull']
    decay_monster = ['worm mass', 'zombie', 'skeleton', 'floating skull']

    def __init__(self, decay=0):
        self.decay_amount = decay

    def take_turn(self, target, fov_map, game, entities):
        results = []
        # decay corpse if outside of FOV
        if not libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
            if randint(50, 200) < self.decay_amount:
                results = self.decay(entities)
                self.decay_amount = 0
            else:
                self.decay_amount += 1
        return results

    def decay(self, entities):
        results = []
        index = self.corpse_labels.index(self.owner.state_name)
        # Check for monster spawn, if no spawn increase state
        if randint(1, 10) >= 8:
            monster = spawn_fighter(self.owner.x, self.owner.y, fighter_type=self.decay_monster[index])
            entities.append(monster)
            results.append({'message': Message('Something decays in the distance', 'map_effect')})
            entities.remove(self.owner)
        elif index + 1 < len(self.corpse_labels):
            self.owner.state_name = self.corpse_labels[index + 1]
        else:
            entities.remove(self.owner)
        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), 'major_event')})

        return results
