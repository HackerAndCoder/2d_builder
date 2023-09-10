import pygame, os

def get_texture(name, size = 40):
    return pygame.transform.scale(pygame.image.load(os.path.join('assets', name + '.png')), (size, size))