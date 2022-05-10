# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30
# GET QUESTIONS: https://quizizz.com/admin/search/h446%20OCR%20computer%20science%201.2.1?queryId=5f6b05fd7c198b001b54c8de-1650744363792
# if __name__ == 'Game_V4':
from entities import Entity, Enemy, Group
import pygame, Window, question_window, os, sys, random, csv
from Tiles import AnimatedTile, Tile
from transition import ScreenFade

pygame.init()
read_json = Window.read_json # using the pre-coded read and write methods to json files
write_json = Window.write_json
x, y = Window.x, Window.y
os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = Window.Display(new_window=True)

class World:
    def __init__(self, level):
        self.obstacle_list = []
        self.bg_scroll = 0
        self.no_collide = []  # blocks that shouldn't be checked for collision
        self.height = Window.Display.MAX_BLOCKS_Y
        self.all_tiles = []
        self.game_level = self.load_level(level)

    def process_data(self, tile_info, img_dict, player_img, enemy_img):
        data = self.game_level
        enemy_counter = 0
        player = Entity(500, 500, 'player', tile_info['player_scale'], melee_dps=50)
        # iterate through each value in level data file
        decorations = []  # add in all the tiles that don't need to be checked for collision
        death_blocks = []
        enemies = []
        portals = []

        for ind, layer in enumerate(data):
            for y, row in enumerate(layer):
                self.height = len(layer)
                for x, tile in enumerate(row):
                    if tile == '-1':
                        continue

                    # if 24 <= int(tile) <= 25:
                    #     tile = str(int(tile) - 2)
                    img = img_dict[tile]  # get the image from the list of images
                    img_rect = img.get_rect()
                    # img_rect.topleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y)
                    img_rect.bottomleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y + 46)
                    img_mask = pygame.mask.from_surface(img)

                    obj = None
                    if tile in tile_info['obstacle'].split():
                        obj = Tile(img, *img_rect.topleft, 'Obstacle')
                        if ind != 0:
                            self.obstacle_list.append(obj) # if it isn't the 1st layer (for no collisions)
                    elif tile in tile_info['decoration'].split():  # grass / no collision decoration
                        obj = Tile(img, *img_rect.topleft, 'Decoration')
                    elif tile in tile_info['kill_block'].split():  # water
                        obj = Tile(img, *img_rect.topleft,'Death Block')
                        if ind != 0: death_blocks.append(obj)
                    elif tile in tile_info['player'].split():  # create player if there's one on the map
                        player = Entity(img_rect.x, img_rect.y, player_img, tile_info['player_scale'], melee_dps=1000)
                    elif tile in tile_info['enemy'].split():
                        enemies += [Enemy(img_rect.x, img_rect.y, enemy_img,
                                          tile_info['enemy_scale'],
                                          all_animations=['Idle', 'Die', 'Running', 'Attack'],
                                          max_health=100, x_vel=2, move_radius=tile_info['move_radii'][enemy_counter],melee_dps=35)]
                        enemy_counter += 1
                    elif tile == tile_info['portal']:
                        portals += [AnimatedTile(img, img_rect.x, img_rect.y, 'Portal')]
                    if obj: self.all_tiles.append(obj)
        return player, decorations, death_blocks, enemies, portals

    def draw(self, background, target):
        background_width = background.get_width()
        for i in range(4):
            window.screen.blit(background, ((i * background_width) - self.bg_scroll, 0))

        for tile in self.all_tiles:
            tile.draw(window.screen, target)

    @staticmethod
    def load_level(level):
        layers = []
        path = f'levels/{level}'
        files = os.listdir(path)

        ordered = sorted(files,key=lambda i: int(i.split('_')[1][:i.split('_')[1].index('.')]))  # sort layers based on numbers
        # highest number == highest layer -> prioritised/placed above everything else
        # so by sorting from lowest -> highest, lowest layer is blitted first, and highest layer is blitted last/ on top of everything else

        files = ordered  # sort the tiles such that highest layer is prioritised/ blitted over the other layers
        for index, file in enumerate(files):
            with open(os.path.join(path, file)) as file:
                level = csv.reader(file, delimiter=',')
                layers.append([*level])
            # sys.exit()
        return layers

# noinspection PyAssignmentToLoopOrWithParameter


