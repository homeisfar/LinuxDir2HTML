# LinuxDir2HTML

LinuxDir2HTML is a small program to help create an offline manifest of your files in an easily navigable html format. It is a CLI-only clone of [Snap2HTML](https://www.rlvision.com/snap2html/). LinuxDir2HTML is based on [DiogenesList](https://github.com/ZapperDJ/DiogenesList), but makes significant improvements to it.

- Python 3.6+
- Doesn't fail on symlinks (symlinks are ignored)
- More graceful invocation and sane usage
- Much, much, much faster
- Highly improved code

This program will produce essentially an identical output to Snap2HTML - using the same template from that project.

## Installation
### Python PIP
Linux

    python -m pip install --user linuxdir2html

macOS

    python3 -m pip install --user linuxdir2html
### Basic
Just download this repository and run the linuxdir2html.py file directly.

## Usage
The program takes two mandatory arguments, the directory to be indexed and the output file name without the extension. So:

    linuxdir2html ~/Pictures output
 
will index the contents of /home/Pictures and save the index as output.html in the present working directory.

There are two optional flags. `--hidden` to include hidden files and directories, and `--links` to make the HTML link to the files.

Newly introduced in v1.4.0 is a stacking `--startswith` parameter. For example,

    linuxdir2html --startswith 'dev' --startswith 'l' ~ ~/output

will select directories that start with 'd' and the directory named Example from the ~ directory. This processing only affects the root search directory. The result will be saved as output.html in ~. The hidden flag is usable with the startswith flag.

Note LinuxDir2HTML requires Python 3.6 or greater, but if you modify the Python to remove string interpolation and the barely used pathlib, the minimum version will be much lower.

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

[X] The up-to-date template uses epoch time and converts to your locale. If you'd like to change this behavior, update the JS function `timestampToDate` in the template.
