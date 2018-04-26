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
'''

import zlib
import numpy as np


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

#load region data (512,256,512 blocks)
def open_region(ch, reg_path=None):
    '''
    return a dictionary of all chunks in region that contain at least one sub chunk
    '''
    chunks = {}
    chX,chZ = ch
    with open(reg_path + 'r.' + str(chX) + '.' + str(chZ) + '.mca', 'rb') as file:
        locations = file.read(4*1024)
        timestamps = file.read(4*1024)
        dat = file.read()

        #for all chunks generated
        for index in range(0,4096,4):
            offset = (int.from_bytes(locations[index:index+3],'big')-2)*4096
            if offset >= 0:
                chunk_len = int.from_bytes(dat[offset:offset+4],'big')-1
                chunk_dat = zlib.decompress( bytes(dat[offset+5:offset+5+chunk_len]),15+32  )
                chunk_arr = np.full((16,256,16),-1,dtype=int)

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
                chunks[file_location_to_chunk(index)] = chunk_arr
    return chunks

def id_counts(chunk):
    '''
    return count of block id in chunk
    '''
    unique, counts = np.unique(chunk, return_counts=True)
    return dict(zip(unique, counts))
    