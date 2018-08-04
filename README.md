# minecraft-tools
A variety of useful tools for minecraft that are mainly focused on automating player actions.

__board_builder.py__
Controls the player to place the image board in game. By doing this manually it can allow people to place images on servers and in survival mode (But only once I add tools to player_actions.py to manipulate the inventory so it can refill the inventory slots with blocks to place)

_A picture of a sphere placed in game using board_generator.py and board_builder.py. 5 different block types were used which with elevation shading allows for 10 different colors_
![Example board](https://github.com/TrevorBivi/minecraft-tools/raw/master/example%20board.jpg "Example board")

__read_memory.py__
Contains functions for reading game memory addresses to gather information about the player.

__world_generator.py__
Used to auto generate worlds and search for desirable world traits within up to 32 chunks of spawn. Contains example functions for searching for world that has an ocean ravine very close to a sunken ship and contains a jungle.

__board_generator.py__
Used to convert an image such as a .png or .jpg into the appropriate in game representation (a block type and wether or not the player should increase the height of the column the pixel is part of to apply elevation shading to pixel on map)

__read_save_file.py__
Contains functions for reading block states of the game world from chunk save data. Tested on 1.13 and 1.12 save formats. Should support as far back as 1.3

__player_actions.py__
Contains functions to control player. Clicks and keyboard presses can be performed while the game is in the background. Actions that require moving the mouse need the window to be in focus.
