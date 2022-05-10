import pygame
from Window import Display as window

class ScreenFade:
    def __init__(self, direction, colour, time=0.6):
        self.direction = direction # 1 == fade outwards, -1 == fade inwards
        time = time*60 # 60 is the FPS
        self.colour = colour
        # adjust the speed such that the vertical and horizontal walls reach the sides at the same time
        self.speed_x = round((window.WIDTH//2)/time)
        self.speed_y = round((window.HEIGHT//2)/time)
        self.fade_counter_x = self.fade_counter_y = 0
        self.acceleration = 2

    def fade(self, surface):
        fade_complete = False
        self.fade_counter_x += self.speed_x * self.acceleration
        self.fade_counter_y += self.speed_y * self.acceleration
        # noinspection PyTypeChecker
        self.acceleration = max(1, self.acceleration*0.97)
        counter_x = self.fade_counter_x
        counter_y = self.fade_counter_y
        if self.direction == 1: # outwards fade
            # horizontal movement
            # pygame.draw.rect(surface, self.colour, (0 - counter_x, 0, window.WIDTH//2, window.HEIGHT))
            # pygame.draw.rect(surface, self.colour, (window.WIDTH//2 + counter_x, 0, window.WIDTH//2, window.HEIGHT))
            # vertical movement
            pygame.draw.rect(surface, self.colour, (0, -window.HEIGHT//2 - counter_y, window.WIDTH, window.HEIGHT))
            pygame.draw.rect(surface, self.colour, (0, window.HEIGHT//2 + counter_y, window.WIDTH, window.HEIGHT))

        else: # fade going inwards
            # pygame.draw.rect(surface, self.colour, (-window.WIDTH//2 + counter_x, 0, window.WIDTH//2, window.HEIGHT))
            # pygame.draw.rect(surface, self.colour, (window.WIDTH - counter_x, 0, window.WIDTH//2, window.HEIGHT))
            pygame.draw.rect(surface, self.colour, (0, -window.HEIGHT + counter_y, window.WIDTH, window.HEIGHT))
            pygame.draw.rect(surface, self.colour, (0,window.HEIGHT - counter_y, window.WIDTH, window.HEIGHT))

        if counter_y - 100 > window.HEIGHT/2:
            fade_complete = True
            self.acceleration = 2
            self.fade_counter_x = 0
            self.fade_counter_y = 0
        return fade_complete

class SurfaceFade:
    def __init__(self, size):
        self.fade_rect = pygame.Surface(size)
        self.fade_rect.fill(0)
        self.alpha_counter = 255

    def fade(self, surface):
        if self.alpha_counter > 0:
            self.alpha_counter -= 4//0.6

        if self.alpha_counter > 0: # if the screen isn't fully transparent yet
            self.alpha_counter -= 6
        else: # if it's transparent don't waste resources changing alpha and blitting
            return

        self.fade_rect.set_alpha(self.alpha_counter)
        surface.blit(self.fade_rect,(0,0))