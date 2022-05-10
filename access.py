
import pygame, os, Window
from Window import Display, NoIndent, read_json, write_json
from boxes import Textbox
import re, json

# --------------------- Main Game stuff -------------------------------#
x,y = Window.x,Window.y
os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"
pygame.init()
clock = pygame.time.Clock()

def get_path(path):
    absolute_path = os.path.abspath(path)
    assert os.path.exists(absolute_path), f"{path} doesn't exist"
    return absolute_path

background = get_path('images/logo2.png')
window = Display(caption='Main Menu')
image = pygame.image.load(background)
background = pygame.transform.scale(image,(1426, 690))
window.background = background
#----------------------------------- Login -----------------------------------#
def presence_in_file(username: str, data: dict):
    return data.get(username)

def check_details(username, password, state):
    data = read_json('users.json') # extract user details
    username_data = presence_in_file(username, data) # .get checks if the key exists, and if it does, it returns the value, else None

    if state=='login':
        if not username_data: return -1 # if there is no key that matches to the username, it doesnt exist
        return username_data.get('password') == password # check if the username's password is the same as the one entered

    elif state=='sign up':
        if username_data: # if there is a key that matches to the username, it already exists
            return -1
        else: # if the username does not exist
            add_info(data, username, password) # add in user info to users.json and all question files
            return 1
    return 0

def add_info(data, username, password):
    data[username] = {"password": "", "points": [], "1.1": -1, "1.2": -1, "1.3": -1, "1.4": -1, "2": -1}
    data[username]['password'] = password

    questions = os.listdir('Questions')
    for file in questions:
        file_info = read_json(f'Questions/{file}')
        for question in file_info:
            file_info[question][username] = NoIndent([0, 0, 0])
        write_json(file_info, f'Questions/{file}') # write to all question files
    write_json(data, 'users.json') # if username was added to all question files, officially add em

def validate_character(string, click, character):
    # Only allow characters, numbers and certain symbols
    valid_chars = re.match('''[A-Za-z\d$@$!%*?&"£%^*(){}~#:;]+''', character)
    # return True if the username as long as the length is 
    # length is < 15 and typing in the username box and the character is valid
    return len(string+character) < 16 and click and bool(valid_chars)

def validate_username(username):
    # length error, not unique error
    if not(4 <= len(username) <= 15):
        return 1, 0
    if presence_in_file(username, Window.read_json('users.json')):
        return 0, 1
    if not(re.findall('([A-Za-z]+)', username)):
        return 0, 0

    return 0, 0 # no errors

def validate_password(password):
    return re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d$@$!%*?&]{4,15}",password)

