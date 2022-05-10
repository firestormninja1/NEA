import os, sys, pygame, Window, random
from boxes import Textbox, AutoBox
from boxes import BoxGroup
from transition import ScreenFade

def get_boxes(question_data, question, window):
    w, h = window.width, 200

    text = question
    options = question_data[question]['options']
    options = random.sample(options, 4) # select a random order from the options, shuffling the order of options

    question_box = AutoBox(0, 0, (w, h*0.8), obj_type='question', text=text)

    # calculate dimensions of the boxes.
    x_padding = 35
    x1 = x_padding
    x2 = (w//2) + x_padding
    width = (w//2) - (2*x_padding)
    option_w, option_h = (width,(window.HEIGHT-h)*0.47)
    y_padding = (window.HEIGHT - question_box.rect.height - (2*option_h))//3

    # creating all the option instances, and positioning them respectively
    option_1 = AutoBox(question_box.rect.x + x1, question_box.rect.bottom + y_padding, (option_w, option_h), obj_type='option', text=options[0])
    option_2 = AutoBox(x2, question_box.rect.bottom + y_padding, (option_w, option_h), obj_type='option', text=options[1])
    option_3 = AutoBox(option_1.rect.left, option_1.rect.bottom + y_padding, (option_w, option_h), obj_type='option', text=options[2])
    option_4 = AutoBox(option_2.rect.left, option_2.rect.bottom + y_padding, (option_w, option_h), obj_type='option', text=options[3])
    main_group = BoxGroup(option_1, option_2, option_3, option_4, question_box)
    return main_group

def start_question(question, question_data, timer=0):
    # ---------- key variables -------------#
    pygame.init()
    x, y = Window.x, Window.y
    Display = Window.Display
    os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"
    FPS = 60
    clock = pygame.time.Clock()
    window = Window.Display(new_window=True, caption='Question Display')
    correct_answer = question_data[question]['options'][0] # correct answer will always be at first index of options
    main_group = get_boxes(question_data, question, window)

    # feedback instance
    feedback_text = question_data[question]['feedback']
    feedback = AutoBox(0,40,(window.SIZE[0],window.SIZE[1]-40),text=feedback_text, obj_type='feedback',font_size=29,center_text=(False,False),colour=Display.BACKGROUND)

    continue_button = Textbox(100, 0.9*window.height,text='Continue',text_size='medlarge',padding=(10,10))
    options_screen = True
    result = None
    check_click = True
    move_to_feedback = 3000 # the time to wait until moving onto feedback screen == 6 seconds
    time1 = 0
    continue_button.create_rect()
    start_fade = True
    fade = ScreenFade(1, (0, 0, 0))
    going_back = False
    time1 = time1
    timer = timer
    pause_timer = False
    debug = 1
    while True:
        window.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT and result is None:
                return timer
                # sys.exit()
            if event.type == pygame.KEYDOWN and debug:
                if event.key == pygame.K_ESCAPE:
                    return timer

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check for the continue button click on the main/ options screen
                if pygame.time.get_ticks() - time1 > move_to_feedback and time1 and options_screen: # wait a bit of time
                    if continue_button.check_click():
                        options_screen = False # don't display options anymore, signalling the feedback screen to show

                # check for continue button click on the feedback screen
                if continue_button.check_click() and not options_screen and not move_to_feedback:
                    start_fade = True
                    going_back = True

                clicked = main_group.check_clicks() # check if an option has been clicked
                if clicked and check_click: # if an option has been clicked
                    result = clicked.text == correct_answer # check if the clicked option's text matches to the correct answer
                    time1 = pygame.time.get_ticks()
                    check_click = False # don't check for more clicks on any other options

                    # change the options' properties based on the outcome
                    for option in main_group.objects:
                        if option.obj_type=='question': # if the box is a question, then don't make any changes
                            continue

                        if option.text != correct_answer: # incorrect answer
                            option.background = option.incorrect_colour
                        else: # correct answer
                            option.background = option.correct_colour
                            move_to_feedback //= 2 # if they're right, show the continue button faster

                        option.check_collision = False # don't check for collisions with the selected option/button anymore
                    pause_timer=True # don't continue the timer after the question has been answered to allow the user to absorb info without worrying about time

                    clicked.border_colour = clicked.hover_border # highlight the selected colour so the user doesn't forget what they clicked
                    clicked.border_radius = 7
        if options_screen: # if the user is still on the options screen
            main_group.update_boxes(window.screen) # update the boxes (draw them) onto the screen

        elif not options_screen: # if an option has been picked, and it was incorrect show the feedback text
            if not feedback.text: # checks if there is feedback for the question
                start_fade = True
                going_back = True # go back

            if not going_back:
                feedback.show(window.screen) # show the feedback
                continue_button.check_hover(pygame.mouse.get_pos())
                continue_button.show(window.screen, center=True)
                move_to_feedback = False

        # after a option is picked, and after a certain time, move to feedback screen, and display its continue button
        if pygame.time.get_ticks() - time1 > move_to_feedback and time1 and options_screen:
            continue_button.check_hover(pygame.mouse.get_pos())
            continue_button.show(window.screen, center=True)
            for box in main_group.get_list():
                if box.obj_type =='question': # keep the question opacity the same
                    continue
                box.surface.set_alpha(60) # reduce the opacity of other options

        if start_fade: # do the fade animation
            if going_back:
                fade.direction = -1 # fading out
            if fade.fade(window.screen):
                start_fade = False
                if going_back: # if they're exiting the question screen
                    return result, timer

        if (pygame.time.get_ticks() - time1) >= 1000 and not pause_timer: # 1 ticks == 1 millisecond, 1000 millisecond = 1 second, update timer every second
            timer += 1  # account for the time in the question screen
            time1 = pygame.time.get_ticks()

        window.draw_text(text=f'Time: {Window.convert_time_format(timer)}', pos=(670,3), size='MEDIUM',center=(True,False))
        pygame.display.update()
        clock.tick(FPS)

