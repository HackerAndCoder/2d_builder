import pygame, os, math, pickle

pygame.init()

width = 800
height = 600

screen = pygame.display.set_mode((width, height))

block_screen_size = 40

camera_offset = [0, -10]

block_select_pos = [0, 0]

registered_blocks = {}

screen_dimensions_block = (width // block_screen_size, height // block_screen_size)

game_font = pygame.font.Font(None, 16)

class Keybinds:
    move_up = pygame.K_w
    move_down = pygame.K_s 
    move_left = pygame.K_a 
    move_right = pygame.K_d 
    remove = 1 # 1 is the left mouse button
    place = 3 # right mouse buttong,  TODO maybe add option for keys 

class Screens:
    ingame = 0
    title_screen = 1
    paused = 2
    block_select = 3

current_screen = Screens.ingame

def get_texture(name):
    return pygame.transform.scale(pygame.image.load(os.path.join('assets', name + '.png')).convert_alpha(), (block_screen_size, block_screen_size))

def key_to_screen(key):
    return (key[0]*block_screen_size, key[1]*block_screen_size)

def screen_to_key(screen_pos):
    return (math.floor(screen_pos[0]/block_screen_size), math.floor(screen_pos[1]/block_screen_size))

def get_looking_at():
    pos = list(screen_to_key(camera_offset))
    pos[0] += screen_dimensions_block[0] // 2
    pos[1] += screen_dimensions_block[1] // 2
    return pos

class Block:
    def __init__(self, display_name, local_name, texture):
        self.display_name = display_name
        self.local_name = local_name
        self.texture = texture

def register_block(display_name, local_name, texture):
    block_object = Block(display_name, local_name, texture)
    registered_blocks[local_name] = block_object
    return block_object

class Blocks:
    blocks = {}
    grass_block = register_block('Grass block', 'grass_block', get_texture('grass_block'))
    dirt_block = register_block('Dirt', 'dirt_block', get_texture('dirt'))
    stone_block = register_block('Stone', 'stone_block', get_texture('stone'))
    gold_ore = register_block('Gold ore', 'gold_ore_block', get_texture('gold_ore'))
    iron_ore = register_block('Iron ore', 'iron_ore_block', get_texture('iron_ore'))
    coal_ore = register_block('Coal ore', 'coal_ore_block', get_texture('coal_ore'))
    spawner = register_block('Mob spawner', 'spawner_block', get_texture('mob_spawner'))


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
            return None
    
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
            try:
                self.set_block(pos, registered_blocks[name])
            except:
                print(f'An error occured loading block {name} at {pos}')

    def get_save(self):
        save_string = ''
        for key in self.blocks.keys():
            save_string += f'{str(key[0])},{str(key[1])}:{self.blocks[key].local_name}\n'
        #return pickle.dumps(self.blocks) # doesn't work
        return save_string

def save_game(world : World, name : str):
    global camera_offset
    save = f'{camera_offset[0]},{camera_offset[1]}\n'
    save += world.get_save()
    with open(name + '.mc', 'w') as f:
        f.write(save)

def load_save(world : World, name : str):
    global camera_offset
    with open(name + '.mc') as f:
        player_info = f.readline().strip().split(',')
        save = f.read()
    
    camera_offset = [int(player_info[0]), int(player_info[1])]
    world.load_save(save)

world = World()

try:
    load_save(world, 'save')    
except:
    world.gen_world()

game_clock = pygame.time.Clock()

#hotbar_index = 0
#hotbar = [Blocks.stone_block, None, None, None, None, None, None, None, None]
#hotbar_image = pygame.transform.scale_by(pygame.image.load(os.path.join('assets', 'hotbar.png')).convert_alpha(), 3)
hand_item = Blocks.stone_block
pause_dimmer = pygame.Surface((width, height)); pause_dimmer.set_alpha(200); pause_dimmer.fill((0, 0, 0))

def render_blocks(world):
    suface = pygame.Surface((width, height))
    suface.fill((128, 128, 255))
    
    for key in world.get_blocks().keys():
        #suface.blit(world.get_block(key).texture, (key_to_screen(key)[0], key_to_screen(key)[1]))
        suface.blit(world.get_block(key).texture, (key_to_screen(key)[0] + (0 - camera_offset[0] - (block_screen_size // 2)), key_to_screen(key)[1] + (0 - camera_offset[1] + 30)))
    
    return suface

def render_world(world, events, do_move = True):
    screen = pygame.Surface((width, height))
    screen.fill((255, 255, 255))
    
    block_render = render_blocks(world)
    #screen.blit(block_render, (0 - camera_offset[0] - (block_screen_size // 2), 0 - camera_offset[1]))
    screen.blit(block_render, (0, 0))
    
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect((width // 2) - (block_screen_size // 2), (height // 2) - (block_screen_size // 2), block_screen_size, block_screen_size), 3)

    try:
        screen.blit(game_font.render(str(world.get_block(get_looking_at()).display_name) + f': {str(get_looking_at())} screen: {current_screen}', True, (0, 0, 0)), (10, 10))
        #print(world.get_block(get_looking_at()).name)
    except:
        pass # we must be looking at air so we will just skip the drawing

    #screen.blit(hotbar_image,  ((width // 2) - (hotbar_image.get_width() // 2), height - hotbar_image.get_height()))

    if hand_item:
        screen.blit(hand_item.texture, (10, 25))

    for event in events:
        if do_move:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == Keybinds.remove:
                    world.remove_block(get_looking_at())
                elif event.button == Keybinds.place:
                    world.set_block(get_looking_at(), hand_item)
            
    
    keys = pygame.key.get_pressed()
    
    if do_move:
        if keys[Keybinds.move_up]: camera_offset[1] -= block_screen_size
        if keys[Keybinds.move_down]: camera_offset[1] += block_screen_size
        if keys[Keybinds.move_left]: camera_offset[0] -= block_screen_size
        if keys[Keybinds.move_right]: camera_offset[0] += block_screen_size

    return screen

def index_to_block_select(index_x, index_y):
    return (width//2-160+(index_x*block_screen_size*1.4), 120 + ((block_screen_size + 15) * index_y))

def check_block_select(max_size):
    global block_select_pos
    if block_select_pos[0] < 0:
        block_select_pos[0] = 0
    elif block_select_pos[0] >= max_size:
        block_select_pos[0] = max_size - 1
    
    if block_select_pos[1] < 0:
        block_select_pos[1] = 0
    elif block_select_pos[1] >= max_size:
        block_select_pos[1] = max_size - 1

def get_selected_block(x, y, grid_size):
    return y*grid_size + x

while True:
    game_clock.tick(10)
    events = pygame.event.get()

    if current_screen == Screens.ingame:
        screen.blit(render_world(world, events), (0, 0))
    
    elif current_screen == Screens.paused:
        screen.blit(render_world(world, events, False), (0, 0))
        screen.blit(pause_dimmer, (0, 0))
    
    elif current_screen == Screens.block_select:
        screen.blit(render_world(world, events, False), (0, 0))
        pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(width // 2 - 200, height // 2 - 200, 400, 400))

        counter_x = 0
        counter_y = 0
        for block in registered_blocks.values():
            screen.blit(block.texture, index_to_block_select(counter_x, counter_y))
            counter_x += 1
            if counter_x == 6:
                counter_x = 0
                counter_y += 1
        
        selection = pygame.Rect(0, 0, block_screen_size, block_screen_size)
        selection.topleft = index_to_block_select(block_select_pos[0], block_select_pos[1])
        pygame.draw.rect(screen, (0, 0, 0), selection, 3)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if current_screen in (Screens.paused, Screens.ingame, Screens.block_select):
                if event.key == pygame.K_ESCAPE:
                    if current_screen == Screens.paused or current_screen == Screens.block_select:
                        current_screen = Screens.ingame
                    else:
                        current_screen = Screens.paused
            
            if current_screen in (Screens.ingame, Screens.block_select):
                if event.key == pygame.K_b:
                    if current_screen == Screens.block_select:
                        current_screen = Screens.ingame
                    else:
                        current_screen = Screens.block_select
                        block_select_pos = [0, 0]
            
            if current_screen == Screens.block_select:
                if event.key in (Keybinds.move_up, pygame.K_UP): block_select_pos[1] -= 1
                if event.key in (Keybinds.move_left, pygame.K_LEFT): block_select_pos[0] -= 1
                if event.key in (Keybinds.move_down, pygame.K_DOWN): block_select_pos[1] += 1
                if event.key in (Keybinds.move_right, pygame.K_RIGHT): block_select_pos[0] += 1
                check_block_select(6)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if current_screen == Screens.block_select:
                try:
                    hand_item = tuple(registered_blocks.values())[get_selected_block(block_select_pos[0], block_select_pos[1], 6)]
                except:
                    hand_item = tuple(registered_blocks.values())[0]
                
                current_screen = Screens.ingame

        elif event.type == pygame.QUIT:
            save_game(world, 'save')
            pygame.quit()
            exit()
    
    pygame.display.flip()
