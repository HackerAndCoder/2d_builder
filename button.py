import pygame

pygame.init()

text_font = pygame.font.Font(None, 25)

def get_render_center(screen_width, screen_height, button):
    return (screen_width // 2 - (button.width // 2), screen_height // 2 - (button.height // 2))

class Button:
    def __init__(self, width, height, text):
        self.width = width
        self.height = height
        self.text = text
        self.hovered = False
    
    def get_render(self):
        button = pygame.Surface((self.width, self.height))
        if not self.hovered:
            button.fill((80, 80, 80))
        else:
            button.fill((100, 100, 100))
        text = text_font.render(self.text, True, (255, 255, 255))
        button.blit(text, (self.width // 2 - text.get_rect().width // 2, self.height // 2 - text.get_rect().height // 2))
        return button
    
    def update(self, mouse_pos, button_pos, mouse_state):
        self.hovered = False
        if button_pos[0] < mouse_pos[0] < button_pos[0]+self.width:
            if button_pos[1] < mouse_pos[1] < button_pos[1]+self.height:
                self.hovered = True
                if mouse_state:
                    return True
        return False