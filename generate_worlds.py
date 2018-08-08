'''
A simple script for automatically generating minecraft worlds to find desirable spawns
'''
import abc
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

def check_world(checks=[], min_score = 1,remove_unused_chunks=True,print_info=True, **kwargs):
    def check_region(reg):
        important_chunks = {}
        check_count = 0
        reg_score = 0
        for chunk,key in zip(reg.chunks.values(),reg.chunks):
            if print_info and check_count % 10 == 0:
                print( '  chunk ' + str(check_count) + '/' + str(len(reg.chunks)) + '.' + str(chunk.coords) + '...')
            #print('see a chunk with palette', [i.name for i in chunk.palette.states])
            chunk_score = sum( (check.check(chunk) for check in checks) )
            if chunk in tuple((check.detections[-1] for check in checks if len(check.detections))):
                important_chunks[key] = chunk
            check_count += 1
        if remove_unused_chunks:
            reg.chunks = important_chunks
        reg_score += chunk_score
            
        return reg_score

                 ##for bcheck in block_checks:
                    ##score += sum((bcheck(block) for block in chunk.blocks.values()))
    
    score = 0
    #region_dir = mc_dir +"\\saves\\" + name + '\\region'
    #print(region_dir)
    regions = []
    if 'save_name' in kwargs:
        region_dir = mc_dir +"\\saves\\" + kwargs['save_name'] + '\\region'
        for region_file in os.listdir(region_dir):
            if region_file.startswith('r.') and regionFile.endswith('.mca'):
                new_region = Region(region_dir + '\\' + region_file,print_info=print_info)
            score += check_region(new_region)
            regions.append(new_region)
    elif 'regions' in kwargs:
        for new_region in kwargs['regions']:
            score += check_region(new_region)
            regions.append(new_region)
          
    print(score)
    return regions
            
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



def dist(pnt1,pnt2):
    '''
    return squared distance between two 3d points
    '''
    return m.sqrt(sum([(pnt1[i]-pnt2[i])**2 for i in range(len(pnt1))]))

class landmark_scorer(object):
    '''
    used to check for instances of a landmark and decide how they should be scored
    '''
    def __init__(self,score,max_score=float('inf'),multiplier = 1,min_dist=0): #,max_dist=float('inf')
        self.max_score = max_score
        self.min_dist = min_dist
        #self.max_dist = max_dist
        self.scored = 0
        self.score = score
        self.multiplier = multiplier
        self.detections = []

    @abc.abstractmethod
    def check(self,to_check): pass

    def get_next_score(self,coords=None):
        print('get next score',coords)
        if coords and self.get_min_dist(coords) < self.min_dist: return 0
        new_score = self.score * self.multiplier ** len(self.detections)
        new_score = min(new_score,self.max_score - self.scored)
        self.scored += new_score
        return new_score

    def get_min_dist(self,coords):    
        min_dist = float('inf')
        for d in self.detections:
            #print('dist',d.coords,coords)
            new_dist = dist(d.coords,coords)
            min_dist = min(new_dist,min_dist)
        return min_dist

    def __repr__(self):
        return (type(self).__name__ + '\n  detections:' + str(len(self.detections)) + '\n  score:' + str(self.scored)  )

class find_village(landmark_scorer):
    def check(self,chunk):
        #print('village check')
        if b'minecraft:torch' in [s.name for s in chunk.palette.states] or b'minecraft:wall_torch' in [s.name for s in chunk.palette.states]:
            for block in chunk.y_range(55,90):#search for lit building above ground
                if block.name in (b'minecraft:torch',b'minecraft:wall_torch'):
                    #print('found tourch', block.coords)
                    for dy in range(35):
                        above = block.above(dy)
                        #print('  ','nne' if not above else (above.name,above.coords))
                        if above and above.name in \
                        (b'minecraft:stone',b'minecraft:dirt',b'minecraft:sand',b'minecraft:gravel',b'minecraft:andesite',b'minecraft:coal_ore',b'minecraft:diorite' ):
                            break
                    else:
                        print('  found village')
                        score = self.get_next_score(chunk.coords)
                        self.detections.append(chunk)
                        return score
        return 0

