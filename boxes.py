import pygame,os,Window
import pygame.freetype
pygame.init()
from Window import StopRunning
pygame.freetype.init()
x,y = Window.x,Window.y
os.environ['SDL_VIDEO_Window_POS'] = f"{x},{y}"
Display = Window.Display

class Textbox(Window.Display):
    rect: object
    default_background = (68, 71, 68)
    default_border = (207, 234, 255)
    default_hover = (85, 155, 251)
    text_colour = (255, 255, 255)
    default_border_hover = (255,255,255)
    background_colour = default_background
    border_colour = default_border
    hover_colour = default_hover
    text_colour = text_colour
    border_hover = default_border_hover
    GREEN = (0,200,0)

    max_width = 270

    def __init__(self, x, y, text='', text_size='MEDIUM', text_colour=text_colour, padding=(0,0), size=(0,0),limit=True):
        self.padding = padding
        self.size = size
        self.text = text
        self.text_size = eval('self.' + text_size.upper()+'_FONT')
        self.x, self.y = x, y
        self.text_colour = text_colour
        self.limit = limit
        self.create_rect()

    def create_rect(self):
        padding_x,padding_y = self.padding

        w,h=self.size

        #updates the text to be displayed on the box
        self.rendered_text = self.text_size.render(self.text, True, self.text_colour)

        self.rect = self.rendered_text.get_rect() # this is the font rectangle
        tempRect = self.rect.copy()
        tempRect.width = tempRect.width + padding_x
        if self.limit:
            tempRect.width = min(270, tempRect.width +padding_x)
        tempRect.height = tempRect.height + padding_y
        self.main_rec = tempRect # font rectangle with padding, the outside rectangle

        if w>0 and h>0: # if a specified size was passed in
            if self.main_rec.width - 43 < w:
                self.main_rec.width = w + padding_x
            self.main_rec.height = h + padding_y

        self.surface = pygame.Surface((self.main_rec.width, self.main_rec.height))
        self.background = self.background_colour
        # self.main_rec.topleft = (self.x,s/elf.y)


    def show(self, canvas, center=False):
        pygame.draw.rect(self.surface, self.background, self.main_rec)
        pygame.draw.rect(self.surface, self.border_colour, self.main_rec, 3)
        text_x = (self.main_rec.width - self.rect.width) // 2
        text_y = (self.main_rec.height - self.rect.height) // 2
        self.surface.blit(self.rendered_text, (text_x, text_y))

        if center:
            self.x = (canvas.get_width() - self.main_rec.width)//2 # center it

        canvas.blit(self.surface, (self.x, self.y)) # blitting the box at the initially specified x and y position

    def set_properties(self, background=background_colour, border=border_colour, hover=hover_colour):
        self.background = background
        self.border_colour = border
        self.hover_colour = hover

    def check_hover(self,mouse_pos=0):
        mouse_pos = pygame.mouse.get_pos()
        x=self.main_rec.copy()
        x.x = self.x
        x.y = self.y
        if x.collidepoint(mouse_pos):
            self.background = self.hover_colour
            # self.border_colour = self.BACKGROUND
        else:
            self.background = self.background_colour
            # self.border_colour = self.default_border

    def check_click(self,mouse_pos=None):
        x=self.main_rec.copy()
        x.x = self.x
        x.y = self.y
        return x.collidepoint(pygame.mouse.get_pos()) and (pygame.mouse.get_pressed()[0])

