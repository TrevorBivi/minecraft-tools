'''
ABOUT:
containts functions for reading block ids from save files

IMPORTANT METHODS:
change_coords -- convert to different game coordinate systems
open_region -- return a dictionary of 3d numpy arrays containing the block ids in loaded chunks

REQUIREMENTS:
- probably will be broken for versions pasts 1.12 because 1.13 is introduction a new world format
  
TO DO:
- add ability to read more than block ids

USEFUL INFO:
https://minecraft.gamepedia.com/Region_file_format
https://minecraft.gamepedia.com/NBT_format
https://minecraft.gamepedia.com/Chunk_format
https://minecraft.gamepedia.com/Anvil_file_format # the file format the game actually uses but it didn't really change how saves work and all the important info is still on the region file format page
https://minecraft-ids.grahamedgecombe.com/

https://minecraft.gamepedia.com/Talk:Chunk_format
'''

import zlib
import numpy as np #you can comment this out if you don't need to parse pre-1.13 saves
import math as m
import PIL
from PIL import Image

mc_dir = 'C:\\Users\\Trevor\\AppData\\Roaming\\.minecraft\\'

texture_dir = 'C:\\Users\\Trevor\\Desktop\\blocks\\' #textures for blocks
#texture_sizes = [ Image.open(mc_dir + '\\textures_' + str(i) + '.png') for i in range(5)  ]

kn = {}
def texture(name):
    global kn

    if name in ( b'minecraft:water',  b'minecraft:lava' ):
        name += b'_still'
    if name in kn:
        return kn[name]
    else:
        try:
            im = Image.open(texture_dir + name[10:].decode('utf8') + '.png')
        except Exception as tmp:
            try:
                im = Image.open(texture_dir + name[10:].decode('utf8') + '_top.png')
            except:
                im = Image.open(texture_dir + 'debug.png')
        kn[name] = im
    return im

    
def world_edges(regions):
    min_x = 99999999
    max_x = -99999999
    min_z = 99999999
    max_z = -99999999
    for r in regions:
        min_x = min(min_x,r.coords[0])
        max_x = max(max_x,r.coords[0])
        min_z = min(min_z,r.coords[1])
        max_z = max(max_z,r.coords[1])
    return min_x,min_z,max_x+1,max_z+1

def get_biv_tile_pos(block,tl):
    return (block.absolute_coords[0] - tl[0] * 32 * 16) * 16,(block.absolute_coords[2] - tl[1] * 32 * 16) * 16


def test_ch(ch):
    
    for x in range(16):
        for z in range(16):
            surfaceless = True
            for y in range(255,0,-1):
                if (x,y,z) in ch.blocks:
                    if ch.blocks[(x,y,z)].name == b'minecraft:air':
                        if surfaceless:
                            surfaceless = False
                            print('air',x,y,z)
                    if not ch.blocks[(x,y,z)].name:
                        print('nothing',x,y,z)
                    if ch.blocks[(x,y,z)].name and ch.blocks[(x,y,z)].name != b'minecraft:air':
                        print('found',x,y,z,ch.blocks[(x,y,z)].name,surfaceless)
                        break

def print_col(ch):
    for y in range(255):
        for z in range(16):
            for x in range(16):
                if (x,y,z) in ch.blocks:
                    print(x,y,z,ch.blocks[(x,y,z)].name)
            

def generate_biv(regions,size=4):
    block_size = 16
    chunk_size = 16 * block_size
    reg_size = 32 * chunk_size
    
    reg_edges = world_edges(regions)

    top_left = reg_edges[0] * reg_size, reg_edges[1] * reg_size
    
    b_size = ((reg_edges[2] - reg_edges[0]) * reg_size   ,(reg_edges[3] - reg_edges[1]) * reg_size )
    print('world has edges',reg_edges,'biv of size',b_size)
    img = Image.new('RGB',b_size)
    pixels = img.load()
    
    for r in regions:
        lch = len(r.chunks)
        print(lch,'chunks')
        for chi,c in enumerate(r.chunks):
            #if chi < 50: continue
            #if chi > 200: break
            print(chi,'/',lch)
            ch = r.chunks[c]
            
            for x in range(16):
                for z in range(16):
                    surfaceless = True
                    for y in range(255,0,-1):
                        if (x,y,z) in ch.blocks:
                            if ch.blocks[(x,y,z)].name == b'minecraft:air':
                                surfaceless = False
                            if ch.blocks[(x,y,z)].name and ch.blocks[(x,y,z)].name != b'minecraft:air':
                                if surfaceless: break
                                
                                tile = texture(ch.blocks[(x,y,z)].name)
                                p_coords =  get_biv_tile_pos(ch.blocks[(x,y,z)], reg_edges)
                                #print((x,y,z) ,p_coords )
                                for npx in range(16):
                                    for npy in range(16):
                                        #print('found',ch.blocks[(x+npx,y,z+npy)].name)
                                          # * 32  + c[1] * 16 + z
                                        pixels[ p_coords[0] + npx ,p_coords[1] + npy] = tile.getpixel((npx,npy))
                                        #print('done something')
                                break
    return img
            
        



