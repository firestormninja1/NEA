import pygame, sys, os, random, inspect

x = '\\'.join(os.path.abspath(__file__).split('\\')[:-2])  # allow imports from main folder
sys.path.insert(1, x)

from Window import Display, StopRunning

# websites:
# https://www.piskelapp.com/
# https://pixlr.com/x/#home

pygame.init()



class Tile:
    def __init__(self, image, rect, mask):
        self.rect = rect
        self.mask = mask
        self.image = image
        self.direction = 0

    def show(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, obj_type, scale, max_health=100, x_vel=6, all_animations=None, combat_animations=None,
                 melee_dps=33):
        self.JUMP_Y = 14.7
        self.GRAVITY = self.JUMP_Y / 20
        self.all_animations = all_animations
        self.combat_animations = combat_animations
        if all_animations is None and obj_type == 'player':
            self.all_animations = ['Idle', 'Running', 'Jumping', 'Falling', 'Melee', 'Bow', 'Die']
        elif not self.all_animations:
            raise StopRunning('Animations for a non-player entity not passed in')

        if combat_animations is None and obj_type == 'player':
            self.combat_animations = [self.get_index('Melee'), self.get_index('Bow')]
        pygame.sprite.Sprite.__init__(self)
        self.max_health = max_health
        self.health = self.max_health
        self.y_vel = 0
        self.obj_type = obj_type
        self.animations = []
        self.animation_pointer = 0
        self.current_action = 0
        self.time1 = pygame.time.get_ticks()
        for animation in self.all_animations:
            self.get_animations(obj_type, animation, scale)
        self.image = self.animations[self.current_action][self.animation_pointer]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.x_vel = x_vel
        self.direction = 1  # [1,-1] = [facing right, facing left]
        self.flip_image = False
        self.jumping = False
        self.in_air = True
        self.sword_attack = False
        self.current_weapon = 1  # 1 == sword, 2 == Bow
        self.mask = pygame.mask.from_surface(self.image)
        self.current_weapon_damage = {1: melee_dps}  # sword deals 50 damage
        self.health_rect = pygame.Rect((x, y, 70, 7))
        self.health_rect.center = self.rect.center
        self.health_rect.y -= self.rect.h // 2 + 10
        self.remove = False
        self.idle_rect = self.rect

    def move(self, moving_left: bool, moving_right: bool, world):  # handle player movement
        self.health_rect.y = self.rect.y - 10
        # reset movement variables
        dx = dy = 0
        check = True
        if self.health <= 0:
            return

        # horizontal movement

        if moving_left and check:
            dx = -self.x_vel
            self.flip_image = True
            self.direction = -1

        if moving_right and check:
            dx = self.x_vel
            self.flip_image = False
            self.direction = 1

        # jumping/vertical movement
        if self.jumping and (not self.in_air) and check:
            self.y_vel = -self.JUMP_Y
            self.jumping = False
            self.in_air = True

        # gravity/ downward acceleration
        y1 = self.y_vel
        self.y_vel = min(self.y_vel + self.GRAVITY, 10)
        dy += self.y_vel

        # check collision with floor
        for tile in world.obstacle_list:
            # check collision in x direction
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.w, self.rect.h):
                dx = 0
                # If AI collision with wall, turn em around
                if isinstance(self, Enemy):
                    # self.direction *= -1
                    # self.move_counter *= -1
                    self.wall_collision = True
                if self.obj_type != 'player':
                    continue # if they collided with wall, don't check for y collision with that wall anymore

            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.w, self.rect.h):
                dy = 0
                # check if jumping and collision occurs below ground
                if self.y_vel < 0:
                    self.y_vel = 0
                    self.rect.top = tile.rect.bottom

                # if they are falling
                elif self.y_vel > 0:
                    self.y_vel = 0
                    self.in_air = False
                    self.rect.bottom = tile.rect.top

        # check if going off the sides
        if self.rect.y > world.height * Display.TILE_DIMENSION_Y - self.rect.h:  # if the player is off screen
            self.remove = True
            # self.kill()
            self.update_action(self.get_index('Die'))
            return

        # update player position
        self.rect.x += dx
        self.rect.y += dy
        self.health_rect.x += dx
        self.health_rect.y += dy
        self.idle_rect.midbottom = self.rect.midbottom

    def draw_health_bar(self, surface, target):
        temp = self.idle_rect.copy()  # copy the rect of the current entity
        temp.x = temp.x - target.rect.x + Display.WIDTH / 2.0
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2 - 10

        if not self.check_alive():  # if the entity is dead, don't draw a health bar
            return

        self.health_rect.midtop = temp.midtop
        if self.direction == -1 and self.obj_type in ['knight', 'samurai']:  # adjusts the position of the health bar if need be
            self.health_rect.topright = temp.topright

        health_colour = (16, 130, 0)
        lost_health_colour = (173, 181, 172)

        if self.obj_type != 'player': # enemy health bar colours
            health_colour = (255, 38, 0)
            lost_health_colour = (219, 182, 175)

        pygame.draw.rect(surface, lost_health_colour, self.health_rect)
        current_health = self.health_rect.copy()
        current_health.w = (self.health / self.max_health) * self.health_rect.w  # the % of health * full width
        pygame.draw.rect(surface, health_colour, current_health)
        pygame.draw.rect(surface, (0, 0, 0), self.health_rect, 2)

    def animation_handling(self):  # updates the animation frame
        self.check_alive()
        # update animation based on a timer since last time recorded
        cooldown_time = 90  # every 120 main game loops change animation frame
        if self.current_action == self.get_index('Idle'):
            cooldown_time = 120
        if self.obj_type == 'stormy' and self.current_action in self.combat_animations:
            cooldown_time = 70
        # update entity image
        self.image = self.animations[self.current_action][self.animation_pointer]
        image_rect = self.image.get_rect()
        image_rect.midbottom = self.rect.midbottom
        if self.obj_type != 'stormy':
            if self.direction == 1:
                image_rect.bottomleft = self.rect.bottomleft  # keep the entity on the ground
            else:
                image_rect.bottomright = self.rect.bottomright

        self.rect = image_rect
        self.idle_rect.midbottom = image_rect.midbottom # move the collision rectangle

        if self.obj_type =='player': # only the player's hit box should be dynamic, for the rest it should be normal
            self.idle_rect = image_rect
            # this fixes the issue of after enemies attack near a tile, if there was some particle that collided with a tile,
            # it would check for collision and move them up even tho it shouldn't have

        self.mask = pygame.mask.from_surface(self.image)
        current_time = pygame.time.get_ticks()
        death_index = self.get_index('Die')

        # change animation frame
        if (current_time - self.time1) > cooldown_time:
            self.animation_pointer += 1  # add one to animation pointer
            if self.current_action in self.combat_animations:  # if its a combat animation
                if self.animation_pointer >= len(
                        self.animations[self.current_action]):  # if at the last frame of animation
                    self.sword_attack = False  # no longer attacking with a weapon
                    self.animation_pointer = 0  # reset animation pointer
                    self.current_action = 0  # go back to idle position

            elif self.current_action == death_index:  # death animation
                if self.animation_pointer > len(self.animations[death_index]) - 1:
                    self.animation_pointer = len(self.animations[death_index]) - 1
                    self.remove = True

            else:  # looping animations
                self.animation_pointer = self.animation_pointer % len(self.animations[self.current_action])

            self.time1 = pygame.time.get_ticks()

    def update_action(self, new_action: int, world=None):
        """ check if the new action is different to the new action
        # if the new action is the same as the old action, it would set animation pointer to 0 every time so only the
        # first frame of the animation would be shown. By adding this check, it makes it so that the animation pointer and animation is changed/reset
        # only if there is a change in the player action. """
        melee_index = self.get_index('Melee')
        if new_action == melee_index and world:
            images = self.animations[melee_index]
            if any(self.frame_change_collision(image, world) for image in
                   images):  # if wall collisions have occured in any of the frames
                self.sword_attack = False
                return

        if new_action != self.current_action:
            self.current_action = new_action
            # reset the index at which the animation for the specific action starts at
            self.animation_pointer = 0
            self.time1 = pygame.time.get_ticks()

    def update(self, moving_right: bool, moving_left: bool, world):
        self.move(moving_right, moving_left, world)
        self.animation_handling()
        # update player animations
        if self.obj_type == 'player' and self.health:
            if self.in_air or self.y_vel > self.GRAVITY:  # if jumping or falling the 0.75 is due to gravity
                if self.y_vel < 0:  # if going upwards
                    self.update_action(self.get_index('Jumping'))
                    pass
                else:  # if falling
                    self.update_action(self.get_index('Falling'))
                    pass
            elif self.sword_attack:
                self.update_action(self.get_index('Melee'),
                                   world)  # if switching to sword animation, make sure new image doesn't collide with walls
            elif moving_right or moving_left:
                self.update_action(self.get_index('Running'))
            else:
                self.update_action(self.get_index('Idle'))
            return

    def frame_change_collision(self, image, world):
        image_rect = image.get_rect()
        if self.direction == 1:
            image_rect.bottomleft = self.rect.bottomleft  # keep the entity on the ground
        else:
            image_rect.bottomright = self.rect.bottomright

        for tile in world.obstacle_list:
            if image_rect.colliderect(tile.rect):
                return True
        return False

    def get_animations(self, obj_type: str, animation: str, scale: tuple):  # add animations for this sprite into a list
        animation_scale = {
            'player': {
                'Bow': (scale[0] * 1.6, scale[1]),
                'Melee': (scale[0] * 1.4, scale[1]),
                'Idle3': (scale[0] * 5, scale[1]),
                'Idle2': (scale[0] * 1.4, scale[1]),
                'Idle': (48, scale[1]),
                'Die': (scale[0] * 1, scale[1] * 0.8),
                'Running2': (scale[0] * 1.4, scale[1]),
                'Running': (48, scale[1]),
                'Jumping': (48, scale[1]),
                'Falling': (48, scale[1])
            },
            'samurai': {
                'Idle': (scale[0] * 0.5, scale[1] * 1),
                'Die': (scale[0] * 1.2, scale[1] * 0.95),
                'Running': (scale[0] * 0.5, scale[1]),
                'Attack': (scale[0] * 1.2, scale[1])
            },
            'knight': {
                'Idle': (46, 92),
                'Attack': (46*2.9, 92),
                'Jumping': (46, 92),
                'Falling': (46, 92),
                'Running': (46 * 1.5, 92),
                'Die': (120, 80)
            },
            'stormy': {
                'Idle':(scale[0]*0.4,scale[1]*0.9),
                'Running': (scale[0]*0.4,scale[1]*0.9),
                'Attack':(scale[0]*1.9,scale[1]*1.9),
                'Die':(scale[0]*0.65,200)
            }
        }
        temp = []
        img_path = f"images/mobs/{obj_type}/{animation}"
        images = os.listdir(img_path) # get a list of images

        scale2 = scale
        scale_info = animation_scale.get(obj_type)
        if scale_info:
            scale_data = scale_info.get(animation)
            if scale_data: scale2 = [*map(int, scale_data)]
        scale2 = [*map(int, (scale2[0] * 0.8, scale2[1] * 0.8))]

        for image in images:  # iterate through the images in this directory
            image = pygame.image.load(os.path.join(img_path, image))
            temp += [pygame.transform.scale(image,scale2).convert_alpha()]
        self.animations += [temp]

    def draw(self, surface, target):
        temp = self.rect.copy()
        temp.x = temp.x - target.rect.x + Display.WIDTH // 2
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2
        surface.blit(pygame.transform.flip(self.image, self.flip_image or self.direction == -1, False), temp.topleft)
        temp = self.idle_rect.copy()
        temp.x = temp.x - target.rect.x + Display.WIDTH // 2
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2
        # pygame.draw.rect(surface, (255,15,64), temp, 2)
        self.draw_health_bar(surface, target)

    def check_alive(self):  # check if the entity is alive
        alive = self.health > 0
        if not alive:  # if they've died
            self.health = 0  # health is back at 0
            death_index = self.get_index('Die')  # get the index of where the 'Die' animation is
            self.update_action(death_index)  # update the series of images that contain the death animation
        return alive

    def get_index(self, animation: str):  # get the death index from the list of animations
        index = None
        if animation in self.all_animations:
            index = self.all_animations.index(animation)
        return index

    def combat_collision(self, obj):  # check for sword attack collision
        if self.check_collision(obj) and obj.sword_attack:
            # self.collisions += 1 and obj.sword_attack and self.direction != obj.direction
            self.health -= obj.current_weapon_damage.get(obj.current_weapon) / 25
            return 1
        return 0

    def check_collision(self, obj):
        if self.health <= 0:
            return
        return self.idle_rect.colliderect(obj.idle_rect)


