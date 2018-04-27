# minecraft-tools
A variety of useful tools for minecraft that are mainly focused on automating player actions

## read_memory.py
contains functions for reading key memory addresses to gather information about the player

## read_save_file.py
contains functions for reading block ids of the game world from chunk save data (game autosaves chunk data every 30 seconds)

## player_actions
contains functions to control player. Clicks and keyboard presses can be performed while the game in in the background, actions that require moving the mouse need the window to be in focus.

## board_generator and board_builder
used to convert image files into an image board to be viewed on a map. 
![example board](https://github.com/TrevorBivi/minecraft-tools/raw/master/example%20board.jpg "example board")
