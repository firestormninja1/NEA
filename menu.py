import pygame, os, re, sys, Window, game_level
from boxes import BoxGroup, AutoBox
from transition import SurfaceFade
import matplotlib.pyplot as plt
pygame.init()

x, y = Window.x, Window.y
os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = Window.Display(new_window=True)

topic_num = {
        'Systems Architecture':"1.1",
        'Software and Software development': "1.2",
        'Exchanging Data': "1.3",
        'Data types, Data structures, and Algorithms': "1.4",
        'Elements of Computational thinking, Problem solving, and programming': "2"
    }

def get_topic_number(topic):
    return topic_num.get(topic)

def show_leaderboards(surface, user_data) -> None:
    # extract username and points as an array for each user, forming a 2D array
    user_points = [[username, sum(user_data[username]['points'])] for username in user_data] # create a 2D array with [[username,points] for each user]
    top_ten = Window.bubble_sort2D(user_points)[:10] # highest -> lowest of the top 10
    font = pygame.font.SysFont('Sans', 30)
    longest_name = font.render('W'*15, 1, (255, 255, 255)).get_rect()  # longest name's data
    padding_y = 20
    padding_x = longest_name.width + 20
    start_x = (window.WIDTH - padding_x) // 2
    start_y = (window.HEIGHT - (padding_y * 6) - longest_name.height * 10) // 2  # position all names to the vertical center

    # draw text username and points titles
    username = font.render('Username', 1, (255, 255, 255))
    points = font.render('Points',1,(255,255,255))
    surface.blit(username, (start_x, 60))
    surface.blit(points, (start_x+padding_x - 20 ,60))
    pygame.draw.line(surface, (255,255,255),(start_x-13,65+username.get_height()),(start_x+padding_x+points.get_width()-10,65+username.get_height()))

    # draw the actual values for each user
    for i in range(len(top_ten)):
        rendered_name = font.render(f'{i+1}) {top_ten[i][0]}', 1, (255, 255, 255))
        rendered_points = font.render(str(top_ten[i][1]), 1, (255, 255, 255))
        surface.blit(rendered_name, (start_x, (padding_y * i) + (longest_name.height * i) + start_y))
        surface.blit(rendered_points, (start_x + padding_x, (padding_y * i) + (longest_name.height * i) + start_y))

def get_graph(username):

    user_data = Window.read_json('users.json')
    points = user_data[username]['points']
    # the first and last x values
    start_x, end_x = 1, len(points)
    # adjust the size of the graph by multiplying it by that scale. Default scale is 80x80.
    # the adjust below multiplies the width and height respectively.
    plt.rcParams["figure.figsize"] = (9.4, 6)

    # adjust the starting and ending points so that the last 20 results are shown.
    if len(points) > 20:
        start_x = len(points) - 19
        end_x = len(points)
        points = points[-20:]

    color = 'black'

    # a linear/arithmetic sequence [ a + (n-1)d ]
    # with the first number being start_x, and common difference (d) being steps
    # and n being the length of the points array
    x_steps = 1
    x_range = range(start_x, end_x + 1, x_steps)
    # adjust the x values to match the x_range calculated above
    plt.xticks(x_range, color=color)

    # same logic as for the x values. Calculate the minimum and maximum y values with default steps of 10
    steps = 10
    start_y = 0
    end_y = 10

    if points: # if the user has points
        # adjust the sequence so it that matches the minimum and maximum of their points
        start_y = min(points)
        end_y = max(points)

    # set the y_range
    y_range = range(start_y, end_y + 10, steps)
    plt.yticks(y_range, color=color)

    # plot the points array against an array of the x values (the x_range)
    # also set a marker to make it easier to locate (x, y) values
    plt.plot(list(x_range), points, marker='o', color='#1f77b4')

    # create labels for the axes and graph
    plt.xlabel('Session', color=color)
    plt.ylabel('Points', color=color)
    plt.title('Points gained in the last 20 attempts')

    plt.savefig('images/points.png') # save the image of the graph in a png file, which will then be loaded and blitted
    # plt.cla(); plt.clf()