def get_time_units(timer):
    time_split = timer.split(':')
    units = ''
    if time_split[2].lstrip('0'): # remove leading 0s
        units = ' seconds'
    if time_split[1].lstrip('0'): # remove leading 0s
        units = ' minutes'
    if time_split[0].lstrip('0'): # remove leading 0s
        units = ' hours'
    return units

def show_summary(right, wrong, total_questions, accuracy, streak, points, timer, player_died, portal_enter):
    timer = Window.convert_time_format(timer)
    accuracy = str(accuracy)+'%'
    units = get_time_units(timer)
    timer = str(timer) + units
    show_back = False
    initial_time = pygame.time.get_ticks()
    attempted = f'{right+wrong}/{total_questions}'
    while True:
        window.refresh(back=show_back, pos=(650, 480))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if window.check_return():
                    return

            if event.type == pygame.QUIT:
                sys.exit()

        initial_x = 430
        for i,line in enumerate(['Attempted', 'Right', 'Accuracy', 'Best Streak', 'Points Collected', 'Time Survived']):
            window.draw_text(line+':', (initial_x,150+(50*i)), center=(False,False))
        for j,value in enumerate([attempted, right, accuracy, streak, points, timer]):
            window.draw_text(str(value),(initial_x*2,150+(j*50)))
        if player_died:
            window.draw_text('You Died',(0,50),center=(True, False), colour=(255, 0, 0), size='MEDLARGE')
        elif portal_enter: # if the player was alive and entered the portal
            window.draw_text('Level Completed!', (0, 50),center=(True, False),colour=(0, 255, 0), size='MEDLARGE')
        else:
            window.draw_text('Level Quit. No points will be added', (0, 50),center=(True, False),colour=(255, 0, 0), size='MEDLARGE')
        if pygame.time.get_ticks() - initial_time >= 2000 and not show_back: # if back button is not being shown and 2 seconds have passed
            show_back = True
        pygame.display.update()


class Camera:
    def __init__(self, target):
        assert hasattr(target, 'rect'), 'target needs a rect object'
        self.target = target
        self.rect = target.rect.copy()
        self.x, self.y = target.rect.topleft
        self.rect.x = window.WIDTH//2
        self.rect.y = window.HEIGHT // 2

    def update(self):
        assert hasattr(self.target, 'rect'), 'target needs a rect object'
        if hasattr(self.target, 'combat_animations') and hasattr(self.target, 'current_action'):
            if self.target.current_action not in self.target.combat_animations:
                # make sure the camera doesn't jitter after switching animations. Keeps the camera in place
                if self.target.direction == 1:
                    self.rect.bottomleft = self.target.rect.bottomleft
                else:
                    self.rect.bottomright = self.target.rect.bottomright
                # self.rect.y = window.HEIGHT // 2 + 200
        else: #
            if self.target.direction == 1:
                self.rect.bottomleft = self.target.rect.bottomleft
            else:
                self.rect.bottomright = self.target.rect.bottomright

# noinspection PyTypeChecker
def get_questions(level, username):
    # select the (max_quota) number of questions for each of the [red, amber, green] category, no longer random selection using sample alone, no longer selecting 10 worst
    question_data = read_json(f'Questions/{level}.json')
    # green = > 75, amber = 50 < x < 75, red = < 50
    # quota = 4, 4, 4
    # sort the questions based on accuracy from largest -> smallest
    questions = Window.bubble_sort2D([[question, question_data[question][username][2]] for question in question_data])
    # separate the questions based on which category they fit in
    green = []
    amber = []
    red = []
    for question, accuracy in questions:
        total_attempts = sum(question_data[question][username][:2]) # sum of right and wrong attempts
        if accuracy >= 0.75 or (accuracy == 0 and total_attempts == 0): # never attempted or strong knowledge
            green.append(question)
        elif 0.5 <= accuracy < 0.75: # moderate knowledge
            amber.append(question)
        else:
            red.append(question) # if the accuracy is less than 50%; absolute shit-housery

    final_list = [] # a list of the final questions

    lists = sorted([green, red, amber], key=lambda i: len(i)) # smallest -> largest lists
    max_quota = 4 # means, that in total there should be 9 questions because 3 * 3 -> (red, amber, green) == 9
    quotas = [max_quota]*3 # initially max_quota reds, max_quota ambers, and max_quota greens

    # find out how many of each category should be picked
    for index, category in enumerate(lists[:-1]): # loop until n-1
        if len(category) < quotas[index]: # if the current category doesn't have enough questions for its assigned quota
            quotas[index+1] += quotas[index] - len(category) # carry over the remaining ones to the next category
            quotas[index] = len(category) # change the quota for the current category to it's length as it can only fit that much

    quotas[-1] = min(quotas[-1], len(lists[-1])) # if everything has been carried over to the last one, it should only pick however much it can

    for index, category in enumerate(lists):
        current_quota = quotas[index] # get the quota that points to the current question
        sample = random.sample(category, current_quota) # select a random order of (n = quota) questions from the current category
        final_list +=[*sample] # add the question to the final list of questions

    return final_list, question_data

