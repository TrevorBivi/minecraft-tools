'''
ABOUT:
reads memory values relating to the player from the Minecraft process

IMPORTANT METHODS:
player_position -- return information about player coordinates and rotation

REQUIREMENTS:
- must be running 1.13.2 -- there is a version that works with 1.12.2 in git history

TODO:
- add support for reading base pointers relative to threadstacks instead of just process modules
- determine player height by finding memory value that represents isCrouching
- add support for reading inventory information and current memory chunk data from memory adresses 
'''

#Used to get pid by process name
from subprocess import check_output

#Used to read memory values
from ctypes import *
from ctypes.wintypes import *

#Used to convert memory values
import struct

#Used to get address of dll within process
import win32process

import math as m


###### get the process id of the Minecraft process
def get_pid(proc_name):
    '''
    get pid by process name
    '''
    cmd_output = check_output('tasklist /fi "Imagename eq '+ proc_name +'"')
    return int(cmd_output.split()[14])

pid = get_pid('javaw.exe')

###### find the handle of the Minecraft process

PROCESS_ALL_ACCESS = 0x1F0FFF
#PROCESS_VM_READ = 0x0010
processHandle = windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

###### find the memory address of the desired Minecraft process module (OpenAL64.dll for player xyz)
def print_module_names(process):
    '''
    just to help find names
    '''
    modules = win32process.EnumProcessModules(process)
    for n,m in enumerate(modules):
        print(str(n) + '-' + hex(m) +'-' + win32process.GetModuleFileNameEx(process,m ))              

def get_module_addr(process,name):
    '''
    get address of module by name that is a member of process
    '''
    modules = win32process.EnumProcessModules(process)
    for m in modules:
        if name in str(win32process.GetModuleFileNameEx(process,m )):
            return m

open_al_addr = get_module_addr(processHandle,"OpenAL.dll")

###### find player position x and camera rotation y relative to desired modules
ReadProcessMemory = windll.kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [HANDLE,LPCVOID,LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.rettype = BOOL

type_sizes = {'f':4, 'l':4, 'q':8} #idk if q would behave
def get_val(process,addr,typ):
    '''
    get value from processHandler starting at address of type
    '''
    buffer = c_void_p()
    bufferSize = type_sizes[typ]
    bytesRead = c_size_t()
    while not ReadProcessMemory(processHandle, addr, byref(buffer), bufferSize, byref(bytesRead)):
        print ("Failed to read",process,hex(addr),typ)
    if buffer.value == None:
        return 0
    return struct.unpack(typ, struct.pack("I", buffer.value)   )[0]

######x val
pointer_addr = open_al_addr + 0x000DEC48 # find the base pointer in module that x coordinate memory adress can be found relative to -- this was found using pointer scanning on the minecraft process with Cheat Engine
pointed_to = get_val(processHandle,pointer_addr,'l')
char_x_addr = pointed_to + 0xF0
print('CHAR X ADDR',char_x_addr)
####### other values are nearby -- found with Cheat Engine's memory viewer
char_y_addr = char_x_addr + 4
char_z_addr = char_x_addr + 8

# I assume the values at these addresses are a patch of trigonemetric function 
# values relating to camera rotation used throughout minecraft 
# values relating to ry can behave strangely under certain circumstances so we need to
# use different ones depending on the sinage of rx
char_rx_addr = char_x_addr + 0x74
char_sin_rx_nsin_ry_addr = char_x_addr + 0x54
char_nsin_ry_addr = char_x_addr + 0x70
char_ncos_ry_addr = char_x_addr + 0x50

player_height = 1.62

def player_position():
    '''
    return dict with information about player position and rotation
    '''
    nsin_ry = get_val(processHandle, char_nsin_ry_addr, 'f')    
    ncos_ry = get_val(processHandle, char_ncos_ry_addr, 'f')

    ry = m.degrees(m.atan2( -nsin_ry, -ncos_ry ) )
    char_sin_rx_nsin_ry = get_val(processHandle, char_sin_rx_nsin_ry_addr, 'f')    
    rx = m.degrees(m.asin( max(char_sin_rx_nsin_ry / nsin_ry,0.0001)))
    
    ret = {
        'x':get_val(processHandle, char_x_addr, 'f'),
        'y':get_val(processHandle, char_y_addr, 'f')- player_height,  # give feet coords like in game's debug screen instead of head coords
        'z':get_val(processHandle, char_z_addr, 'f'),
        'rx': rx,
        'ry': ry
    }
    return ret

class THREADENTRY32(Structure):
    _fields_ = [
        ('dwSize' , c_long ),
        ('cntUsage' , c_long),
        ('th32ThreadID' , c_long),
        ('th32OwnerProcessID' , c_long),
        ('tpBasePri' , c_long),
        ('tpDeltaPri' , c_long),
        ('dwFlags' , c_long) ]

def get_tid(proc_id):
    '''
    get the ids of processes's threads
    (This function is only the first step of reading a base pointer relative to a threadstack)
    haven't needed to do but steps are as follows https://stackoverflow.com/questions/48237813/
    
    - Get the id of each thread (wew)
    - Get a Handle to the thread: Use OpenThread() 
    - import NtQueryInformationThread which is an undocumented function exported by ntdll.dll
    - call NtQueryInformationThread() with the thread handle in the first argument and ThreadBasicInformation as the second. The result is a THREAD_BASIC_INFORMATION structure with member variable StackBase.
    - StackBase is the address of THREADSTACK, just match it with the correct id. 
    
    '''
    hSnapshot = c_void_p(0)
    te32 = THREADENTRY32 ()
    te32.dwSize = sizeof(THREADENTRY32 )

    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0)
        
    thr_ids = []
    
    ret = Thread32First(hSnapshot, pointer(te32))
    if ret == 0:
        CloseHandle(hSnapshot)
        return false
    
    while ret :
        if te32.th32OwnerProcessID == proc_id:
            #print('thr_id',te32.th32ThreadID, '  tpBasePri',te32.tpBasePri,'  tpDeltaPri',te32.tpDeltaPri, '  cntUsage',te32.cntUsage,'  dwSize',te32.dwSize  )
            thr_ids.append( te32.th32ThreadID)
        ret = Thread32Next(hSnapshot, pointer(te32))
    return thr_ids
