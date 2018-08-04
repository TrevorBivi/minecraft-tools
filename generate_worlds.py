'''
A simple script for automatically generating minecraft worlds to find desirable spawns
'''

import os
import cv2
import numpy as np
from PIL import ImageGrab as iGrab
from matplotlib import pyplot as plt
import time
import pyautogui as pag
from read_save_file import *
#from player_actions import press
#import win32gui
#import win32con
#import win32api

#window = win32gui.FindWindow(None,"Minecraft 1.13")
#print(window)

mc_dir = 'C:\\Users\\Trevor\\AppData\\Roaming\\.minecraft'

button_back_to_server_list = cv2.imread('imgs\\button_back_to_server_list.png',cv2.IMREAD_UNCHANGED)
button_cancel = cv2.imread('imgs\\button_cancel.png',cv2.IMREAD_UNCHANGED)
button_singleplayer = cv2.imread('imgs\\button_singleplayer.png',cv2.IMREAD_UNCHANGED)
button_create_world = cv2.imread('imgs\\button_create_new_world.png',cv2.IMREAD_UNCHANGED)
button_save_and_quit = cv2.imread('imgs\\button_save_and_quit_to_title.png',cv2.IMREAD_UNCHANGED)
button_delete = cv2.imread('imgs\\button_delete.png',cv2.IMREAD_UNCHANGED)
text_new_world = cv2.imread('imgs\\text_new_world.png',cv2.IMREAD_UNCHANGED)
text_select_world = cv2.imread('imgs\\text_select_world.png',cv2.IMREAD_UNCHANGED)
masked_text_select_world = cv2.imread('imgs\\masked_text_select_world.png',cv2.IMREAD_UNCHANGED)

#virtual key codes for keyboard events
'''key_codes = {'backspace':0x08,
           'tab':0x09,
           'enter':0x0D,
           'shift':0x10,
           'ctrl':0x11,
           'alt':0x12,
           'pause':0x13,
           'caps_lock':0x14,
           'esc':0x1B,
           ' ':0x20,
           'page_up':0x21,
           'page_down':0x22,
           'end':0x23,
           'home':0x24,
           'left_arrow':0x25,
           'up_arrow':0x26,
           'right_arrow':0x27,
           'down_arrow':0x28,
           'print_screen':0x2C,
           'ins':0x2D,
           'del':0x2E,
           '0':0x30,
           '1':0x31,
           '2':0x32,
           '3':0x33,
           '4':0x34,
           '5':0x35,
           '6':0x36,
           '7':0x37,
           '8':0x38,
           '9':0x39,
           'a':0x41,
           'b':0x42,
           'c':0x43,
           'd':0x44,
           'e':0x45,
           'f':0x46,
           'g':0x47,
           'h':0x48,
           'i':0x49,
           'j':0x4A,
           'k':0x4B,
           'l':0x4C,
           'm':0x4D,
           'n':0x4E,
           'o':0x4F,
           'p':0x50,
           'q':0x51,
           'r':0x52,
           's':0x53,
           't':0x54,
           'u':0x55,
           'v':0x56,
           'w':0x57,
           'x':0x58,
           'y':0x59,
           'z':0x5A,
           'F1':0x70,
           'F2':0x71,
           'F3':0x72,
           'F4':0x73,
           'F5':0x74,
           'F6':0x75,
           'F7':0x76,
           'F8':0x77,
           'F9':0x78,
           'F10':0x79,
           'F11':0x7A,
           'F12':0x7B,
           'num_lock':0x90,
           'scroll_lock':0x91,
           'left_shift':0xA0,
           'right_shift ':0xA1,
           'left_control':0xA2,
           'right_control':0xA3,
           '=':0xBB,
           ',':0xBC,
           '-':0xBD,
           '.':0xBE,
           '/':0xBF,
           '`':0xC0,
           ';':0xBA,
           '[':0xDB,
           '\\':0xDC,
           ']':0xDD,
           "'":0xDE,
}'''
'''
def key_dwn(key=None):
        win32gui.SendMessage(window,#win handle
                             win32con.WM_KEYDOWN,#msg
                             key_codes[key],
                             0) # all 0 flags is fine

def key_up(key=None):
    if key:
        win32gui.SendMessage(window,
                             win32con.WM_KEYUP,
                             key_codes[key],
                             0xC0000000) # previous key state and transition state flags must be 1

def press(key,press_time=0.05):
    key_dwn(key)
    time.sleep(press_time)
    key_up(key)'''


def screenshot(box = None):
    '''return image at given box on screen
    Keyword arguments:
    box -- box to target on screen (default None)
    target_game_window -- target inside the game window instead of whole screen (default True)
    '''
    img = iGrab.grab(box)
    cv_im =  cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return cv_im

def match_template(image,template,min_match=-1,error=False):
    '''returns top left position of best match for image 
    Keyword arguments:
    image -- the image template is inside
    template -- the image to find inside of image
    min_match -- minimum match before fail 0.0-1.0 (default -1.0)
    error -- if fail, raise error instead of return none (default = False)
    '''
    #setup mask layer
    mask = None
    if template.shape[2] == 4:
        t_channels = cv2.split(template)
        template = cv2.merge(t_channels[:3])
        mask = cv2.merge([t_channels[3]]*3)
    
    match = cv2.minMaxLoc(cv2.matchTemplate(image, template ,cv2.TM_CCORR_NORMED,mask=mask))
    if min_match > match[1]:
        if error:
            raise ValueError("failed to match a template")
        return None

    return match[3],match[1]
