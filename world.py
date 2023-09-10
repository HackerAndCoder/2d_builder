from blocks import *
import random

class World:
    def __init__(self, width = 100, height = 64):
        self.width = width
        self.height = height
        self.blocks = {}
    
    def set_block(self, pos, block):
        self.blocks[tuple(pos)] = block
    
    def remove_block(self, pos):
        try:
            del self.blocks[tuple(pos)]
        except:
            pass
    
    def _update_block(self, pos):
        if self.get_block(pos) == Blocks.grass_block:
            if self.get_block((pos[0], pos[1] - 1)).is_solid:
                self.set_block(pos, Blocks.dirt_block)
    
    def _random_tick_block(self, pos):
        if self.get_block(pos) == Blocks.dirt_block:
            if not self.get_block((pos[0], pos[1] - 1)).is_solid:
                self.set_block(pos, Blocks.grass_block)
    
    def random_tick_blocks(self, num):
        for i in range(num):
            x = random.randint(0, self.width) - self.width // 2
            y = random.randint(0, self.height)
            self._random_tick_block((x, y))
            #print(f'random ticked {self.get_block((x, y)).get_name()}')
    
    def update_around(self, pos):
        x = pos[0]
        y = pos[1]

        self._update_block((x, y))
        self._update_block((x, y+1))
        self._update_block((x, y-1))
        self._update_block((x+1, y))
        self._update_block((x-1, y))
    
    def gen_world(self):
        for y in range(self.height):
            for x in range(self.width):
                x -= self.width // 2
                if y == 0:
                    self.blocks[(x , y)] = Blocks.grass_block
                elif y < 4:
                    self.blocks[(x , y)] = Blocks.dirt_block
                else:
                    self.blocks[(x , y)] = Blocks.stone_block

    def get_blocks(self):
        return self.blocks
    
    def get_block(self, pos):
        try:
            return self.blocks[tuple(pos)]
        except:
            return Blocks.air_block
    
    def load_save(self, save_string : str):
        save = save_string.split()
        self.blocks = {}
        for data in save:
            block_data = data.split(':') # ['0,0', 'grass_block']
            pos = block_data[0].split(',') # ['0', '0']
            pos[0], pos[1] = int(pos[0]), int(pos[1])
            name = block_data[1] # 'grass_block'
            if not name in registered_blocks.keys():
                print(f'An error occured registering {name} at {pos}')
                continue
            try:
                self.set_block(pos, registered_blocks[name])
            except:
                print(f'An error occured loading block {name} at {pos}')

    def get_save(self):
        save_string = ''
        for key in self.blocks.keys():
            save_string += f'{str(key[0])},{str(key[1])}:{self.blocks[key].local_name}\n'
        return save_string