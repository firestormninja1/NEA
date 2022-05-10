import pygame
import pygame.freetype
import os, sys, json, re

x,y = 50,80


os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"
from _ctypes import PyObj_FromPtr
# https://stackoverflow.com/questions/42710879/write-two-dimensional-list-to-json-file for adding lists to json no indent
# --------------- modules to add lists/tuples to .json without indentation ---------------------- #
class NoIndent(object):
    """ Value wrapper. """
    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError('Only lists and tuples can be wrapped')
        self.value = value

class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {'cls', 'indent'}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(MyEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                    else super(MyEncoder, self).default(obj))

    def iterencode(self, obj, **kwargs):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(MyEncoder, self).iterencode(obj, **kwargs):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = PyObj_FromPtr(id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                            '"{}"'.format(format_spec.format(id)), json_repr)

            yield encoded

class StopRunning(Exception):
    """raised to display an error message about something and stop execution. Avoiding print statements"""
    pass
def get_path(path):
    absolute_path = os.path.abspath(path)
    if os.path.exists(absolute_path):
        return absolute_path
    else:
        raise FileNotFoundError

def read_json(path):
    details = get_path(path)
    with open(details, 'r') as file:
        return json.load(file)

def write_json(data, path, cls=MyEncoder):
    details_path = get_path(path)

    # re-assigning any lists to NoIndent instances
    for detail in data:
        for thing in data[detail]:
            if type(data[detail][thing]) == list and thing!='options': # so options can be visually seen
                data[detail][thing] = NoIndent(data[detail][thing]) # if its any other thing that's list format, ie points or right-wrong

    with open(details_path, 'w') as file:
        file.seek(0)
        json.dump(data, file, indent=4, cls=cls)

def convert_time_format(time):
    h, r = divmod(time, 3600) # calculate how many hours, and the remainder is the number of minutes (in seconds)
    m, s = divmod(r, 60) # convert the remaining seconds into minutes, and the remainder is the amount of seconds
    return f'{h:02}:{m:02}:{s:02}' # format each value by filling in missing number(s) of maximum 2 numbers with leading 0s.

def delete_json_key(path, cls=MyEncoder, key=None, depth=1):
    details_path = get_path(path)
    data = read_json(details_path)
    for key1 in data:
        if depth==2:
            for key2 in data[key1]:
                if key2 == key:
                    del data[key1][key2]
                    break # go onto next main key
        elif depth==1:
            if key1==key:
                del data[key1]
                break

    write_json(data, path)

def delete_user(username):
    # To remove a user and maintain referential integrity by deleting all records of the user everywhere.
    for file in os.listdir('Questions'):
        delete_json_key(f'Questions/{file}', key=username, depth=2)
    delete_json_key(f'users.json',key=username)

def delete_users():
    users = read_json('users.json')
    for user in users:
        delete_user(user)

def bubble_sort2D(array) -> list: # sort a 2D array
    # We want to stop passing through the list
    # as soon as we pass through without swapping any elements
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(array) - 1):
            if array[i][1] < array[i+1][1]: # comparing the key index, can be points or accuracy
                array[i], array[i+1] = array[i+1], array[i]
                swapped = True
    return array # return the sorted 2D array

class Display:
    pygame.init()
    RED = (255,0,0)
    BLUE = (168, 193, 255)
    WHITE = (255,255,255)
    GREY = (80,80,80)
    BLACK = (0,0,0)
    BACKGROUND = (34,40,44)
    ORANGE = (255,215,0)
    GREEN = BACKGROUND

    TILE_DIMENSION_X,TILE_DIMENSION_Y = 46,46
    BLOCKS_X,BLOCKS_Y = 31,15 # game window resolution
    WIDTH,HEIGHT = int(BLOCKS_X * TILE_DIMENSION_X), int(BLOCKS_Y * TILE_DIMENSION_Y)
    SIZE = (WIDTH, HEIGHT)

    MAX_BLOCKS_X = 112
    MAX_BLOCKS_Y = 25

    LARGE_FONT = pygame.font.SysFont('Sans', 35)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
    MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
    SMALL_FONT = pygame.font.SysFont('Sans', 20)

    BACK_X, BACK_Y = 10, 15 # default position of back arrow

    def __init__(self, background=GREEN, caption='Game', size=SIZE, new_window=True, back_pos=None):
        self.SIZE = size
        self.WIDTH, self.HEIGHT = size
        self.width, self.height = size

        self.BACK_X, self.BACK_Y = (10,10)
        if back_pos is not None:
            self.BACK_X, self.BACK_Y = back_pos

        self.screen = pygame.display.set_mode(self.SIZE)
        if new_window:
            pygame.display.set_caption(caption)

        self.background=background
        self.back_image = pygame.transform.scale(pygame.image.load(get_path('images/go_back.png')), (100, 38))
        self.back_rect = pygame.Rect(self.BACK_X, self.BACK_Y, *self.back_image.get_size())

    def draw_back(self, pos=None):
        if pos is None:
            pos = (self.BACK_X, self.BACK_Y)
        self.back_rect = pygame.Rect(*pos, *self.back_image.get_size())
        # pos = (self.BACK_X, self.BACK_Y)
        # self.back_rect = pygame.Rect(*pos,*self.back_image.get_size())
        self.screen.blit(self.back_image,pos)
        pygame.draw.rect(self.screen, self.BLUE, (*pos,*self.back_image.get_size()),2)

    def refresh(self, back=False, pos=None, show_mouse_pos=False):
        if isinstance(self.background, tuple): # if the background is a colour
            self.screen.fill(self.background)
        else: # if its an image
            self.screen.blit(self.background,(0,0))
        if back:
            self.draw_back(pos)

        if show_mouse_pos:
            mouse_pos = self.MEDIUM_FONT.render(str(pygame.mouse.get_pos()),1,self.WHITE)
            rect = mouse_pos.get_rect()
            self.screen.blit(mouse_pos,((self.WIDTH-rect.w)//2,0))

    def check_return(self, mouse_pos=None):
        if not mouse_pos:
            mouse_pos = pygame.mouse.get_pos()

        if self.back_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            return 1

    def draw_text(self,text,pos,size='MEDIUM',colour=WHITE, center=(False, False),underline=False):
        center_x, center_y = center
        text = eval(f'self.{size.upper()}_FONT.render(text, True, colour)')
        rec=text.get_rect()
        x, y = pos
        if center_x:
            x = (self.WIDTH-rec.w)//2
        if center_y:
            y = (self.HEIGHT-rec.h)//2
        self.screen.blit(text,(x,y))
        if underline:
            pygame.draw.line(self.screen, (colour), (x, y + rec.h,), (x + rec.w, y + rec.h),2)


