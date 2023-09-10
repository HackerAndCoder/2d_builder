from utils import *

registered_blocks = {}

class Block:
    def __init__(self, display_name, local_name, texture, is_solid = True):
        self.display_name = display_name
        self.local_name = local_name
        self.texture = texture
        self.is_solid = is_solid
    
    def get_name(self):
        return self.local_name

def register_block(display_name, local_name, texture, is_solid = True):
    block_object = Block(display_name, local_name, texture,is_solid)
    registered_blocks[local_name] = block_object
    return block_object

class Blocks:
    air_block = Block('Air', 'air', None, False)
    grass_block = register_block('Grass block', 'grass_block', get_texture('grass_block'))
    dirt_block = register_block('Dirt', 'dirt_block', get_texture('dirt'))
    stone_block = register_block('Stone', 'stone_block', get_texture('stone'))
    gold_ore = register_block('Gold ore', 'gold_ore_block', get_texture('gold_ore'))
    iron_ore = register_block('Iron ore', 'iron_ore_block', get_texture('iron_ore'))
    coal_ore = register_block('Coal ore', 'coal_ore_block', get_texture('coal_ore'))
    spawner = register_block('Mob spawner', 'spawner_block', get_texture('mob_spawner'))
    glass = register_block('Glass block', 'glass', get_texture('glass'), False)

