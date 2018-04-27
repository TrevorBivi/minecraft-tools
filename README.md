# minecraft-tools
A variety of useful tools for minecraft that are mainly focused on automating player actions.

## read_memory.py
Contains functions for reading key memory addresses to gather information about the player.

## read_save_file.py
Contains functions for reading block ids of the game world from chunk save data (game autosaves chunk data every 30 seconds).

## player_actions.py
Contains functions to control player. Clicks and keyboard presses can be performed while the game is in the background. Actions that require moving the mouse need the window to be in focus.

## board_generator.py and board_builder.py
Used to convert image files into an image board to be viewed on a map. 
![Example board](https://github.com/TrevorBivi/minecraft-tools/raw/master/example%20board.jpg "Example board")