# noinspection PyArgumentList
class AutoBox(Textbox):
    default_background = Textbox.default_background
    incorrect_colour = (204, 51, 0)
    correct_colour = (51, 153, 51)
    hover_colour = (65, 114, 191)
    hover_border = (207, 234, 255)
    border_radius = 2

    def __init__(self, x, y, size, obj_type, text='', font_size='MEDIUM',center_text=(True,True),colour=default_background):
        self.background_colour = colour
        self.border_colour = None

        if isinstance(font_size, int): # if a custom font size is passed in
            self.font = pygame.font.SysFont('Sans', font_size)

        elif font_size.upper() in 'MEDIUM LARGE MEDLARGE SMALL'.split():
            self.font = eval(f'self.{font_size}_FONT')

        else:
            StopRunning('Invalid text size passed in')

        self.obj_type = obj_type
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, *size)
        self.surface = pygame.Surface(self.rect.size)
        text_rect_size = [0.9*self.rect.w,0.9*self.rect.h] # create a padding for where the text will be placed

        # calculate the offset to place the text rectangle in the center of the main box rectangle
        self.dx = (self.rect.w - text_rect_size[0])//2
        self.dy = (self.rect.h - text_rect_size[1])//2
        self.text_rect = pygame.Rect((self.rect.x + self.dx, self.rect.y + self.dy, *text_rect_size))
        self.surf = None
        self.text=text
        self.center_text = center_text
        self.add_text(text)
        self.background = self.background_colour
        self.check_collision = True

    def show(self, surface, center=(False,False)):
        self.surface.fill(self.background)
        center_x,center_y = center
        # if self.background: pygame.draw.rect(self.surface, self.background, (0, 0, self.rect.w, self.rect.h))
        if self.border_colour: # if there is a border colour
            pygame.draw.rect(self.surface, self.border_colour, (0, 0, self.rect.w, self.rect.h), self.border_radius)

        x, y = self.dx, 0
        if self.center_text[0]:
            x = (self.rect.w-self.text_rect.w)//2
        if self.center_text[1]:
            y = (self.rect.h-self.text_rect.h)//2
        self.surface.blit(self.surf, (x, y, self.text_rect.w, self.text_rect.h))
        # blit everything onto the specified surface
        if center_x: self.x = (surface.get_width() - self.rect.w)//2
        if center_y: self.y = (surface.get_height() - self.rect.h)//2
        self.rect.topleft = (self.x, self.y)
        surface.blit(self.surface, self.rect.topleft)

    # this allows text to fit in a box.
    def add_text(self, text):
        """
        \\n = newline
        break up the text and try to blit each word individually; if at any point any of the letters for a word goes out,
        then repeat the blit attempt process for the word again but on a new line/y-coordinate. However, if there is only
        one word (left in the text) and it doesn't fit, trying to add to a new y value would cause the same issue, therefore
        if this does occur, don't try to add that word forever, just break out of the loop and if the word is missing, the user
        should know that it couldn't fit in the box.
        """
        text = text.strip()
        text = text.strip().split() # remove the white spaces on the left and right sides and split all the words
        # modification variables
        add_y = 0
        widths = 0
        # text variables
        pointer = 0
        letter_count = 0
        height = self.font.render('h',1,(255,255,255)).get_height()
        self.surf = pygame.Surface(self.text_rect.size, pygame.SRCALPHA, 32)
        self.surf.convert_alpha()

        if self.obj_type == 'button' and len(text)==1:
            rendered = self.font.render(text[0],1,(255,255,255))
            self.surf.blit(rendered,(0,0))
            return

        # to evaluate: this can go on forever if the box is too small for all of the text to fit in
        break_while = False
        last_word_attempt = 0
        max_x = 0
        while pointer <= len(text) - 1:
            current_word = text[pointer]
            if last_word_attempt > 2: # if 2 new line attempts have been made then it means the word still cannot fit
                # break out of the while loop and stop attempting to infinitely trying to add the word
                break
            temp = self.surf.copy() # create a temporary surface where letters will be blitted
            font_letters = []

            for letter in current_word:
                font_letters += [self.font.render(letter, 1, (255, 255, 255))]

            for index,letter in enumerate(font_letters): # iterating through each rendered letter
                newline = False

                rect = letter.get_rect()
                if not letter_count: # if the row has no letters (if its the first letter)
                    proposed_x, proposed_y = 0, add_y * height
                    letter_count += 1
                    widths = 0 # initial padding from the side of rectangle
                else:
                    proposed_x = widths # sum all the widths + padding of previous letters
                    proposed_y = add_y * height
                    # if adding a character of a word will overflow, add the whole word to the next line
                    if proposed_x + rect.w > self.text_rect.w:
                        newline = True

                if newline or current_word == '\\n':
                    max_x = max(max_x, min(self.text_rect.w, proposed_x+rect.w))
                    add_y += 1 # increasing the y
                    widths = 1 # resetting the widths to 1
                    letter_count = 0 # reset the letter count on the row
                    if pointer == len(text)-1: # if its the last word and still not fitting
                        last_word_attempt += 1
                    if current_word == '\\n':
                        pointer += 1
                    break # repeat the process again for this word but on a new line
                max_x = max(max_x, min(self.text_rect.w, proposed_x+rect.w))

                temp.blit(letter, (proposed_x, proposed_y)) # blit it on the temp surface
                widths += rect.w + 1 # +1 is for the padding between letters

            else: # if the loop finished iterating meaning that all letters were successfully blitted
                if letter_count: # if there is a first character on the row
                    # self.surf.blit(self.font.render('   ',1,(255,255,255)), (proposed_x, proposed_y))
                    widths += self.font.render(' ',1,(255,255,255)).get_width()# this is the "space" between each word
                pointer += 1 # once a word has finished blitting, move onto the next one
                self.surf = temp.copy() # if a word was fully blitted, then add it onto the main canvas/surface of this box

        self.text_rect.h = (add_y+1) * height
        self.text_rect.w = max_x

    def update_text(self, text):
        self.add_text(text)

    def check_hover(self, mouse_pos=0):
        self.surface.set_alpha(220)
        # if the mouse position is over the rectangle, change colour, otherwise change it back to normal
        if self.obj_type != 'question':
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and self.check_collision:
                self.background = self.hover_colour
                self.border_colour = self.hover_border
            else:
                self.background = self.background_colour
                self.border_colour = None

    def check_click(self, mouse_pos=0):
        if (not self.check_collision) or (self.obj_type == 'question'): return
        mouse_pos = pygame.mouse.get_pos()
        self.rect.x = self.x; self.rect.y = self.y
        if self.rect.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0]):
            return self


class BoxGroup:
    def __init__(self, *args):
        self.objects = [*args]

    def update_boxes(self, surface):
        box_clicked = False
        for box in self.objects:
            if hasattr(box, 'show'):
                box.show(surface)
            if hasattr(box, 'check_hover') and box.check_collision:
                box.check_hover()
            if hasattr(box, 'check_click') and not box_clicked:  # if a box hasn't already been clicked
                if box.check_click():
                    box_clicked = True # a box has been clicked

    def check_clicks(self):
        box_clicked = False
        for box in self.objects:
            if hasattr(box, 'check_click') and not box_clicked:
                if box.check_click():
                    box_clicked = box
        return box_clicked

    def get_list(self):
        return self.objects