#win32api.SetCursorPos( (round(dy),round(dx)) )

def press(key,wait=0.1):
    pag.keyDown(key)
    time.sleep(wait)
    pag.keyUp(key)

def create_world(name,generation_time):
    view = screenshot()
    button,acc = match_template(view,button_singleplayer)
    print(button,acc)
    if acc > 0.97:
        pag.click(button)
        time.sleep(1)
        view = screenshot()
    button,acc = match_template(view,button_create_world)
    pag.click(button)
    time.sleep(1)
    view = screenshot()
    button,acc = match_template(view,text_new_world)
    pag.click(button[0]+300, button[1])
    pag.typewrite(name)
    button,acc = match_template(view,button_create_world)
    pag.click(button)
    
    time.sleep(generation_time)
    pag.hotkey('alt','tab')
    time.sleep(3)
    button,acc = match_template(screenshot(),button_save_and_quit)
    pag.click(button)
    time.sleep(1)

def check_world(name, chunk_checks = [], block_checks = [], min_score = 1):
    score = 0
    region_dir = mc_dir +"\\saves\\" + name + '\\region'
    print(region_dir)
    for regionFile in os.listdir(region_dir):
        if regionFile.startswith('r.') and regionFile.endswith('.mca'):
            region = Region(region_dir + '\\' + regionFile)
            for chunk in region.chunks.values():
                #print('see a chunk with palette', [i.name for i in chunk.palette.states])
                score += sum( (ccheck(chunk) for ccheck in chunk_checks) )
                for bcheck in block_checks:
                    score += sum((bcheck(block) for block in chunk.blocks.values()))
    print(score)
    if score > min_score:
        return True
            
def delete_last_world():
    view = screenshot()
    button,acc = match_template(view,button_singleplayer)
    if acc > 0.97:
        pag.click(button)
        time.sleep(1)
    button,acc = match_template(view,masked_text_select_world)
    
    pag.click( (button[0], button[1] + 70) )
    for i in range(2):
        time.sleep(1)
        button,acc = match_template(screenshot(),button_delete)
        pag.click(button)

#input('enter to start')
#time.sleep(4)

def find_underwater_ravine(chunk,ignore_found=False,known_neighbour=False):
    #def notRavineException(Exception):pass
    #try:
                                 
    if not find_underwater_ravine.found or ignore_found:
        for dx in range(5,16,4):
            for dz in range(5,16,4):
                for y in range(20,60):
                    if (dz,y,dx) in chunk.blocks and chunk.blocks[(dz,y,dz)].name != b'minecraft:water': break
                else:
                    if known_neighbour: return 100
                        
                    for i in range(-1,2,2):
                        for j in range(-1,2,2):
                            neighbour_coords = (chunk.coords[0] + i, chunk.coords[1] + j)
                            if neighbour_coords in chunk.region.chunks and find_underwater_ravine(chunk.region.chunks[neighbour_coords],ignore_found=True,known_neighbour=True):
                                if not ignore_found: find_underwater_ravine.found = True
                                return 100
                    return 0
    return 0
find_underwater_ravine.found = False

def find_sunken_boat(chunk):
    for y in range(20,50):
        for dx in range(16):
            for dz in range(16):
                if (dx,y,dz) in chunk.blocks and chunk.blocks[(dx,y,dz)].name == b'minecraft:chest':
                    expected_blocks = 0
                    for cy in range(y,51):
                        if chunk.blocks[(dx,cy,dz)].name and chunk.blocks[(dx,cy,dz)].name[-5:] in (b'water',b'lanks',b'tairs',b'fence',b'_slab'):
                            expected_blocks += 1
                        elif chunk.blocks[(dx,cy,dz)].name == b'minecraft:stone':
                            expected_blocks = 0
                            break;
                    else:
                        if expected_blocks > 59 - cy - 4 > 10: return 100
    return 0
#find_underwater_ravine.found = False

def find_underwater_boat_near_ravine(chunk,ignore_found=False):
    if not find_underwater_boat_near_ravine.found or ignore_found:
        if find_sunken_boat(chunk):
            for i in range(-2,3):
                for j in range(-2,3):
                    new_coords = (chunk.coords[0] + i, chunk.coords[1] + j)
                    new_chunk = chunk.region.chunks[new_coords] if new_coords in chunk.region.chunks else None
                    
                    if new_chunk and find_underwater_ravine(chunk,ignore_found=True):
                        if not ignore_found: find_underwater_boat_near_ravine.found = True
                        return 100
    return 0
    #except notRavineException:pass
find_underwater_boat_near_ravine.found = False    
                                 
def find_jungle_wood(block):
    if not find_jungle_wood.found and block.name == b'minecraft:jungle_wood':
        find_jungle_wood.found = True
        return 10
    return 0
find_jungle_wood.found = False

for i in range(5,44):
    create_world(' num ' + str(i), 90)
    time.sleep(8)
    check = check_world('New World num ' + str(i),chunk_checks=[find_underwater_boat_near_ravine],block_checks=[find_jungle_wood])
    if not check:
        print('FAIL')
        #delete_last_world()
    else:
        print('PASS',check )
    find_underwater_boat_near_ravine.found = False
    find_jungle_wood.found = False