class Enemy(Entity):
    def __init__(self, x, y, obj_type, scale, max_health=100, x_vel=2, all_animations=None, attack_radius=150,
                 move_radius=3, melee_dps=30):
        super().__init__(x, y, obj_type, scale, max_health, x_vel, all_animations, melee_dps=melee_dps)
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        attack_animations = self.animations[self.get_index('Attack')]
        idle_image = self.animations[self.get_index('Idle')][0]

        attack_radius = max(attack_animations, key=lambda image: image.get_width()).get_width() + 20

        attack_radius -= idle_image.get_width() - 10
        self.attack_vision = pygame.Rect(0, 0, attack_radius, 3)
        self.combat_animations = [self.get_index('Attack')]
        self.attacked = False
        self.wait = 0
        self.change_direction = False
        self.wall_collision = False
        self.move_radius = move_radius * Display.TILE_DIMENSION_X
        self.idle_rect.w += 13

    def rec_collision(self, obj):
        # check if obj is within enemy's attack vision
        return self.attack_vision.colliderect(obj.rect)

    def start_attack(self, obj, world):
        # if attack cooldown is over, obj within attack vision and enemy(self) on the ground
        if self.wait == 0 and self.rec_collision(obj) and self.check_alive() and (not self.in_air and self.y_vel >= self.GRAVITY):
            self.sword_attack = True # change enemy state
            self.update_action(self.get_index('Attack'), world)  # change the animation to attack animation
            self.wait = 100 # initiate cooldown

    def AI(self, world):
        if self.in_air or self.y_vel > self.GRAVITY:  # if the enemy is falling
            self.move(0, 0, world)  # don't move in any direction
            self.set_idling(world)
            return  # don't do anything else related to AI movement
        self.wait = max(0, self.wait - 1)

        AI_moving_right = False
        if self.current_action in [self.get_index('Attack')]:
            return

        # set up attack radius
        self.attack_vision.center = self.rect.center
        if self.direction == 1:
            self.attack_vision.left = self.rect.right
        else:
            self.attack_vision.right = self.rect.left

        if self.check_alive():
            # checking if enemy is not already idling and not falling/jumping
            if random.randint(1, 500) == 1 and not self.idling and not self.in_air:
                self.set_idling(world)
                pass

            # if the enemy is in idling motion:
            if self.idling:
                # self.update_action(0)
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False
                    if self.change_direction:
                        self.direction *= -1
                        self.move_counter *= -1

                return  # don't attempt to move the player in idling animation

            if self.direction == 1:
                AI_moving_right = True

            AI_moving_left = not AI_moving_right
            self.move(AI_moving_left, AI_moving_right, world)
            self.update_action(self.get_index('Running'), world)
            self.move_counter += self.x_vel

            self.change_direction = False
            if (self.move_counter > (self.move_radius) or self.wall_collision) and self.y_vel <= self.GRAVITY:
                self.change_direction = True
                self.set_idling(world)
                self.wall_collision = False

    def set_idling(self, world):
        self.idling = True
        self.idling_counter = 50
        self.update_action(self.get_index('Idle'), world)

    def update(self, player, surface, world):
        self.animation_handling()

        # combat checking
        if self.health > 0:

            self.start_attack(player, world)  # check if player collision has
            player.combat_collision(self) # check if self has dealt damage to player
            self.combat_collision(player)  # check if player has dealt damage to self

        self.AI(world)  # do enemy AI

    def regen(self):
        self.health = self.max_health
        self.update_action(self.get_index('Idle'))


class Group:
    def __init__(self, *args):
        self.sprites = [*args]

    def update(self, *args, **kwargs):
        for sprite in self.sprites:
            if hasattr(sprite, 'update'):
                sprite.update(*args, **kwargs)

    # this is for images
    def draw(self, surface, target=None):
        for sprite in self.sprites:
            # Check if the sprite has a `draw` method.
            if hasattr(sprite, 'draw'):
                sprite.draw(surface, target=target)
            else:
                surface.blit(sprite.image, sprite.rect)

    def regen(self):
        for sprite in self.sprites:
            # Check if the sprite has a `regen` method.
            if hasattr(sprite, 'regen'):
                sprite.regen()

    def check_death(self): # used to check if an entity has died to trigger a question
        entity_died = False
        for obj in self.sprites:
            if obj.remove: # if the death animation was initiated and then finished:
                entity_died = True
                obj.kill() # free up memory space
                self.sprites.remove(obj) # remove the obj from the array
        return entity_died
