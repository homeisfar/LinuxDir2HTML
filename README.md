# LinuxDir2HTML

LinuxDir2HTML is a CLI-only clone of [Snap2HTML](https://www.rlvision.com/snap2html/). It is directly based on [DiogenesList](https://github.com/ZapperDJ/DiogenesList), making significant improvements to it.

- Python 3.6+
- Doesn't fail on symlinks (symlinks are ignored)
- More graceful invocation and sane usage
- Much, much, much faster
- Highly improved code

This program will produce essentially an identical output to Snap2HTML - using the same template from that project.

## Usage
The program takes two mandatory arguments, the directory to be indexed and the output file name without the extension. So:

    python diogeneslist.py ~/Pictures output
 
will index the contents of /home/Pictures and save them to the present working directory in an easy-to-use html file.

The two optional flags are `--hidden` to include hidden files and directories, and `--links` to make the HTML link to the files.

Note LinuxDir2HTML requires Python 3.6 or greater, but if you modify the Python to remove string interpolation and the barely used pathlib, the minimum version will be lower.

## License
The LinuxDir2HTML.py file is licensed under GPLv2.

The template.html file Copyright (C) by Dan and is licensed as GPLv3.

## Issues (Wishlist)

Nice. I did everything I set out to do. These are all fixed/improved:

[X] The original Python code was not well-implemented. I've made essentially the minimum efforts needed to improve upon it, but have plans to continue making improvements, but no timeline to do so.

[X] The template HTML is based on an old version, and I'd like to update the output to use the latest available version from Snap2HTML. This will improve the search functionality, among other things.

[X] File links in the HTML are not implemented.

[X] I'd also like to include an option to ignore hidden files.

[X] There are no plans to implement a GUI.

[X] ~~As an American, I prefer MM/DD/YYYY. Sorry!~~ The up-to-date template uses epoch time.
