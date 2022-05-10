import pygame, sys
import os

from Window import Display
from entities import Group

current_path = os.path.dirname(__file__)  # Where your .py file is located
image_path = os.path.join(current_path, 'images', '') # The image folder path
# print(image_path)
pygame.init()


class Tile(pygame.sprite.Sprite):
    def __init__(self, img, x, y, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.image = img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + Display.TILE_DIMENSION_X // 2, y)  # make it so that its at the center of a tile, even if the size isn't the same
        self.initial_time = pygame.time.get_ticks()
        self.obj_type = item_type
        self.direction = 1

    def draw(self, surface, target):
        temp = self.rect.copy()
        x, y = target.rect.topleft
        temp.x = temp.x - x + Display.WIDTH//2
        temp.y = temp.y - y + Display.HEIGHT//2
        surface.blit(self.image, temp)

    def update(self, obj, camera=None):
        # do the animation handling
        if hasattr(self, 'animation_handling'):
            self.animation_handling()
        # check for collision
        collision = self.check_collision(obj)
        return collision

    def check_collision(self, objs):
        if isinstance(objs, Group):
            for obj in objs:
                collision = self.mask_collision(obj)
                if collision:
                    if self.obj_type == 'Death Block': obj.health = 0
                    return True

        else:
            collision = self.mask_collision(objs) and objs.rect.y + objs.rect.h*0.5 >= self.rect.y # if more than half of body is submerged
            if collision:
                if self.obj_type == 'Death Block': objs.health = 0
                # if self.obj_type == 'Portal':print('here')
                return True

    def mask_collision(self, obj):
        mask = pygame.mask.from_surface(self.image)
        offset = (obj.rect.x - self.rect.x, obj.rect.y - self.rect.y)
        return mask.overlap(obj.mask, offset)

class AnimatedTile(Tile):
    def __init__(self, img, x, y, item_type):
        pygame.sprite.Sprite.__init__(self)
        Tile.__init__(self, img, x, y, item_type)
        self.animations = []
        self.get_animations()
        self.animation_pointer = 0
        self.image = self.animations[self.animation_pointer]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + Display.TILE_DIMENSION_X // 2, y)  # make it so that its at the center of a tile, even if the size isn't the same

    def get_animations(self):
        item_path = os.path.join(image_path, self.obj_type) # the image path of the item

        images = os.listdir(item_path)  # get a list of the image names for the animation
        for image in images:
            image = pygame.image.load(os.path.join(item_path, image))
            self.animations += [image]

    def animation_handling(self):
        cooldown_time = 90 # cooldown time
        if self.obj_type == 'Portal':
            cooldown_time = 100 # increase rate of change for frames if its a portal
        current_time = pygame.time.get_ticks()

        if current_time - self.initial_time >= cooldown_time: # if the cooldown time has finished
            self.animation_pointer = (self.animation_pointer + 1) % len(self.animations) # increase the animation pointer
            self.initial_time = current_time # change the time

        self.image = self.animations[self.animation_pointer] # update the image

        self.mask = pygame.mask.from_surface(self.image) # update the mask
        self.rect = self.image.get_rect()
        self.rect.midtop = (self.x + Display.TILE_DIMENSION_X // 2, self.y)  # make it so that its at the center of a tile, even if the size isn't the same