def update_data(question_data, questions, max_questions, level, username, points, timer, portal_enter, total_accuracy, user_quit):
    # update question data and user data when/ if run == False, if they just finished level/died
    write_json(question_data, f'Questions/{level}.json')
    user_info = read_json(f'users.json')
    current_best = user_info[username][level]

    # only update the completion time if the user answered all the questions/ defeated all enemies and they made it to the portal
    if portal_enter and total_accuracy == 100:
        if current_best == -1:
            current_best = timer
        else:
            current_best = min(current_best, timer)

    user_info[username][level] = current_best # update time if it was lower
    if len(questions) != max_questions and not user_quit: user_info[username]['points'].append(points) # adding points onto the player's history for graph plotting; if they answered questions
    write_json(user_info, f'users.json') # save all the changes

def play_level(username, level):
    ENEMY = random.choice(['knight', 'samurai', 'stormy']) # pick a random enemy
    PLAYER = 'player'

    LEVEL = 2 #random.randint(1, 5) # choose a random map layout
    world = World(LEVEL)
    TILE_TYPES = os.listdir(f'level_config/{LEVEL}/Tiles') # get a list of all the tiles
    background = pygame.transform.scale(pygame.image.load(Window.get_path(f'level_config/{LEVEL}/background.png')),window.SIZE).convert_alpha()

    # load in game data
    img_dict = {}
    for i in TILE_TYPES:
        img = pygame.image.load(Window.get_path(f'level_config/{LEVEL}/Tiles/{i}')).convert_alpha()
        name = i[:i.index('.')]
        img_dict[name] = img

    # load in the questions
    # NOTE: question_data[question][username] = list(correct: int, incorrect: int, percentage: float)
    questions, question_data = get_questions(level, username)
    questions = random.sample(questions, len(questions)) # shuffle the order of selected questions
    # questions will be treated as a stack. Last in is first out
    tile_info = Window.read_json(f'level_config/{LEVEL}/tile_info.json')
    # sprite groups
    player, decorations, death_blocks, enemies, portals = world.process_data(tile_info, img_dict, PLAYER, ENEMY)

    death_blocks_group = Group(*death_blocks)
    enemy_group = Group(*enemies)
    portal_group = Group(*portals)

    fade = ScreenFade(1, (0, 0, 0))
    start_fade = True
    run=True
    show_question = False
    time1 = pygame.time.get_ticks()
    timer = 0
    points = 0
    total_right = total_wrong = total_accuracy = 0
    streak = 0
    max_streak = 0
    portal_enter = False
    questions = questions[:len(enemy_group.sprites)]
    max_questions = len(questions)
    user_quit = False

    camera = Camera(player)
    while run:
        player.check_alive()
        camera.update()

        # only perform actions based on these conditions
        ground_conditions = not player.in_air and player.health and (
                    player.y_vel <= player.GRAVITY) and not start_fade # making sure player isn't in the air and is still alive

        move_conditions = not (
                player.sword_attack) and not start_fade  # only allow attacking if not already in attack animation -> ADD INTO ITERATIVE DEVELOPMENT

        window.refresh(show_mouse_pos=False, back=True, pos=(10, 10))
        world.draw(background, camera)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                user_quit = True

            # check for keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # level is not finished, therefore don't save changes
                    return

                if event.key == pygame.K_r:
                    enemy_group.regen()

                if event.key == pygame.K_h:
                    player.health = player.max_health

                # jumping
                # making sure the player is falling or jumping during
                if (event.key == pygame.K_w or event.key == pygame.K_UP) and ground_conditions and move_conditions and not player.in_air:
                    player.jumping = True

                # attacking
                if (event.key == pygame.K_SPACE) and ground_conditions and move_conditions:
                    if player.current_weapon == 1:  # sword selected
                        player.sword_attack = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if window.check_return():
                    if len(questions) == max_questions: # if they haven't answered any questions
                        return
                    run = False # otherwise, save the user's attempts and don't add any points
                    user_quit = True

        keys = pygame.key.get_pressed()

        # group handling
        moving_left = (keys[pygame.K_a] or keys[pygame.K_LEFT]) and move_conditions
        moving_right = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and move_conditions

        # player handling
        player.draw(window.screen, camera)
        player.update(moving_left, moving_right, world)

        # enemy handling
        enemy_group.update(player, window.screen, world)
        enemy_group.draw(window.screen, target=camera)

        # death block handling
        death_blocks_group.draw(window.screen, target=camera)
        death_blocks_group.update(player, camera)  # do death block checking for player

        # portal handling
        portal_group.draw(window.screen, target=camera)
        # if the user hasn't already entered the portal
        for portal in portal_group.sprites:
            portal_collision = portal.update(player) and not portal_enter
            if portal_collision and (not questions or not enemy_group.sprites): # if all questions are answered or enemies are dead, then allow the user to enter the portal
                start_fade = True # start the transition
                fade.direction = -1
                show_question = False # don't show a question
                portal_enter = True # mark the portal as entered

        if show_question:
            assert bool(questions), 'No more questions left' # making sure there are still questions left to pop
            # extract current stats for the question and adjust them based on result of the user's choice
            current_question = questions.pop()
            question_window_values = question_window.start_question(current_question, question_data, timer)
            # extract current stats for the question and adjust them based on result of the user's choice
            if isinstance(question_window_values, tuple): # if the result and timer was returned
                result = question_window_values[0] # the outcome of the question displayed
                user_right, user_wrong, user_accuracy = (question_data[current_question])[username]
                if result:
                    user_right += 1; points += 10; total_right+=1; streak += 1 # if they got the question right, add 10 points, increase streak, and recover health
                    player.health = min(player.health + 0.2*player.max_health, player.max_health)
                else:
                    user_wrong += 1; total_wrong += 1; streak = 0
                if user_wrong!=0 or user_right!=0:
                    user_accuracy = user_right/(user_right+user_wrong) # to ensure that the denominator is not 0
                    total_accuracy = round(total_right/(total_right+total_wrong), 2)
                question_data[current_question][username] = [user_right, user_wrong, user_accuracy] # update statistics of the user on the question displayed
                timer = question_window_values[1]
            else:
                timer = question_window_values
            max_streak = max(streak, max_streak)

            # inwards fade
            start_fade = True
            fade.direction = 1
            show_question = False

        # start fade animation if player has died
        if player.remove and not start_fade:
            start_fade = True
            fade.direction = -1

         # if an enemy has died, present a question
        enemy_dead = enemy_group.check_death()
        if enemy_dead and questions: # if there are still questions left, then do the animation to goto question screen
            start_fade = True
            fade.direction = -1

        if (pygame.time.get_ticks() - time1) > 1000 and not player.remove and not portal_enter: # 1 ticks == 1 millisecond, 1000 millisecond = 1 second
            timer += 1  # account for the time in the question screen
            time1 = pygame.time.get_ticks()

        # draw text and back button
        window.draw_text(text=f'Time: {Window.convert_time_format(timer)}', pos=(670,3), size='MEDIUM', center=(True,False))
        window.draw_back()
        window.draw_text(f'Current Weapon: {["Sword"][player.current_weapon - 1]}', (200, 5))
        window.draw_text(f'Points: {points}',(490,5))

        # do fade animation
        if start_fade:
            if fade.fade(window.screen): # if the fade has completed
                start_fade = False # don't show the intro fade anymore

                if (portal_enter or player.remove) and fade.direction == -1:
                    run = False
                    show_question = False

                # if fading out, check if there are still questions and enemies left to show a question, otherwise its just a normal fade
                elif fade.direction == -1 and not player.remove:
                    show_question = True


        pygame.display.update()  # make all the changes
        clock.tick(FPS)

    # show the user their summary statistics:
    total_accuracy = round(total_accuracy*100, 2)
    show_summary(total_right, total_wrong, max_questions, total_accuracy, max_streak, points, timer, player.remove, portal_enter)
    update_data(question_data, questions, max_questions, level, username, points, timer, portal_enter, total_accuracy, user_quit)

def main(username, user_id, level):
    play_level(username, user_id, level)

if __name__ == '__main__':
    main('Testing1', 0, 2)