class find_ocean(landmark_scorer):
    def check(self,chunk):
        for block in chunk.y_range(41,48,8,dh=8):
            if block.name != b'minecraft:water':
                break
        else:
            if (4,60,4) in chunk.blocks and chunk.blocks[(4,60,4)].name == b'minecraft:water' and \
               (4,64,4) in chunk.blocks and chunk.blocks[(4,64,4)].name == b'minecraft:air':
                print('  found ocean')
                score = self.get_next_score(chunk.coords)
                self.detections.append(chunk)
                return score
        return 0

class find_jungle(landmark_scorer):
    def check(self,chunk):
        if b'minecraft:jungle_leaves' in [s.name for s in chunk.palette.states]:
            for block in chunk.y_range(65,80,1,dh=2):
                if block.name == b'minecraft:jungle_wood':
                    if block.above(1).name == b'minecraft:jungle_leaves':
                        print('  found jungle')
                        score = self.get_next_score(chunk.coords)
                        self.detections.append(chunk)
                        return score
        return 0

class find_mineshaft(landmark_scorer):
    def check(self,chunk):
        if b'_fence' in [s.name[-6:] for s in chunk.palette.states if s.name]:
            for block in chunk.y_range(10,65,2,dh=3):
                if block.name and block.name[-6:] == b'_fence' and block.above(1).name and block.above(1).name[-7:] == b'_planks':
                    print('  found mineshaft')
                    score = self.get_next_score(chunk.coords)
                    self.detections.append(chunk)
                    return score
        return 0
        
class find_spawner(landmark_scorer):
    def __init__(self,*args, **kwargs):
        self.include_cave_spider = False
        landmark_scorer.__init__(self,*args,**kwargs)
        
    def check(self,chunk):
        if b'minecraft:spawner' in [s.name for s in chunk.palette.states]:
            print('  found spawner')
            score = self.get_next_score(chunk.coords)
            self.detections.append(chunk)
            return score
        return 0




#

if __name__ == '__main__':

    f_village = find_village(20, max_score=70, multiplier=1.1, min_dist = 8)
    f_ocean = find_ocean(300,max_score = 300,min_dist = float('inf'))
    f_spawner = find_spawner(20,max_score = 120,multiplier = 1.5)
    f_mineshaft = find_mineshaft(300,max_score = 500,min_dist = 20)
    f_jungle = find_jungle(300,max_score = 300,min_dist = 20)
    
    ### use all regions
    #r = check_world(save_name='w1' ,checks=[f_village,f_ocean,f_spawner,f_mineshaft,f_jungle])

    ### select specific chunks
    r = Region('C:\\Users\\Trevor\\AppData\\Roaming\\.minecraft\\saves\\w1\\region\\r.-1.-1.mca',print_info=True) #
    check_world(regions=[r] ,checks=[f_village,f_ocean,f_spawner,f_mineshaft,f_jungle])

### SCRAPS BELOW
### SCRAPS BELOW
############################################

#for f in [f_village,f_ocean,f_spawner,f_mineshaft,f_jungle]:
#    print(repr(f))
#

'''def get_score(block):
        if block.name in ('minecraft:torch','minecraft:wall_torch') and block.coords[1] > 55:
            for i in range(40):
                if block.chunk.blocks[(block.coords[0],block,coords[1]+i,block.coords[2])] in ('minecraft:stone','minecraft:dirt'):
                    break
                else:
                    bonus = self.score * multiplier ** len(detections)
                    self.detections.append(block.chunk.coords)
                    return bonus

class find_ocean(object):
    def '''

'''def find_sunken_boat(chunk):
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
                        if expected_blocks > 59 - cy - 4 > 10: return 100'''

#find_underwater_ravine.found = False
'''
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
find_underwater_boat_near_ravine.found = False    '''

#for i in range(5,44):
#   #score,max_score=None,multiplier = 1,min_dist=float('inf')
'''create_world(' num ' + str(i), 90)
    time.sleep(8)
    check = check_world('New World num ' + str(i),checks=[f_village,f_ocean,f_spawner,f_mineshaft,f_jungle])
    if not check:
        print('FAIL')
        #delete_last_world()
    else:
        print('PASS',check )
    find_underwater_boat_near_ravine.found = False
    find_jungle_wood.found = False'''



#+ str(i)

