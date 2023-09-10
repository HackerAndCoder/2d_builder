import pygame, math, button, os
from world import *
from utils import *
from blocks import *

pygame.init()

width = 800
height = 600

screen = pygame.display.set_mode((width, height))

block_screen_size = 40

camera_offset = [0, -10]

block_select_pos = [0, 0]

screen_dimensions_block = (width // block_screen_size, height // block_screen_size)

game_font = pygame.font.Font(None, 16)


class Keybinds:
    move_up = pygame.K_w
    move_down = pygame.K_s 
    move_left = pygame.K_a 
    move_right = pygame.K_d
    remove = pygame.K_q # for both place and remove, you can remap the keyboard keys but mouse buttons 1 and 3 will always break and place without modifying the code
    place = pygame.K_e 

class Screens:
    ingame = 0
    title_screen = 1
    paused = 2
    block_select = 3

class Buttons:
    save_button = button.Button(200, 40, 'Save and quit')
    back_to_game_button = button.Button(200, 40, 'Back to game')

current_screen = Screens.ingame

def key_to_screen(key):
    return (key[0]*block_screen_size, key[1]*block_screen_size)

def screen_to_key(screen_pos):
    return (math.floor(screen_pos[0]/block_screen_size), math.floor(screen_pos[1]/block_screen_size))

def get_looking_at():
    pos = list(screen_to_key(camera_offset))
    pos[0] += screen_dimensions_block[0] // 2
    pos[1] += screen_dimensions_block[1] // 2
    return pos


def save_game(world : World, name : str):
    global camera_offset
    save = f'{camera_offset[0]},{camera_offset[1]}\n'
    save += world.get_save()
    with open(os.path.join('saves', name + '.dat'), 'w') as f:
        f.write(save)

def load_save(world : World, name : str):
    global camera_offset
    with open(os.path.join('saves', name + '.dat')) as f:
        player_info = f.readline().strip().split(',')
        save = f.read()
    
    camera_offset = [int(player_info[0]), int(player_info[1])]
    world.load_save(save)

def set_block(world : World, pos, block : Block):
    world.set_block(pos, block)
    world.update_around(pos)

def remove_block(world : World, pos):
    world.remove_block(pos)
    world.update_around(pos)

world = World()

try:
    load_save(world, 'save')    
except:
    world.gen_world()

game_clock = pygame.time.Clock()

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
        screen.blit(game_font.render(str(world.get_block(get_looking_at()).display_name) + f': {str(get_looking_at())}', True, (0, 0, 0)), (10, 10))
        #print(world.get_block(get_looking_at()).name)
    except:
        pass # we must be looking at air so we will just skip the drawing

    #screen.blit(hotbar_image,  ((width // 2) - (hotbar_image.get_width() // 2), height - hotbar_image.get_height()))

    if hand_item:
        screen.blit(hand_item.texture, (10, 25))

    for event in events:
        if do_move:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    remove_block(world, get_looking_at())
                elif event.button == 3:
                    set_block(world, get_looking_at(), hand_item)
                
            elif event.type == pygame.KEYDOWN:
                if event.key == Keybinds.place:
                    set_block(world, get_looking_at(), hand_item)
                elif event.key == Keybinds.remove:
                    remove_block(world, get_looking_at())
            
    
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
    
    if get_selected_block(block_select_pos[0], block_select_pos[1], max_size) >= len(registered_blocks):
        block_select_pos = [0, 0] # if the selection is not over a block than just put it back at the start

def get_selected_block(x, y, grid_size):
    return y*grid_size + x

while True:
    game_clock.tick(10)
    world.random_tick_blocks(1)
    events = pygame.event.get()
    
    if current_screen == Screens.title_screen:
        screen.fill((100, 100, 100))

    if current_screen == Screens.ingame:
        screen.blit(render_world(world, events), (0, 0))
    
    elif current_screen == Screens.paused:
        screen.blit(render_world(world, events, False), (0, 0))
        screen.blit(pause_dimmer, (0, 0))
        screen.blit(Buttons.save_button.get_render(), (width // 2 - Buttons.save_button.width // 2, height // 2 + 50))
        screen.blit(Buttons.back_to_game_button.get_render(), (width // 2 - Buttons.back_to_game_button.width // 2, height // 2))
        if Buttons.save_button.update(pygame.mouse.get_pos(), (width // 2 - Buttons.save_button.width // 2, height // 2 + 50), pygame.mouse.get_pressed()[0]):
            save_game(world, 'save')
            current_screen = Screens.title_screen
        
        elif Buttons.back_to_game_button.update(pygame.mouse.get_pos(), (width // 2 - Buttons.back_to_game_button.width // 2, height // 2), pygame.mouse.get_pressed()[0]):
            current_screen = Screens.ingame
    
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
                        hand_item = tuple(registered_blocks.values())[get_selected_block(block_select_pos[0], block_select_pos[1], 6)]
                    else:
                        current_screen = Screens.block_select
                        block_select_pos = [0, 0]
            
            if current_screen == Screens.block_select:
                if event.key in (Keybinds.move_up, pygame.K_UP): block_select_pos[1] -= 1
                if event.key in (Keybinds.move_left, pygame.K_LEFT): block_select_pos[0] -= 1
                if event.key in (Keybinds.move_down, pygame.K_DOWN): block_select_pos[1] += 1
                if event.key in (Keybinds.move_right, pygame.K_RIGHT): block_select_pos[0] += 1

                check_block_select(max_size=6)
            
            if current_screen == Screens.ingame:
                if event.key == pygame.K_r:
                    camera_offset = [0, -10]
        
        
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
