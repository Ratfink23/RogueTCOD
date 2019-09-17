import tcod as libtcod

from random import randint
from game_messages import Message
from spawner import spawn_fighter


class MeleeMonster:
    """
    Basic Melee attack AI that follow the target if within the player FOV and try to get close enough to attack
    If wounded they will attempt to flee and heal when outside of sight of the player
    If sight if lost it will chase for three moves.
    """
    follow_counter = 0
    target_seen = False
    fleeing = False

    def __init__(self, follow_length=3, flee_level=3, heal_rate=1):
        self.follow_length = follow_length
        self.flee_level = flee_level
        self.heal_rate = heal_rate

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        #todo replace 'map_is_in_fov' with map.Map.fov
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            # Should I run away and panic?
            if int(monster.fighter.hp / monster.fighter.max_hp * 10) <= self.flee_level:
                if monster.state_prefix == 'Fleeing':
                    monster.flee(target.x, target.y, entities, game_map)
                else:
                    monster.state_prefix = 'Fleeing'
                    monster.flee(target.x, target.y, entities, game_map)
                    results.append({'message': Message('{0} panics'.format(monster.display_name), 'combat_event')})
            # Too far to hit with Melee attack, move closer
            elif monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            # Take a swing
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack_melee(target)
                results.extend(attack_results)
            # Target has been seen and can be followed
            self.target_seen = True

        elif self.target_seen:
            self.follow_counter += self.follow_counter
            if monster.state_prefix == 'Fleeing':
                monster.fighter.heal(int(monster.fighter.max_hp*0.1*self.heal_rate))
                if int(monster.fighter.hp / monster.fighter.max_hp * 10) > self.flee_level:
                    monster.state_prefix = None
                    results.append({'message': Message('...a creatures recovers...', 'map_unseen')})
            else:
                monster.move_astar(target, entities, game_map)
        # Target hasn't been seen for three turns.
        if self.follow_counter == self.follow_length:
            self.follow_counter = 0
            self.target_seen = False

        return results


class ArcherMonster:
    # TODO need at add maximum range as input?
    """
    Basic Archery attack AI that follow the target if within the player FOV.
    If sight if lost it will chase for three moves.
    """
    follow_turns = 0
    target_seen = False
    max_range = 4

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        #todo replace 'map_is_in_fov' with map.Map.fov
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= self.max_range:
                monster.move_astar(target, entities, game_map)
            # Change monster.distance_to(target) to 1.5 too make them harder to attack (on corners only)
            elif monster.distance_to(target) <= 1:
                monster.move_away(target.x, target.y, entities, game_map)
            elif target.fighter.hp > 0:
                # TODO check blocks between target to see if blocked by another entity
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


#todo add breeding to breeding AI
class BreedingMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        #todo replace 'map_is_in_fov' with map.Map.fov
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack_melee(target)
                results.extend(attack_results)

        return results


class CorpseMonster:
    # TODO investigate if the lists can be another way
    corpse_labels = ['corpse', 'skeleton', 'bones', 'skull']
    decay_monster = ['worm mass', 'zombie', 'skeleton', 'floating skull']

    def __init__(self, decay=0):
        self.decay_amount = decay

    def take_turn(self, target, fov_map, game, entities):
        results = []
        # decay corpse if outside of FOV
        #todo replace 'map_is_in_fov' with map.Map.fov
        if not libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
            if randint(50, 200) < self.decay_amount:
                results = self.decay(entities)
                self.decay_amount = 0
            else:
                self.decay_amount += 1
        return results

    def decay(self, entities):
        results = []
        index = self.corpse_labels.index(self.owner.state_suffix)
        # Check for monster spawn, if no spawn increase state
        if randint(1, 10) >= 8:
            monster = spawn_fighter(self.owner.x, self.owner.y, fighter_type=self.decay_monster[index])
            entities.append(monster)
            results.append({'message': Message('...something decays...', 'map_unseen')})
            entities.remove(self.owner)
        elif index + 1 < len(self.corpse_labels):
            self.owner.state_suffix = self.corpse_labels[index + 1]
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
            self.owner.state_prefix = 'Confused'
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, entities, game_map)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            self.owner.state_prefix = None
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), 'major_event')})

        return results
