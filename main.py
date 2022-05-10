#---------------------------------- Imports ----------------------------------#

import pygame, os, re, json, menu, Window
from boxes import Textbox
from access import input_information

Display = Window.Display
read_json = Window.read_json
write_json = Window.write_json
# laptop
x, y = Window.x, Window.y
try:
    import pygame,os
    from Window import Display
    from boxes import Textbox, Inputbox
    import re,json
    from access import input_information
    import Window
    import Game_V4
except ImportError as error:
    print(error)

# lapto
x,y = Window.x,Window.y
# school computer
# x,y = 50,80
os.environ['SDL_VIDEO_CENTERED'] = '1'
#--------------------------------- Setting Up --------------------------------#
clock = pygame.time.Clock()

def get_path(path):
    absolute_path = os.path.abspath(path)
    assert os.path.exists(absolute_path), f"{path} doesn't exist"
    return absolute_path

background = get_path('images/logo2.png')
window = Display(caption='Platform Access',size=(1426, 690))
image = pygame.image.load(background)
background = pygame.transform.scale(image,window.SIZE)
window.background = background
pygame.init()
#------------------------------ update details ------------------------------#
def update_details():
    # fill in missing user data in question files. ie when a new question is added, don't have to do it manually
    for user in read_json('users.json'):
        for topic_name in os.listdir('Questions'):
            question_path = f'Questions/{topic_name}'
            topic_data = read_json(question_path)
            for question in topic_data:
                topic_data[question].setdefault(user, [0, 0, 0])
            write_json(topic_data, question_path)

#------------------------------- Main Game Loop ------------------------------#

def main():
    update_details() # if there's any user info missing from question data, fill it in before proceeding, ie when I decide
    # to add in a new question, I don't wanna manually type in user info

    login_box = Textbox(100,460,'Login',text_size='medlarge',padding=(0,0),size=(300,60))
    signUp_box = Textbox(100,530,'Sign Up',text_size='medlarge',padding=(0,0),size=(300,60))

    login=sign_up=False

    signUp_result=login_result=0
    while True:
        window.refresh()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                login = login_box.check_click(mouse_pos)
                sign_up = signUp_box.check_click(mouse_pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        mouse_pos = pygame.mouse.get_pos()
        login_box.check_hover(mouse_pos)
        signUp_box.check_hover(mouse_pos)

        login_box.show(window.screen,center=True)
        signUp_box.show(window.screen,center=True)

        if login:
            login_result = input_information(state='login')
            login = False

        elif sign_up:
            signUp_result = input_information(state='sign up')
            sign_up = False

        if signUp_result:
            username = signUp_result
            menu.show_menu(username)
            signUp_result = False # if come back to main menu, they should no longer be logged in

        if login_result:
            username = login_result
            menu.show_menu(username)
            login_result = False # if come back to main menu, they should no longer be logged in

        pygame.display.update()
        clock.tick()

if __name__ == '__main__':
    main()
