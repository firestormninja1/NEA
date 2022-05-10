import os, sys, csv, json
from Window import get_path
from openpyxl import load_workbook
from boxes import Textbox
# from entities import Entity, Enemy, Projectile, Group
import pygame, Window, random, boxes
# from Items import Item, Decoration, DeathBlock
# from level_editor import load_level, draw_grid
#
# pygame.init()
#
# x, y = Window.x, Window.y
# os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"
#
# current_path = os.path.dirname(__file__)  # Where your .py file is located
# image_path = os.path.join(current_path, 'images')  # The image folder path
# coin_path = os.path.join(image_path, 'coin')
#
# FPS = 60
# clock = pygame.time.Clock()
# window = Window.Display(new_window=True)
# LEVEL = 2
# TILE_TYPES = os.listdir(f'images/tiles/{2}')
# img_list = []
# TILE_SCALE = (window.TILE_DIMENSION_X, window.TILE_DIMENSION_Y)
# tile_x,tile_y = TILE_SCALE
# # flip_images = [15]
# # entities = [17, 18]
# img_list = {}
# for i in TILE_TYPES:
#     img = pygame.transform.scale(pygame.image.load(Window.get_path(f'images/tiles/{LEVEL}/{i}')).convert_alpha(), TILE_SCALE)
#     # if i in flip_images: img = pygame.transform.flip(img, False, True)
#     # if i in entities: img = pygame.transform.scale(img, (46,92))
#     name = i[:i.index('.')]
#     img_list[name] = img
#
# print(img_list)
#
# class Tile:
#     def __init__(self, image, rect):
#         self.image = image
#         self.rect = rect
#         self.mask = pygame.mask.from_surface(self.image)
#
#     def draw(self):
#         window.screen.blit(self.image, self.rect)
#
# def load_level(level):
#     layers = {}
#     path = f'levels/level{level}'
#     files = os.listdir(path)
#     ordered = sorted(files, key = lambda i: int(i.split('_')[1][:i.split('_')[1].index('.')])) # sort based on layer
#     # print(ordered)
#
#     for index, file in enumerate(files):
#         with open(os.path.join(path, file)) as file:
#             level = csv.reader(file, delimiter=',')
#             x = []
#             # for row in level:
#             #     x+=[[*map(int,row)]]
#             layers[index] = [*level]
#         # sys.exit()
#     return layers
#
# game_level = load_level(2)
# print(game_level)
#
# def process_data(data):
#     obstacles = []
#     # obstacles.append()
#     for layer in data.values():
#         for y, row in enumerate(layer):
#             for x, tile in enumerate(row):
#                 if tile == '-1':
#                     continue
#                 tile = Tile(img_list[tile], (tile_x * x, tile_y*y, tile_x, tile_y))
#                 obstacles += [tile]
#     return obstacles
# level = process_data(game_level)
#
# # while 1:
# #     window.refresh()
# #     for event in pygame.event.get():
# #         if event.type == pygame.QUIT:
# #             pygame.quit()
# #             sys.exit()
# #     for tile in level:
# #         window.screen.blit(tile.image,tile.rect)
# #     pygame.display.update()
# #     clock.tick(FPS)
# ---------------------------- Loading and storing Excel stuff -----------------------------
# book = load_workbook('questions.xlsx')
# current_sheet = book['1.1']
# questions = {
#     1:{
#         'right':1,
#         'wrong':3
#     }
# }
# id = 1
# print(current_sheet['A'])
# for question, row in enumerate(current_sheet):
#     print(row)
#     for index, cell in enumerate(row):
#         # changing values after questions completed:
#
#         if not current_sheet[f'A{question+1}'].value in questions:
#             continue
#         # print(cell.value)
#         right_ind = 5+(id*2)
#         wrong_ind = right_ind + 1
#         if index == right_ind:
#             cell.value = questions[question+1]['right']
#         elif index == wrong_ind:
#             cell.value = questions[question+1]['wrong']
#
#         pass
#
# book.save('Questions/questions.xlsx')
# print(questions)

