'''
ABOUT:
contains methods relating to controlling the player in game

IMPORTANT METHODS:
rotate_to -- rotate player to be looking at either a given rotation or 3d point
move_to -- move to a certain xz by walking the shortest path (doesn't rotate vision, just uses walk keys)
click -- click a mouse key
press -- press a keyboard key
wait_to_cross -- wait for a player position variable to cross over a given value
jump_peak_wait -- wait for the player to reach the peak of a jump

REQUIREMENTS:
- sending key and mouse presses can be done while the window is in the
  background, to rotate player the mouse is overrided and the window must be
  in the front. It seems minecraft won't allow mouse movements to rotate
  the player if the window is not in focus
  
TO DO:
- add functions to manipulate inventory
'''


#Used to control player
import win32
import win32api
import win32con
import win32gui

import time
import math as m

import ctypes

from read_memory import *

window = win32gui.FindWindow(None,"Minecraft 1.13.2")

### Scan code event
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', ctypes.c_long),
                ('dy', ctypes.c_long),
                ('mouseData', ctypes.c_ulong),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (('wVk', ctypes.c_ushort),
                ('wScan', ctypes.c_ushort),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', ctypes.c_ulong),
                ('wParamL', ctypes.c_ushort),
                ('wParamH', ctypes.c_ushort))
    
class _INPUTunion(ctypes.Union):
    _fields_ = (('mi', MOUSEINPUT),
                ('ki', KEYBDINPUT),
                ('hi', HARDWAREINPUT))

class INPUT(ctypes.Structure):
    _fields_ = (('type', ctypes.c_ulong),
                ('union', _INPUTunion))

def send_input(*inputs):
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
    return ctypes.windll.user32.SendInput(nInputs, pInputs, cbSize)

scan_codes = {' ':57,
              'w':17,
              'a':30,
              's':31,
              'd':32,
              'e':18}

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
IMPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

def key_input(code,flags):
    kbinp = KEYBDINPUT(code, code, flags, 0,None)
    print('cd',code,'fg',flags)
    inp = INPUT(
        INPUT_KEYBOARD,
        _INPUTunion(ki = kbinp)
        )
    send_input(inp)

def sc_key_up(scan_code,extra_flags=KEYEVENTF_SCANCODE):
    if not extra_flags: extra_flags = 0
    key_input(scan_code, KEYEVENTF_KEYUP | extra_flags) #KEYEVENTF_SCANCODE |

def sc_key_down(scan_code,extra_flags=KEYEVENTF_SCANCODE):
    if not extra_flags: extra_flags = 0
    key_input(scan_code,extra_flags) #

def sc_key_press(scan_code,press_time=0.01,extra_flags=KEYEVENTF_SCANCODE):
    key_down(scan_code,extra_flags)
    time.sleep(press_time)
    key_up(scan_code,extra_flags)

#time.sleep(4);key_press(0x49)





###### primary mouse controls
def click(key = 'left', press_time = 0.05):
    if key == 'left':    
        win32gui.SendMessage(window, win32con.WM_LBUTTONDOWN, 1, 0)
        time.sleep(press_time)
        win32gui.SendMessage(window, win32con.WM_LBUTTONUP, 1, 0)
    elif key == 'right':
        win32gui.SendMessage(window, win32con.WM_RBUTTONDOWN, 1, 0)
        time.sleep(press_time)
        win32gui.SendMessage(window, win32con.WM_RBUTTONUP, 1, 0)

def rotate(dy,dx):
    '''
    rotate -- adjust facing by (dy / dx)
    '''
    screen_box = win32gui.GetWindowRect(window)
    dy += (screen_box[2] + screen_box[0] )/2+ 1
    dx += (screen_box[3] + screen_box[1] )/2 + 10
    win32api.SetCursorPos( (round(dy),round(dx)) )

###### primary key controls
key_codes = {
    '1':0x31,'2':0x32,'3':0x33,'4':0x34,'5':0x35,'6':0x36,'7':0x37,'8':0x38,'9':0x39,
    'w':0x57,'a':0x41,'s':0x53,'d':0x44,
    'shift':0xA0,'ctrl':0x11,' ':0x20,
    'e':0x45,
}

def key_dwn(key=None,ignore_crouch=False):
    if key:
        if key == 'ctrl' and ignore_crouch:
            player_height = 1.54
        if key in ('ctrl','shift'):
            win32gui.SendMessage(window,#win handle
                                 win32con.WM_KEYDOWN,#msg
                                 key_codes[key],
                                 0) # all 0 flags is fine
        else:
            sc_key_down(scan_codes[key])
        

def key_up(key=None,ignore_crouch=False):
    if key:
        if key == 'ctrl' and ignore_crouch:
            player_height = 1.62
        if key in ('ctrl','shift'):
            win32gui.SendMessage(window,
                                 win32con.WM_KEYUP,
                                 key_codes[key],
                                 0xC0000000) # previous key state and transition state flags must be 1
        else:
            sc_key_up(scan_codes[key])
            
