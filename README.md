# LinuxDir2HTML

LinuxDir2HTML is a small program to help create an offline manifest of your files in an easily navigable html format. It is a CLI-only clone of [Snap2HTML](https://www.rlvision.com/snap2html/). LinuxDir2HTML is a rewrite of [DiogenesList](https://github.com/ZapperDJ/DiogenesList), making significant improvements to it:

- Python 3.6+
- Doesn't fail on symlinks (symlinks are ignored)
- More graceful invocation and sane usage
- Much, much, much faster
- Highly improved code

LinuxDir2HTML will produce essentially an identical output to Snap2HTML by using the same HTML template from that project.

## Installation
### Python PIP
Linux

    python -m pip install --user linuxdir2html

macOS

    python3 -m pip install --user linuxdir2html
### Basic
There are no external dependencies, so the file linuxdir2html.py could be downloaded and run directly.

## Usage
The program takes two mandatory arguments, the directory to be indexed and the output file name without the extension. So:

    linuxdir2html ~/Pictures output
 
will index the contents of /home/Pictures and save the index as output.html in the present working directory.

There are two optional flags. `--hidden` to include hidden files and directories, and `--links` to make the HTML link to the files directly.

By user request, newly introduced in v1.4.0 are a stacking `--startswith`and `--child` parameters. For example,

    linuxdir2html --startswith 'dev' --child 'Pictures' ~ ~/output

will select directories that start with 'dev' and the directory named 'Pictures' from the the user's home directory. The `--startswith` filter only affects the root search directory, all subdirectories and files will be indexed. The hidden flag is usable with the startswith flag.

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