# --------------------------- text boxes -----------------------------------
# pygame.init()
#
# x, y = Window.x, Window.y
# os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"
#
# FPS = 60
# clock = pygame.time.Clock()
# window = Window.Display(new_window=True,caption='Question Display',size=(1000,500))
#
# class QuestionBox(Textbox):
#     LARGE_FONT = pygame.font.SysFont('Sans', 35)
#     MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
#     MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
#     SMALL_FONT = pygame.font.SysFont('Sans', 15)
#
#     def __init__(self, x, y, size, value, text='', font_size='MEDIUM'):
#         # inherit a few methods
#         # super().__init__(x, y)
#         # self.check_hover = Textbox.check_hover
#         # self.check_click = Textbox.check_click
#         self.value = value
#         self.x, self.y = x, y
#         self.rect = pygame.Rect(x, y, *size)
#         self.surface = pygame.Surface(self.rect.size)
#         self.background = Textbox.BACKGROUND
#         text_rect_size = [*map(lambda i: i*0.9,self.rect.size)] # create a padding for where the text will be placed
#         # calculate the offset of where the text rectangle will be placed
#         dx = (self.rect.w - text_rect_size[0])//2
#         dy = (self.rect.h - text_rect_size[1])//2
#         self.text_rect = pygame.Rect((self.rect.x + dx, self.rect.y + dy, *text_rect_size))
#         self.font = eval(f"self.{font_size}_FONT")
#         self.surf = None
#         self.text=text
#         self.border_color = None
#         self.add_text(text)
#
#     def show(self, surface):
#         # self.surface.fill(self.background)
#         pygame.draw.rect(self.surface, self.background, (0, 0, self.rect.w, self.rect.h))
#         if self.border_color: # if there is a border color
#             pygame.draw.rect(self.surface, self.border_color, (0, 0, self.rect.w, self.rect.h), 1)
#         # pygame.draw.rect(self.surface, self.border_color, (self.text_rect.x-self.rect.x, self.text_rect.y-self.rect.y, self.text_rect.w,self.text_rect.h),1)
#         surface.blit(self.surface,(self.rect.topleft))
#         if self.surf:
#             surface.blit(self.surf, self.text_rect.topleft)
#
#     def add_text(self, text, delay=False):
#         text = text.split() # split all the words
#         # modification variables
#         add_y = 0
#         widths = 0
#         # text variables
#         pointer = 0
#         letter_count = 0
#         height = self.font.render('h',1,(255,255,255)).get_rect().height
#         self.surf = pygame.Surface(self.text_rect.size, pygame.SRCALPHA, 32)
#         self.surf.convert_alpha()
#
#         if self.value == 'button' and len(text)==1:
#             rendered = self.font.render(text[0],1,(255,255,255))
#             self.surf.blit(rendered,(0,0))
#             return
#
#         while pointer <= len(text) - 1:
#             temp = self.surf.copy() # create a temporary surface where letters will be blitted
#             font_letters = []
#             for letter in text[pointer]:
#                 font_letters += [self.font.render(letter,1,(255,255,255))]
#
#             for letter in font_letters:
#                 rect = letter.get_rect()
#                 if not letter_count: # if the row has no letters
#                     proposed_x, proposed_y = 5, add_y * height
#                     letter_count+=1
#                     widths = 5
#                 else:
#                     proposed_x = widths
#                     proposed_y = add_y * height
#
#                     # if adding a character of a word will overflow, add the whole word to the next line
#                     if proposed_x + rect.w > self.text_rect.w:
#                         add_y += 1 # increasing the y
#                         widths = 1 # resetting the widths to 2
#                         letter_count = 0 # reset the letter count on the row
#                         break # repeat the process again for this word but on a new line
#
#                     # proposed_x = rect.x + widths
#                     # proposed_y = add_y * height
#
#                 temp.blit(letter, (proposed_x, proposed_y))
#                 widths += rect.w + 1 # +2 is for the padding after a letter has been added
#
#             else:
#                 if letter_count: # if there is a first character on the row
#                     # self.surf.blit(self.font.render('   ',1,(255,255,255)), (proposed_x, proposed_y))
#                     widths += 10 # this is the "space" between each word
#                 pointer += 1 # once a word has finished blitting, move onto the next one
#                 self.surf = temp.copy() # if a word was fully blitted, then add it onto the main canvas/surface
#
#     def check_hover(self, mouse_pos=0):
#         mouse_pos = pygame.mouse.get_pos()
#         if self.rect.collidepoint(mouse_pos):
#             self.background = self.hover_color
#             self.border_color = (0,0,255)
#             return 1
#         else:
#             self.background = self.background_color
#             self.border_color = None
#             return 0
#
#     def check_click(self, mouse_pos):
#         return self.rect.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])
#
#
# center = [*window.screen.get_rect().center]
# w, h = window.width, 200
# text = "Explain in detail as to why many users get so confused with many operating systems such as linux... is it because of the cmd?"
# question = QuestionBox(center[0]-w//2, 0 , (w, h*0.8),value='question', text=text)
#
# options = ['A','B','C','D']
# x1 = int(window.width*0.1//4)
# width = 0.9
#
# options = random.sample(options,4)
#
# option_1=QuestionBox(question.rect.x + x1, question.rect.bottom + 10, (w*width//2,(window.height-h)//2),value='a',text=a)
# option_2=QuestionBox(question.rect.center[0] + x1, question.rect.bottom + 10,(w*width//2,(window.height-h)//2),value='b',text=b)
# option_3=QuestionBox(option_1.rect.left,option_1.rect.bottom + 15,(w*width//2,(window.height-h)//2),value='c',text=c)
# option_4=QuestionBox(option_2.rect.left,option_2.rect.bottom + 15,(w*width//2,(window.height-h)//2),value='d',text=d)
# # question.add_text(text)
# # feedback = "The data bus retrieves data and instructions from main memory. The address bus sends addresses to main memory. The control bus sends read right signals to main memory"
# # feedback = "The program counter holds the memory location address of the next instruction to be performed by the central processing unit.  Memory data register holds the data that has been retrieved from memory, or that is about to be stored in memory. Accumulator holds the result of calculations and operations performed by the arithmetic and logic unit."
# feedback_text = 'nothing'
# feedback = QuestionBox(0,0,window.SIZE,text=feedback_text,value='feedback',font_size='MEDIUM')
# # continue_box = Textbox(0,int(0.8*window.height),text='Continue',size=(100,50))
# continue_button = Textbox(100,0.8*window.height,text='Continue',text_size='medlarge')
# display = True
#
# while 1:
#     window.refresh()
#     # continue_box.create_rect()
#     continue_button.create_rect()
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 pygame.quit()
#                 sys.exit()
#                 pass
#             if event.key == pygame.K_SPACE:
#                 display = False
#
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # print(a.check_click(pygame.mouse.get_pos())) # only check for click collision if need be
#             pass
#     if display:
#         question.show(window.screen)
#         for option in [option_1, option_2, option_3, option_4]:
#             option.show(window.screen)
#             option.check_hover()
#     else:
#         feedback.show(window.screen)
#         continue_button.check_hover(pygame.mouse.get_pos())
#         continue_button.show(window.screen,center = True)
#         if continue_button.check_click(pygame.mouse.get_pos()):
#             break
#
#     pygame.display.update()
#     clock.tick(FPS)
# ------------------------------------------------- STOPWATCH ------------------------------------------------
pygame.init()

x, y = Window.x, Window.y
os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = Window.Display(new_window=True,caption='Stopwatch',size=(200,160))
time1 = pygame.time.get_ticks()
timer=0
pause = False
y = 2
pause_button = boxes.AutoBox(190,60+y,(120,40),'pause','Pause',font_size=20)
reset_button = boxes.AutoBox(190,110+y,(120,40),'reset','Reset',font_size=20)
clicked=False

while 1:
    window.refresh()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = pause_button.check_click()
            if clicked:
                pause = not pause
            if reset_button.check_click():
                timer = 0

    if pygame.time.get_ticks() - time1 >= 1000:
        timer += 1*(not pause)
        time1 = pygame.time.get_ticks()

    time = Window.convert_time_format(timer)
    window.draw_text(time,(window.HEIGHT//2,y+18),center=(True,False),size='LARGE')
    if pause:
        window.draw_text('Paused',(window.HEIGHT//2, y),center=(True,False),size='SMALL',colour=(255,51,51))

    reset_button.show(window.screen, center=(True, False))
    reset_button.check_hover()

    pause_button.show(window.screen, center=(True, False))
    pause_button.check_hover()

    pygame.display.update()
    clock.tick(30)