import tcod as libtcod

from random import randint
from game_messages import Message
from entity import spawn_fighter


class BasicMonster:
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
    corpse_labels = ['corpse', 'skeleton', 'bones', 'skull']

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
        if index + 1 < len(self.corpse_labels):
            self.owner.state_name = self.corpse_labels[index + 1]
        else:
            if randint(1, 10) >= 1:
                # TODO Change test value back to normal
                monster = spawn_fighter(self.owner.x, self.owner.y, 'worm mass')
                entities.append(monster)
                results.append({'message': Message('Something decays in the distance', libtcod.grey)})
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
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), libtcod.red)})

        return results
