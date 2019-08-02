import tcod as libtcod

from game_messages import Message
from spawner import spawn_item


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item_entity):
        results = []
        stacked = False

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': Message('You can not carry any more', libtcod.yellow)
            })
        else:
            results.append({
                'item_added': item_entity,
                'message': Message('You pick up the {0}!'.format(item_entity.name), libtcod.light_blue)
            })

            # TODO Review this code. I'm sure there is a better way
            # Check if can be stacked
            if not item_entity.item.stackable:
                self.items.append(item_entity)
            else:
                # check for same item type by look at the name
                for item_check in self.items:
                    # TODO need to add item type into items for checks
                    if item_check.name == item_entity.name:
                        item_check.item.stackable += 1
                        stacked = True

                if not stacked:
                    self.items.append(item_entity)

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({'equip': item_entity})
            else:
                results.append({'message': Message('The {0} cannot be used'.format(item_entity.name), libtcod.yellow)})

        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                print(type(kwargs))
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        # Check if item is a stackable and the stack is above 1
                        if item_entity.item.stackable and item_entity.item.stackable > 1:
                            for item_check in self.items:
                                if item_entity.name == item_check.name:
                                    item_check.item.stackable -= 1
                        else:
                            self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item_entity):
        self.items.remove(item_entity)

    def drop_item(self, item_entity):
        results = []

        if self.owner.equipment.main_hand == item_entity or self.owner.equipment.off_hand == item_entity:
            self.owner.equipment.toggle_equip(item_entity)

        item_entity.x = self.owner.x
        item_entity.y = self.owner.y

        if item_entity.item.stackable and item_entity.item.stackable > 1:
            # Reduce stack size
            item_entity.item.stackable -= 1
            # Create a new item to drop
            # TODO fix the item type. might need to give items a type
            item_entity = spawn_item(self.owner.x, self.owner.y, item_type='healing_potion')
        else:
            self.remove_item(item_entity)

        results.append({'item_dropped': item_entity, 'message': Message('You dropped the {0}'.format(item_entity.name), libtcod.dark_yellow)})

        return results