def press(key,press_time=0.05,ignore_crouch=False):
    key_dwn(key,ignore_crouch)
    time.sleep(press_time)
    key_up(key,ignore_crouch)

###### some useful math stuff
def get_pnt_rot(pnt,pos):
    '''
    get rotation needed to look at point
    '''
    dx = pnt[0] - pos['x']
    dy = pnt[1] - pos['y'] - player_height
    dz = pnt[2] - pos['z']
    lxz = m.sqrt(dx**2+dz**2)
    ry = -m.degrees(m.atan2(dx,dz))
    rx = -m.degrees(m.atan2(dy,lxz))
    return ry,rx

def sub3x3(a,b):
    return [a[i]-b[i] for i in range(3)]

def dot3x3(a,b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def cross3x3(a,b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])

def signed_vol6(a,b,c,d):
    '''
    return the signed volume of a tetrahedron multiplied by 6
    '''
    return dot3x3(cross3x3(sub3x3(b,a),sub3x3(c,a)),sub3x3(d,a))

def line_intersect_tri(l,t):
    '''
    return if line intersects tri in 3d

    Keyword Arguments:
    l -- the line ((x0,y0,z0),(mx,my,mz))
    t -- the triangle verticies (x,y,z)
    '''

    x0,y0,z0 = l[0]
    mx,my,mz = l[1]
    
    lp1 = (x0 + 5000 * mx,y0 + 5000 * my,z0 + 5000 * mz)
    lp2 = (x0 - 5000 * mx,y0 - 5000 * my,z0 - 5000 * mz)

    v1 = signed_vol6(lp1,t[0],t[1],t[2]) >= 0
    v2 = signed_vol6(lp2,t[0],t[1],t[2]) >= 0
    v3 = signed_vol6(lp1,lp2,t[0],t[1]) >= 0
    v4 = signed_vol6(lp1,lp2,t[1],t[2]) >= 0
    v5 = signed_vol6(lp1,lp2,t[2],t[0]) >= 0
    
    return (v1 != v2) and (v3 == v4 == v5)

def line_intersect_quad(l,q):
    '''return if looking at a given quadralateral in 3d

    Keywork Arguments:
    l -- the line ((x0,y0,z0),(mx,my,mz))
    q -- the quadralateral verticies (x,y,z)
    '''
    return line_intersect_tri(l,q[1:]) or line_intersect_tri(l,q[:-1])

def relative_ang(ang_a,ang_b):
    '''
    determine ang_b relative to ang_a
    '''
    if ang_a < -90 and ang_b > 90:
        return ang_b - 360 - ang_a
    if ang_a > 90 and ang_b < -90:
        return ang_b + 360 - ang_a
    return ang_b - ang_a

'''# no longer need these
def in_triangle(pnt,tri):
    #return if a 2d point is in a 2d triangle
    p1,p2,p3 = tri
    a = ((p2[1] - p3[1])*(pnt[0] - p3[0]) + (p3[0] - p2[0])*(pnt[1] - p3[1])) / ((p2[1] - p3[1])*(p1[0] - p3[0]) + (p3[0] - p2[0])*(p1[1] - p3[1]))
    b = ((p3[1] - p1[1])*(pnt[0] - p3[0]) + (p1[0] - p3[0])*(pnt[1] - p3[1])) / ((p2[1] - p3[1])*(p1[0] - p3[0]) + (p3[0] - p2[0])*(p1[1] - p3[1]))
    c = 1 - a - b
    return (0 <= a <= 1) and (0 <= b <= 1) and (0 <= c <= 1)

def in_quad(pnt,rot_quad):
    #return if a 2d point is in a 2d quadrilateral
    if rot_quad == None or pnt == None:
        print ('fuck fuck gay ass cunt fuck bittch')
        return

    for i,qp in enumerate(rot_quad):
        if pnt[0] - qp[0] > 180:
            rot_quad[i] = (rot_quad[i][0] + 360, rot_quad[i][1])
        elif pnt[0] - qp[0] < -180:
            rot_quad[i] = (rot_quad[i][0] - 360, rot_quad[i][1])
    result = in_triangle(pnt,rot_quad[1:]) or in_triangle(pnt,rot_quad[:-1])

    return result

def add(a,b):
    return [a[i]+b[i] for i in range(3)]
'''

###### rotation tools
def cam_line(pos):
    '''
    return information about camera line (x0,y0,z0),(mx,my,mz)
    where slope is in direction being faced
    '''
    xyz0 = pos['x'],pos['y']+player_height,pos['z']
    sinRx = m.sin(m.radians(pos['rx']))
    cosRx = m.cos(m.radians(pos['rx']))
    slope = (-cosRx * m.sin(m.radians(pos['ry'])), -sinRx,  cosRx * m.cos(m.radians(pos['ry'])))
    return xyz0,slope

