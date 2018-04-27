'''
ABOUT:
generates a board object that represents an image

IMPORTANT CLASSES:
board -- represents an image

         Init Keyword Arguments:
         img -- the image to represent (default None (gui select))
         tether -- allow checkerboard tethering (default False)
         pallet_group -- the color pallet being used (default pallet_groups["bw"])
         build dir -- z direction of column building (default 1)
         
         Important Variables:
         board.width -- width of board in pixels
         board.height -- height of board in pixels
         board.pallet -- the color pallet used to represent image
         board.build_dir -- the direction the image is to be built in game
         board.pxl_dat -- the bext color pallet color chosen to represent each pixel

         Important Functions
         board.save -- function to save what the board looks like as an image
         build_inf -- return information about how to place board pixel in game

REQUIREMENTS:
- must use creative mode
'''

import tkinter as tk
import tkinter.filedialog
from PIL import Image
import os

# a pallet group is a group of blocks that make of a color pallet for a board
# the player can place blocks in an upwards direction to increase the amount of color
# options using beveling on maps - which adjusts a tile's color based on it's height relative
#to the place at z+1.
pallet_groups = {
"bw":{
    "names":(
    "black wool",
    "grey wool",
    "cobblestone",
    "light grey wool",
    "white wool"
    ),
        
    1:(#place col in increasing z direction
    
    (21,21,21),#black wool   - normal value
    (25,25,25),#             bevel value

    (52,52,52),
    (64,64,64),
    #grey wool

    (75,75,75),#cobble stone
    (77,77,77),

    (106,106,106),
    (129,129,129),#light grey wool
    

    (216,216,216),#white wool
    (250,250,250),
    ),

    -1:(#place col in decreasing z direction
    (17,17,17),#               beveled value
    (21,21,21),#black wool - normal value
    

    (64,64,64),#grey wool
    (75,75,75), 

    (94,94,94),#cobble stone
    (110,110,110),

    (129,129,129),#light grey wool
    (150,150,150),

    (176,176,176),
    (216,216,216),#white wool
    
    )
},

}

def get_file():
    '''
    return a file object selected by the user
    '''
    return Image.open(tk.filedialog.askopenfilename())

def mid_pnt(pnt1,pnt2):
    '''
    return point at the middle of two 3d points
    '''
    return [(pnt1[i] + pnt2[i])/2 for i in range(3)]

def sq_dist(pnt1,pnt2):
    '''
    return squared distance between two 3d points
    '''
    return sum([(pnt1[i]-pnt2[i])**2 for i in range(3)])

def best_col(pxl,pallet, tether_xy = None):
    '''
    find the id of the best color for pixel

    Keyword Arguments:
    pxl -- the rgb pixel
    tether_coords -- coords of pxl to allow checkerboard tethering (default None)
    '''
    best_col = -1
    best_dist = 9999999
    for c,c_val in enumerate(pallet):

        #check if new color is better
        new_dist = sq_dist(pxl,c_val)
        if(new_dist < best_dist):
            best_dist = new_dist
            best_col = c

        #try with tethering
        if (tether_xy and c < len(pallet)-1):
            new_dist = sq_dist(pxl,mid_pnt(c_val,pallet[c+1]))
            if (new_dist < best_dist):
                best_dist = new_dist
                best_col = c + (tether_xy[0] % 2 + tether_xy[1]) % 2
    return best_col

class board(object):
    def __init__(self, img = None, tether=False, pallet_group=pallet_groups["bw"], build_dir = 1):
        '''
        Create a board representing an image

        Keyword Arguments:
        img -- the image to represent (default None (gui select))
        tether -- allow checkerboard tethering (default False)
        pallet_group -- the color pallet being used (default pallet_groups["bw"])
        build dir -- z direction of column building (default 1)
        '''
        if img == None:
            img = get_file()
        elif type(img) == str:
            img = Image.open(img)

        pxl_rgb = img.convert('RGB')
        
        self.width,self.height = img.size
        self.pallet = pallet_group[build_dir]
        self.build_dir = build_dir
        self.pxl_dat = []
        
        if tether:
            for y in range(self.height):
                self.pxl_dat.append(
                    [best_col(pxl_rgb.getpixel((x,y)),self.pallet,(x,y)) for x in range(self.width)]
                    )
        else:
            for y in range(self.height):
                self.pxl_dat.append(
                    [best_col(pxl_rgb.getpixel((x,y)),self.pallet) for x in range(self.width)]
                    )

    def save(self,filename = None):
        '''
        save a image representation of the board
        '''
        rgb_dat = []
        
        for y in range(self.height):
            rgb_dat += [self.pallet[col_id] for col_id in self.pxl_dat[y]]
        
        outputIm = Image.new("RGB", (self.width, self.height))
        outputIm.putdata(rgb_dat)

        if filename:
            outputIm.save(filename)
        else:
            file = tk.filedialog.asksaveasfile(mode='w', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
            if file:
                outputIm.save(os.path.abspath(file.name))

    def build_inf(self,xz):
        '''
        get information about how to place block

        Keyword Arguments:
        xz -- the relative coords of the block to place

        Return (block_id, jump place 1 higher)
        '''
        x,z=xz
        print('xz',xz)
        if self.build_dir == 1:
            color_id = self.pxl_dat[x][z]
            slot = color_id // 2
            y_dir = color_id % 2
        
        else:
            if x == self.height:
                slot = 8
            else:
                slot = self.pxl_dat[self.height - 1 - x][z] // 2

            if x == 0:
                y_dir = 0
            else:
                y_dir = 1 - self.pxl_dat[self.height - x][z] % 2
        slot += 1
        return slot,y_dir
