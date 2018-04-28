# minecraft-tools
A variety of useful tools for minecraft that are mainly focused on automating player actions.

## read_memory.py
Contains functions for reading game memory addresses to gather information about the player.

## read_save_file.py
Contains functions for reading block ids of the game world from chunk save data (game autosaves chunk data every 30 seconds).

## player_actions.py
Contains functions to control player. Clicks and keyboard presses can be performed while the game is in the background. Actions that require moving the mouse need the window to be in focus.

## board_generator.py
Used to convert image file's pixels into the appropriate in game representation (a block type and wether or not the player should increase the height of the column the pixel is part of to apply elevation shading to pixel on map)

## board_builder.py
Controls the player to place the image board in game. By doing this manually it can allow people to place images on servers and in survival mode (But only once I add tools to player_actions.py to manipulate the inventory so it can refill the inventory slots with blocks to place)

_A picture of a sphere placed in game using board_generator.py and board_builder.py_
![Example board](https://github.com/TrevorBivi/minecraft-tools/raw/master/example%20board.jpg "Example board")