def rotate_helper(rot_inf,sensitivity = 1, err = 0.2, place = False, rot_quad = None):
    '''
    retrun if was already at right rotation or made a correction

    Keyword Arguments:
    rot_inf -- either contains (ry,rx) or (x,y,z) to look at
    sensitivity -- decimal form of sensitivity
    err -- max allowed deviation of rx or ry
    place -- right click once rotated
    rot_quad -- perform raycast to check if looking at quadralateral
    '''
    pos = player_position()
    #determine desired rotation
    look_pnt = len(rot_inf) == 3
    if look_pnt:
        ry,rx = get_pnt_rot(rot_inf,pos)
    else:
        ry,rx = rot_inf
    
    #determine desired change in ry
    if ry != None: 
        dry = ry - pos['ry']
        if dry > 180:
            dry -= 360
        elif dry < -180:
            dry += 360
    
    #determine desired change in rx
    if rx != None:
        drx = rx - pos['rx']

    #rotate vision if not looking at right position
    if ((rot_quad and not line_intersect_quad( cam_line(pos), rot_quad)) or
       (not rot_quad and ((rx != None and abs(drx) > err) or (ry != None and abs(dry) > err)))):
        # get change in rotation needed
        mx,my=0,0
        if ry != None and abs(dry) > err:
                mx = (dry) * 30 / 4.5 / sensitivity
        if rx != None and abs(drx) > err:
                my = (drx) * 30 / 4.5 / sensitivity
        rotate(mx,my)
        #print('move with',mx,my, 'rot ', dry,drx)
        return False

    if place:
        #print('pos',pos)
        click('right')
        
    return True

def rotate_to(rot_inf,sensitivity = 1,err=0.2,place=False,rot_freq=0.1,rot_quad=None):
    '''
    rotate to be facing (ry / rx) or (x,y,z)

    Keyword Arguments:
    rot_inf -- either contains (ry,rx) or (x,y,z) to look at
    sensitivity -- decimal form of sensitivity
    err -- max allowed deviation of rx or ry
    place -- right click once rotated
    rot_quad -- perform raycast to check if looking at quadralateral
    '''
    while not rotate_helper(rot_inf,sensitivity,err,place,rot_quad):
        time.sleep(rot_freq)

###### move tools
def get_move_keys(rot):
    '''
    get keys to press to move in move in direction of rot
    '''
    keys = []
    if -67.5 <= rot <= 67.5:
        keys.append('w')

    if 22.5 <= rot <= 157.5:
        keys.append('d')

    if -157.5 <= rot <= -22.5:
        keys.append('a')

    if rot >= 112.5 or rot <= -112.5:
        keys.append('s')
    return keys      

def move_to(xz, err = 0.2, special_key=None,scan_freq=0.15, max_time = 99):
    '''
    walk straight to coords

    Keyword Arguments:
    xz -- the position to walk to
    err -- the max squared distance from xz to stop (default 0.2)
    special_key -- extra key to hold while moving (default None)
                   ie. 'shift','ctrl',' '
    max_time -- max time to attempt move
    '''
    keys_down = []
    key_dwn(special_key)
    
    start_time = time.time()
    successful = True

    #continue moving until within sqrt dist
    pos = player_position()
    dx = xz[0] - pos['x']
    dz = xz[1] - pos['z']    
    while ( dx**2 + dz ** 2 > err ):
        if time.time() - start_time > max_time:
            successful = False
            break
        #get movement dir
        vel_ang = m.degrees(m.atan2(-dx,dz))#direction player needs to move in
        move_ang = relative_ang( pos['ry'], vel_ang)#direction relative to player rotation
        move_keys = get_move_keys(move_ang)
        #print('vel',vel_ang,'move',move_ang,move_keys)
        
        #start pressing keys that aren't needed
        for k in move_keys:
            if not k in keys_down:
                key_dwn(k)
                print('KEY DOWN',k)
                
        #stop pressing keys that aren't needed
        for k in keys_down:
            if not k in move_keys:
                key_up(k)
                print('KEY UP',k)

        keys_down = move_keys
        time.sleep(scan_freq)
        pos = player_position()
        dx = xz[0] - pos['x']
        dz = xz[1] - pos['z']
        print('xz',sz,'pos',pos,'dx,dz',dx,dz)

    #stop pressing all keys
    for k in keys_down:
        key_up(k)
    key_up(special_key)
    
    return successful

###### wait for events
def wait_to_cross(var,val,scan_freq=0.02,max_time = 99):
    '''
    wait for some position variable to pass over a given value
    '''
    start_rel = player_position()[var] > val
    start_time = time.time()
    
    time.sleep(scan_freq)
    while start_rel == (player_position()[var] > val):
        if time.time() - start_time > max_time:
            return False
        time.sleep(scan_freq)
    return True

def jump_peak_wait(jump=True, use_start_height=True, scan_freq = 0.0175):
    '''
    wait to reach the peak of a jump
    '''
    

    last_y = -999
    new_y = player_position()['y']

    if jump:
        if use_start_height:
            start_y = round(player_position()['y'])
            key_dwn(' ')
        else:
            press(' ')

    while True:
        last_y = new_y
        new_y = player_position()['y']
        vel = new_y - last_y
        if use_start_height:
            if new_y - start_y > 1 and vel > 0:
                key_up(' ')
                break
        elif vel < 0:
            break

