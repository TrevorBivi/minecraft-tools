'''
ABOUT:
places a board that represents an image in minecraft (to be viewed on a map)

IMPORTANT METHODS:
place_board -- place a given board object

REQUIREMENTS:
- must use creative mode

TO DO:
- make program able to replenish blocks it places in the hotbar so the bot can work on survival mode
- clean up how code handles different placement directions
'''

from board_generator import *
from player_actions import *
from read_memory import *

def place_block(item_slot,place_xz,build_dir = 1,change_height = 0):
    '''
    place the next block of column being built
    '''
    print('place_block()',place_xz,change_height)
    pos = player_position()

    if change_height == 1:
        press('9')#
    else:
        press( str(item_slot) )
    
    #get position of block to place
    px,pz = place_xz
    py = pos['y']


    if build_dir == 1:
        moved = move_to((px,pz + 0.3),err = 0.03, max_time = 4)
    else:  
        moved = move_to((px,pz + 0.7),err = 0.03, max_time = 4)
    if not moved:
        return False
    
    #place block        
    if build_dir == 1:
        quad = (( px-0.4,py-0.1,pz ),
                    ( px+0.4,py-0.1,pz ),
                    ( px-0.4,py-0.9,pz ),
                    ( px+0.4,py-0.9,pz ))
        rotate_to( (px,py-0.5,pz), err = 0, place=True, rot_quad = quad)
    else:
        quad = (( px-0.4,py-0.1,pz +1),
                    ( px+0.4,py-0.1,pz+1 ),
                    ( px-0.4,py-0.9,pz+1),
                    ( px+0.4,py-0.9,pz+1 ))
        rotate_to( (px,py-0.5,pz+1), err = 0, place=True, rot_quad = quad)

    print('placed')
    #time.sleep(33)

    #place extra block underneath self if pixel uses beveling
    if change_height == 1:
        press( str(item_slot) )
        rotate_to((None,90),err = 1)
        press('w')
        jump_peak_wait()
        click('right')
    return True

def place_col(start_xyz,xi,chosen_board):
    '''
    place next column of board being built
    '''
    key_dwn('ctrl')
    
    col_size = chosen_board.height
    if chosen_board.build_dir == -1:
        col_size += 1

    slot,y_dir = chosen_board.build_inf((0,xi))
    for yi in range(col_size):
        if col_size and not col_size % 32:
            refill_hotbar()
        
        old_slot,old_y_dir = slot,y_dir
        
        #get info about how to place block
        slot,y_dir = chosen_board.build_inf((yi,xi))
    
        placed = place_block(slot,
                    (start_xyz[0] + xi ,start_xyz[2] + chosen_board.build_dir * (yi+1)),
                    chosen_board.build_dir, y_dir )
        while not placed:
            place_block(old_slot, # a missplace has happened retry placing previous block
                        (start_xyz[0] + xi ,start_xyz[2] + chosen_board.build_dir * max(yi,1)),
                        chosen_board.build_dir, old_y_dir )
            placed = place_block(slot,
                    (start_xyz[0] + xi ,start_xyz[2] + chosen_board.build_dir * (yi+1)),
                    chosen_board.build_dir, y_dir )
    key_up('ctrl')

def place_board(board,start_xyz=None,start_col = 0):
    '''
    build a board starting at start_xyz
    '''
    time.sleep(2)
    
    if not start_xyz:#use current position
        pos = player_position()
        start_xyz = (m.floor(pos['x']) + 0.5 ,pos['y'],m.floor(pos['z']))
    print('starting a board at:',start_xyz)
    for i in range(start_col,board.width):
        if i - start_col > 2:
            print('MADE 3 COLS')
            break
        place_col(start_xyz,i,board)
        rotate_to((start_xyz[0]  + i, start_xyz[1], start_xyz[2]),sensitivity=0.06,err=0.5)
        
        key_dwn('shift')
        key_dwn('w')
        
        if board.build_dir == 1:  
            wait_to_cross('z', start_xyz[2] + 3)
            key_up('shift')
            wait_to_cross('z',start_xyz[2] + 0.2)
        else:
            wait_to_cross('z', start_xyz[2] - 2)
            key_up('shift')
            wait_to_cross('z',start_xyz[2] + 0.8)
        key_up('w')
        move_to( (start_xyz[0] + 1.25 + i, start_xyz[2] + 0.5  ), special_key='ctrl' )

tl_tile = (424, 743)
br_tile = (859, 853)
hb_tile = (426, 916)

def calibrate_inv_pos():
    import pyautogui as pag
    input('Hover over top left inv tile')
    _tl_tile = pag.position()
    input('Hover over bottem right inv tile')
    _br_tile = pag.position()
    input('Hover over left most hotbar tile')
    _hb_tile = pag.position()

    print('tl_tile=',tuple(_tl_tile))
    print('br_tile=',tuple(_br_tile))
    print('hb_tile=',tuple(_hb_tile))

def get_tile_pos(x,y):
    v = (br_tile[0] - tl_tile[0]) / 8
    if y < 3:
        h = (br_tile[1] - tl_tile[1]) / 2
        return tl_tile[0] + h * x,tl_tile[1] + v * y
    return hb_tile[0] + v * x,hb_tile[1]


refills_performed = 0
def refill_hotbar(cols = 5):
    press('e')
    time.sleep(0.2)
    global refills_performed
    for i in list(range(cols)) + [8]:

        refill_slot = get_tile_pos(i, refills_performed // 2)
        bar_slot = get_tile_pos(i, 3)
        
        wm_mouse_move( refill_slot[0],refill_slot[1] )
        time.sleep(0.1)
        click(press_time=0.1)
        time.sleep(0.1)
        wm_mouse_move( bar_slot[0],bar_slot[1] )
        time.sleep(0.1)
        click(press_time=0.1)
        time.sleep(0.1)
        wm_mouse_move( refill_slot[0],refill_slot[1] )
        time.sleep(0.1)
        click(press_time=0.1)
        time.sleep(0.1)
    refills_performed += 1


'''
b = board("C:\\Users\\Trevor\\Desktop\\chen final.png",build_dir = 1,tether=False)#.save()
time.sleep(3)
place_board(b,start_col=23,start_xyz=(375.5, 83.00000274658203, -431))
'''