def show_graph(surface):
    graph_img = pygame.image.load('images/points.png')
    img_rect = graph_img.get_rect()
    # centre the image
    surface.blit(graph_img, ((window.WIDTH - img_rect.w)//2, (window.HEIGHT - img_rect.h)//2))


def get_accuracy(question_data, username) -> str:
    right = wrong = 0
    accuracy = 'N/A' # default accuracy is non applicable if no questions are attempted
    for question in question_data:
        stats = question_data[question][username]
        right += stats[0]
        wrong += stats[1]

    total_attempted = right + wrong

    if total_attempted > 0: # making sure denominator is not 0, and that they have attempted questions
        accuracy = (right/total_attempted)*100

    if total_attempted: # if they've answered at least one question and got it right/wrong
        accuracy = str(round(accuracy, 2))+'%'

    return accuracy

def get_topic_boxes(username, user_data) -> list:
    default_message = 'Achieve 100% accuracy and enter the portal in the level to unlock'
    topics = []
    row_1 = ['Systems Architecture', 'Software and Software development', 'Exchanging Data']
    row_2 = ['Data types, Data structures, and Algorithms',
             'Elements of Computational thinking, Problem solving, and programming']

    accuracy_1 = [] # first row's accuracies
    for topic in row_1:
        topic_number = get_topic_number(topic)
        question_data = Window.read_json(f'Questions/{topic_number}.json')
        accuracy_1.append(get_accuracy(question_data,username))

    accuracy_2 = [] # second row's accuracies
    for topic in row_2:
        topic_number = get_topic_number(topic)
        question_data = Window.read_json(f'Questions/{topic_number}.json')
        accuracy_2.append(get_accuracy(question_data, username))

    # arrange topic selection
    width1 = 430
    padding1 = (window.WIDTH - 3 * width1) // 4
    for i in range(3):
        # adjust the current best time if the user doesn't have one
        current_time = user_data[username][get_topic_number(row_1[i])]
        if current_time == -1:
            current_time = default_message
        else:
            current_time = Window.convert_time_format(current_time)
        topics.append(
            # create a box at suitable position with padding
            AutoBox(padding1 * i + (width1 * i) + padding1, 200, (width1, 0.4 * width1), row_1[i], text=row_1[i]+f' \\n \\n Accuracy: {accuracy_1[i]}  \\n Best Time: {current_time}',center_text=(False,True),font_size=22))

    width2 = 520
    padding2 = (window.WIDTH - 2 * width2) // 3
    padding_y = 200

    for j in range(2):
        # adjust the current best time if the user doesn't have one
        current_time = user_data[username][get_topic_number(row_2[j])]
        if current_time == -1:
            current_time = default_message
        else:
            current_time = Window.convert_time_format(current_time)
        # create a box at suitable position with padding
        topics.append(AutoBox(padding2 * j + (width2 * j) + padding2, topics[1].rect.h + padding_y + padding1,(width2, 0.35 * width2), row_2[j], text=row_2[j]+f' \\n \\n Accuracy: {accuracy_2[j]}  \\n Best Time: {current_time}',center_text=(False,True),font_size=22))
    return topics


def show_instructions(surface):
    instructions = pygame.image.load('images/instructions.png')
    # scale up the image to fit the window size
    instructions = pygame.transform.scale(instructions, surface.SIZE)
    # draw the image on the topleft of the surface
    surface.screen.blit(instructions, (0, 0))

def show_menu(username) -> None:
    user_data = Window.read_json('users.json')
    topics = get_topic_boxes(username, user_data)
    rec = topics[1].rect # the 2nd topic's rect
    rec2 = topics[2].rect # the 3rd topic's rect
    username_width = AutoBox.MEDIUM_FONT.render(f'username: {"W"*15} ', 1, (255, 255,255)).get_width() + 45  # finding out the maximum width for a username since 'W' is largest width character
    username_text = f'Username: {username} \\n Points: {sum(user_data[username]["points"])}'

    leaderboard_width = AutoBox.MEDIUM_FONT.render(f'Leaderboards', 1, (255, 255, 255)).get_width() * 1.3 # get a slightly scaled up width of leaderboards font

    # position the leaderboards box at the centered x position relative to the 2nd topic box
    leaderboard_pos = (rec.x + (rec.w - leaderboard_width)//2, 40)
    leaderboard_size = (leaderboard_width, topics[1].rect.h // 2)
    leaderboard_box = AutoBox(*leaderboard_pos, leaderboard_size, 'leaderboard', text='Leaderboards', center_text=(True, True))

    # space between leaderboard box and username box == space between leaderboard box and instructions box
    username_pos = (rec2.x + (rec2.w - username_width)//2, 40)
    username_size = (username_width, topics[1].rect.h // 2)
    username_box = AutoBox(*username_pos, username_size, 'username', text=username_text, font_size=23, center_text=(False, True))

    instructions_pos = (leaderboard_box.rect.left - (username_box.rect.x - leaderboard_box.rect.right) - leaderboard_width, 40)
    instructions_size = (leaderboard_width, topics[1].rect.h // 2)
    instructions_box = AutoBox(*instructions_pos, instructions_size, 'instructions', text='How To Play', center_text=(True, True))

    all_boxes = BoxGroup(*topics, leaderboard_box, username_box, instructions_box)
    fade = SurfaceFade(window.SIZE)
    leaderboards = graph = instructions = False
    get_graph(username)
    while True:
        window.refresh(back=True, show_mouse_pos=False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check for button clicks
                clicked = all_boxes.check_clicks()
                # don't register non go back clicks if not in the topic selection
                if clicked and (leaderboards or graph or instructions):
                    clicked=False

                # check for back click
                # clicking back on non topic screens takes user back to topics screen. If on the topic screen, takes the
                # user back to Platform Access screen.
                if window.check_return():
                    if leaderboards:
                        leaderboards = False
                    elif graph:
                        graph = False
                    elif instructions:
                        instructions = False
                    else:
                        return

                elif bool(clicked): # if a valid click was made
                    corresponding_num = get_topic_number(clicked.obj_type)
                    if corresponding_num: # if the clicked box is a topic
                        game_level.play_level(username, corresponding_num)
                        # update user information after a change has been made by finishing a level don't do it constantly
                        user_data = Window.read_json('users.json')
                        username_box.update_text(f'Username: {username} \\n Points: {sum(user_data[username]["points"])}')
                        topics = get_topic_boxes(username,user_data) # updates the text_box size and text after user completes a level
                        all_boxes = BoxGroup(*topics, username_box, leaderboard_box, instructions_box)
                        get_graph(username)

                    # change state of the variables depending on the conditions.
                    elif clicked.obj_type == 'leaderboard':
                        leaderboards = True

                    elif clicked.obj_type == 'username':
                        graph = True

                    elif clicked.obj_type == 'instructions':
                        instructions = True

        if leaderboards: # display the leaderboards
            show_leaderboards(window.screen, user_data)

        elif graph: # display the graph
            show_graph(window.screen)

        elif instructions: # display the instructions
            show_instructions(window)

        else: # show topic selection
            all_boxes.update_boxes(window.screen)
            text = 'Click the box above to view progress graph'
            rendered_text = window.SMALL_FONT.render(text,1,(255,255,255))
            # position it so that the center of the text == center of the username box
            pos = (username_box.rect.x + (username_box.rect.width - rendered_text.get_width())//2, username_box.rect.bottom + 10)
            window.draw_text(text, pos, size='SMALL')
        fade.fade(window.screen)
        window.draw_back()
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    import random
    # show_menu(random.choice(list(Window.read_json('users.json'))))
    show_menu('Harsh21')
