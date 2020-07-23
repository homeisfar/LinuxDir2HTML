# LinuxDir2HTML

LinuxDir2HTML is a CLI-only clone of [Snap2HTML](https://www.rlvision.com/snap2html/). It is directly based on [DiogenesList](https://github.com/ZapperDJ/DiogenesList) but makes significant improvements.

- Python 3.6+
- Doesn't fail on symlinks (symlinks are ignored)
- More graceful invocation and sane usage
- Much, much, much faster

This program will produce essentially an identical output to Snap2HTML - using the freely available template provided.

## Usage
The program only takes two arguments, the directory to be indexed and the output file name without the extension, so:

 *python diogeneslist.py ~/Pictures output*
 
Will index the contents of /home/Pictures and save them to the present working directory in an easy-to-use html file.

Note this requires Python3.6 or greater, but if you modify the python to remove string interpolation the minimum version will be lower.

## License
The LinuxDir2HTML.py file is licensed under GPLv2.

The template.html file Copyright (C) by Dan and is licensed as GPLv3.

## Issues (Wishlist)
The original Python code was not well-implemented. I've made essentially the minimum efforts needed to improve upon it, but have plans to continue making improvements, but no timeline to do so.

The template HTML is based on an old version, and I'd like to update the output to use the latest available version from Snap2HTML. This will improve the search functionality, among other things.

File links in the HTML are not implemented, and might never be.

I'd also like to include an option to ignore hidden files.

There are no plans to implement a GUI.

As an American, I prefer MM/DD/YYYY. Sorry!