def input_information(state):
    max_length=15
    username = ''
    password = ''
    fill_text = 'Username'
    fillpass_text = 'Password'

    counter = 0
    username_click = False
    password_click = False
    
    username_box = Textbox(100,460,text=fill_text.center(15),text_size='medlarge',size=(300,60))
    password_box = Textbox(100,530,text=fillpass_text.center(15),text_size='medlarge',size=(300,60))

    continue_button = Textbox(100,630,text='Continue',size=(200, 50),text_size='medlarge', padding =(10,0))
    continue_button.create_rect()
    continue_click = False

    incorrect_details = False
    display_string_length = False
    display_password_text = False

    successful_signUp = successful_login = False

    delete = False

    delete_counter = 0

    while True:
        data = read_json('users.json')
        window.refresh(back=True, pos=(435,500))
        username_box.text=fill_text
        password_box.text=fillpass_text

        username_box.create_rect()
        password_box.create_rect()
        continue_button.create_rect()

        continue_state = username and password # checks if both fields have an input in them
        message_text = None
        message_pos = (100, 595)
        message_colour = window.RED

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN: # handle key presses
                if event.key == pygame.K_TAB:
                    username_click = not username_click
                    password_click = not username_click
                    continue

                if event.key == pygame.K_RETURN and continue_state:
                    continue_click = True

                if username_click or password_click: # if the user is typing in username or password fields
                    incorrect_details = False # removes the error message if user has clicked/ is typing in an inputbox
                    display_password_text = False
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]: # if they press enter/return key, don't register as valid
                        continue

                character = event.unicode # collect the string format of the key pressed
                
                if event.key==pygame.K_BACKSPACE:
                    incorrect_details = False # remove the error message if it is present
                    delete = True
                    continue # a backspace isn't a valid 'character' that can be added to username and password, therefore

                # only add to username and/or password if the character is valid
                if validate_character(username, username_click, character): username += character
                if validate_character(password, password_click, character): password += character

            if event.type == pygame.KEYUP:
                if event.key==pygame.K_BACKSPACE:
                    delete=False
                    delete_counter = 0
                    if username_click:username=username[:-1]
                    if password_click:password=password[:-1]

            if event.type == pygame.MOUSEBUTTONDOWN: # check which button has been clicked
                mouse_pos = pygame.mouse.get_pos()

                go_back = window.check_return(mouse_pos)
                if go_back:
                    return
                username_click = username_box.check_click(mouse_pos)
                password_click = password_box.check_click(mouse_pos)
                continue_click = continue_button.check_click(mouse_pos) and continue_state # checking if continue button is available and also clicked

                if username_click or password_click: # don't show any error messages if they've clicked on a box again to type
                    incorrect_details = display_string_length = display_password_text = False

        # login page error messages
        if incorrect_details and state=='login':
            message_text = 'Incorrect username and password combination'
            message_colour = window.RED

        # sign up page error messages
        elif incorrect_details:
            message_text = 'Username is already taken'
            message_colour = window.RED
        elif display_string_length:
            message_text = 'Username must be between 4 and 15 characters long'
            message_colour = window.RED
        elif display_password_text:
            message_text='Password must contain 4-15 characters, minimum [one uppercase and lowercase letters, one number] and optional special character'
            message_colour = window.RED

        if message_text:
            window.draw_text(text=message_text, pos=message_pos,colour=message_colour,size='MEDIUM',center=(True,False))

        if continue_state: # if the username and password fields are filled make the continue button brighter
            continue_button.surface.set_alpha(300)
        else:
            continue_button.surface.set_alpha(100)

        delete_counter = [0, delete_counter + 1][delete]

        if delete_counter > 8 and (delete_counter%2)==0: # allows for singular + held down deletion
            if username_click: username=username[:-1]
            if password_click: password=password[:-1]
        
        if not username: # if nothing has been typed in the username box, it should display 'Username'
            fill_text='Username'
        if not password:# if nothing has been typed in the username box, it should display 'Password'
            fillpass_text = 'Password'

        if username_click: # if the the user has chosen to type in the username field highlight the border
            valid_username = all(i == 0 for i in validate_username(username))
            username_box.border_colour = username_box.RED
            fill_text = username
            if valid_username or state == 'login':
                username_box.border_colour = username_box.GREEN
        else:
            username_box.border_colour = username_box.default_border

        if password_click: # if the user has chosen to type in the password field highlight the border
            valid_password = validate_password(password)
            password_box.border_colour = password_box.RED
            fillpass_text = '*'*len(password) # cover the characters in the password
            if valid_password or state == 'login':
                password_box.border_colour = password_box.GREEN
        else:
            password_box.border_colour = password_box.default_border
            
        if continue_click: # if the continue button has been pressed
            valid_username = validate_username(username)
            valid_password = validate_password(password)

            if state=='sign up' and (sum(valid_username)==1 or not valid_password):
                if valid_username[0]: # if there was an issue with string length
                    display_string_length = True
                    display_password_text = False
                    incorrect_details = False

                elif valid_username[1]: # if there is already an existing user
                    display_string_length = False
                    display_password_text = False
                    incorrect_details = True

                elif not valid_password:
                    display_password_text = True
                    display_string_length = False
                    incorrect_details = False

            else: # if it was sign up or login state
                # print('here')
                display_string_length = False # don't show error messages
                correct = check_details(username, password, state)
                incorrect_details = correct < 1

                if not incorrect_details:
                    return username

            continue_click = False # once the button has been pressed, it should be counted as 'not pressed' after this section is ran
            # if not incorrect_details: return 1

        mouse_pos = pygame.mouse.get_pos()
        username_box.check_hover(mouse_pos)
        password_box.check_hover(mouse_pos)
        if continue_state:
            continue_button.check_hover(mouse_pos)
        
        # Display username and password boxes    
        username_box.show(window.screen, center=True)
        password_box.show(window.screen, center=True)
        continue_button.show(window.screen, center=True)
        window.draw_text(f'{state.title()} Page',(0,315),center=(True,False),size='MEDLARGE',underline=True)
        window.draw_text(f'Press [tab] or [select using mouse] to switch input boxes',(0, 370),center=(True,False),size='SMALL')
        window.draw_text(f'Press Return key/ Enter as an alternative to clicking continue',(0,400),center=(True,False),size='SMALL')

        pygame.display.update()
        clock.tick(30)