#img.save("image.png", "PNG")
    


def get_name(inp):
    '''
    WIP return string ID if given an int ID or int ID if given a string ID
    '''
    pairs = (
        (b'minecraft:grass_block'),
        (b'minecraft:dirt'),
        (b'minecraft:lava'),
        (b'snow_layer'),
        (b'water'),
        (b'stone'),
        (b'coal_ore'),
        ('')
        )
    if isinstance(inp,int):pass
        

def show_map_world(regions): pass

def change_coords(xz,cur_sys,new_sys):
    '''
    return converted xz coord system
    '''
    if(cur_sys == 'region'):
        if (new_sys == 'chunk'):
            return [i * 32 for i in xz]
        elif(new_sys == 'block'):
            return [i * 512 for i in xz]

    elif(cur_sys == 'chunk'):
        if(new_sys == 'region'):
            return [i // 32 for i in xz]
        elif(new_sys == 'block'):
            return [i * 16 for i in xz]

    elif(cur_sys == 'block'):
        if(new_sys == 'chunk'):
            return [i // 16 for i in xz]
        elif(new_sys == 'region'):
            return [ (i // 16) //32 for i in xz]
        
    raise ValueError('could not understand coord conversion '+cur_sys+'->'+new_sys)

def chunk_to_file_location(x,z):
    '''
    return start location of relatie xz chunk in reg file
    '''
    return 4 * ((x % 32) + (z % 32) * 32)

def file_location_to_chunk(loc):
    '''
    return the relative chunk xz of chunk in file
    '''
    index = loc/4
    return int(index % 32), int(index // 32)

def find_dat(dat,to_find):
    '''
    find indexs of binary data
    '''
    indexs = []
    
    tag_len = len(to_find)
    cur_index = dat.find(to_find)
    
    while cur_index != -1:
        indexs.append(cur_index+tag_len)
        cur_index = dat.find(to_find,cur_index+1)
    return indexs

def get_bits(field,start,size):
    '''
    return int representing bits from field starting at index start and of size size
    '''
    val = field >> start
    val = val & (2 ** size - 1)
    return val

def test_get_bits():
    for i in range(15):
        for j in range(4):
            offset = i * 4 + j
            ret = get_bits(0x0123456789abcdef, offset, 4)
            print(offset, ret, bin(ret), )
        print()

    for i in range(5):
        for j in range(5):
            offset = i * 5 + j
            ret = get_bits(0b1000001000001000001000001, offset, 5)
            print(offset, ret, bin(ret), )
        print()

class BlockState():
    '''
    represents a possible state a block can be. block states are stored in Palette.states
    '''
    def __init__(self,name,description=None):
        self.name = name
        self.description = description
        
class Palette():
    '''
    represents all possible states a block can be in a given section
    '''
    def __init__(self,byteData=''):
        entries = get_indexs(byteData,b'\x08\x00\x04Name')
        props = get_indexs(byteData,b'\n\x00\nProperties')
        next_props = 0
        self.states = []
        for i,e in enumerate( entries):
            name_size = int.from_bytes(byteData[e+7:e+9],byteorder='big')
            newState = BlockState(name = byteData[e+9:e+9 + name_size])
            
            if next_props < len(props) and (i == 0 or entries[i-1] < props[next_props]) and( i == len(entries) - 1 or entries[i+1] > props[next_props] ):
                prop_size = props[next_props] - entries[i] - 13  #int.from_bytes(byteData[props[nxt_props]+14:i+16],byteorder='big')
                newState.description = byteData[props[next_props] + 13: props[next_props] + 13 + prop_size]
                next_props += 1

            self.states.append(newState)
            
class Chunk():
    '''
    represents a chunk filled with blocks 
    '''
    def __init__(self,coords,region):
        self.coords = coords
        self.blocks = {}
        self.region = region
        self.palette = [] #for convinence. chunks dont actually have pallets in game, only sections within them.

    @property
    def absolute_coords(self):
        region_coords = change_coords(self.region.absolute_coords,'region','chunk')
        return tuple((self.coords[i] + region_coords[i] for i in range(2)))

    def y_range(self,mini = 0,maxi = 255,dv=1,dh=1):
        for x in range(0,16,dh):
            for z in range(0,16,dv):
                for y in range(mini,maxi,dv):
                    if (x,y,z) in self.blocks:
                        yield self.blocks[(x,y,z)]
                    
class Block():
    '''
    represents a block in game
    '''
    def __init__(self,coords,chunk,palette,state):
        self.coords = coords
        self.palette = palette
        self.state = state
        self.chunk = chunk

    def __getattr__(self,attrName):
        if attrName in ('name','description'):
            if len(self.palette.states) > self.state:
                return self.palette.states[self.state].__getattribute__(attrName)
            else:
                return None
        raise AttributeError('attribute does not exist')

    @property
    def absolute_coords(self):
        chunk_coords = self.chunk.absolute_coords  
        return (self.coords[0] + chunk_coords[0] * 16, self.coords[1], self.coords[2] + chunk_coords[1] * 16)

    def above(self,amount):
        new_coords = (self.coords[0],self.coords[1]+amount,self.coords[2])
        if new_coords in self.chunk.blocks:
            return self.chunk.blocks[ new_coords ]
        return None

    '''
    replaced to easily support further block state property parsing

    @property
    def name(self):
        if len(self.Palette.states) > self.state:
            return None
        return self.Palette[self.state].name
        
    @property
    def description(self):
        if len(self.Palette.states) > self.state:
            return None
        return self.Palette[self.state].description
    '''

bsss = None

class Region():
    '''
    represents a region filled with chunks
    '''
    def __init__(self,path,version = '1.13',print_info=False):
        temp = path.split('.')
        self.coords = int(temp[-3]), int(temp[-2])
        
        with open(path, 'rb') as file:
            locations = file.read(4*1024)
            timestamps = file.read(4*1024)
            data = file.read()
            self.chunks = {}

            #newPalette = Palette()
            
            #for all chunks (16x256x16)
            if print_info: print('parsing region ' + path.split('/')[-1].split('\\')[-1] )
            
            for index in range(0,4096,4):
                if print_info and index % (4096 // 10) < 4:
                    dig = 9 - (index // (4096 // 10)) + 1
                    print(str( dig ) + '...',end='\n' if dig == 0 else '')
                
                offset = (int.from_bytes(locations[index:index+3],'big')-2)*4096
                if offset >= 0:
                    chunk_len = int.from_bytes(data[offset:offset+4],'big')-1
                    chunk_dat = zlib.decompress( bytes(data[offset+5:offset+5+chunk_len]),15+32  )
                    chunk_coords = file_location_to_chunk(index)
                    
                    if version == '1.13':
                        if chunk_coords == (10,2):
                            global bsss
                            bsss = chunk_dat
                            print('bss def')
                            
                        newChunk = Chunk(chunk_coords,self) #chunks are described using new chunk object (using property 'blocks'-a dict of coord keys and block object values )
                        self.chunks[chunk_coords] = newChunk

                        newChunk.palette = Palette()
                        
                        section_ys = get_indexs(chunk_dat,b'\x01\x00\x01Y') #y values of all sections
                        block_state_starts = get_indexs(chunk_dat,b'\x0c\x00\x0bBlockStates') #list of state of blocks (Palette index)   
                        palette_starts = get_indexs(chunk_dat,b'\t\x00\x07Palette') #blocks that there are at least 1 of in this section (and always air at index 0)
                        palette_ends = get_indexs(chunk_dat, b'\x07\x00\x08SkyLight')

                        
                        
                        assert len(section_ys) == len(block_state_starts ) == len(palette_starts) == len(palette_ends)

                        #for all sections (16x16x16)
                        for si,(yi,bsi,psi,pei) in enumerate( zip(section_ys,block_state_starts,palette_starts,palette_ends)):
                            ys = chunk_dat[yi+4]
                            #print('si',si)
                            palette = Palette(chunk_dat[psi:pei])#get_Palette(chunk_dat[psi:pei])

                            newChunk.palette.states += [s for s in palette.states if s not in newChunk.palette.states]
                            if chunk_coords == (14,3):
                                print('bsz',(psi-bsi-18)/8/64,'ys',ys,'yi',yi,'ps',[j.name for j in palette.states])
                            b_size = int((psi-bsi-18)/8/64)
                            assert b_size == (psi-bsi-18)/8/64
                            #if chunk_coords == (10,2):
                                #print('intv',chunk_dat[bsi + 17 - 17:bsi + 17 + 32 - 17],chunk_dat[psi-1 - 512:psi - 1 + 8])
                            int_val =int.from_bytes( chunk_dat[bsi + 8+1:psi],byteorder='big')# int.from_bytes( chunk_dat[bsi + 7:psi],byteorder='little')

                            if chunk_coords == (14,3):
                                print( bin(int.from_bytes( chunk_dat[bsi + 8+1:psi],byteorder='little')))
                                print( bin(int.from_bytes( chunk_dat[bsi + 8+1:psi],byteorder='big')))
                                #print( bin())
                                #print('int val',int_val)
                                
                            for y in range(16):
                                for z in range(16):
                                    for x in range(16):
                                        
                                        dat_pos = (x+z*16+y*256) * b_size
                                        val = get_bits(int_val,dat_pos,b_size)
                                        newChunk.blocks[(x,y+ys*16,z)] = Block((x,y+ys*16,z),newChunk,palette,val)
                                        
                    elif version == '1.12': #may work for versions as far back as 1.3
                        chunk_arr = np.full((16,256,16),-1,dtype=int) #chunks are descriped as a numpy array

                        #read data from all chunk sections (16x16x16 blocks)
                        block_starts = [i + 4 for i in find_dat(chunk_dat,b'\x07\x00\x06Blocks')] #find start locations of block ids using tag #1b - tag type , 2b - length of string , utf8 string
                        y_starts = find_dat(chunk_dat,b'\x00\x01Y') #find start locations of chunk sections idk why used to have this tag with a x01 but it seemed to work b'\x01\x00\x01Y'  
                        for sec in range(len(block_starts)):
                            y_pos = chunk_dat[y_starts[sec]]
                            block_dat = chunk_dat[block_starts[sec]:block_starts[sec]+4096]
                            
                            for x in range(16):
                                for y in range(16):
                                    for z in range(16):
                                        dat_pos = x+z*16+y*256
                                        chunk_arr[x,y+y_pos*16,z] = int(block_dat[dat_pos])
                        chunks[chunk_coords] = chunk_arr
                    else:
                        raise ValueError('unsupported save version (version=' + version + ')')
    @property
    def absolute_coords(self):
        return self.coords
    
def id_counts(chunk):
    '''
    return count of block id in chunk
    '''
    unique, counts = np.unique(chunk, return_counts=True)
    return dict(zip(unique, counts))

def get_indexs(byteData,val):
    s = -1
    indexs = []

    try:
        while True:
            s = byteData.index(val,s+1)
            indexs.append(s)
    except Exception: pass

    return indexs



if __name__ == '__main__':
    #print('start parse...')
    r1 = Region('C:\\Users\\Trevor\\AppData\\Roaming\\.minecraft\\saves\\New World num 10\\region\\r.0.0.mca',print_info=True)
    
    #r00 = Region('C:\\Users\\Trevor\\AppData\\Roaming\\.minecraft\\saves\\world1\\region\\r.0.0.mca',print_info=True)

'''
def get_Palette(byteData):
    entries = get_indexs(byteData,b'\x08\x00\x04Name')
    props = get_indexs(byteData,b'\n\x00\nProperties')
    next_props = 0
    pal = []
    for i,e in enumerate( entries):
        name_size = int.from_bytes(byteData[e+7:e+9],byteorder='big')
        name = byteData[e+9:e+9 + name_size]
        if next_props < len(props) and (i == 0 or entries[i-1] < props[next_props]) and( i == len(entries) - 1 or entries[i+1] > props[next_props] ):
            prop_size = props[next_props] - entries[i] - 13  #int.from_bytes(byteData[props[nxt_props]+14:i+16],byteorder='big')
            prop = byteData[props[next_props] + 13: props[next_props] + 13 + prop_size]
            next_props += 1
        else:
            prop = None
        pal.append(block_dat(name,prop))
    return pal
'''



