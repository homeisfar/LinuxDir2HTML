# LinuxDir2HTML

LinuxDir2HTML is a small program to help create an offline manifest of your files in an easily navigable html format. It is a CLI-only clone of [Snap2HTML](https://www.rlvision.com/snap2html/). LinuxDir2HTML is a rewrite of [DiogenesList](https://github.com/ZapperDJ/DiogenesList), making significant improvements to it:

- Python 3.6+
- Doesn't fail on symlinks (symlinks are ignored)
- More graceful invocation and sane usage
- Much, much, much faster
- Highly improved code

LinuxDir2HTML will produce essentially an identical output to Snap2HTML by using the same HTML template from that project.

## Installation
### Python PIP Install
Linux

    python -m pip install --user linuxdir2html

macOS

    python3 -m pip install --user linuxdir2html
### Basic Install
There are no external dependencies. If you do not wish to use pip, download `linuxdir2html.py` and `template.html`. Run the python directly.

## Usage
The program takes two mandatory arguments, the directory to be indexed and the output file name without the extension. So:

    linuxdir2html ~/Pictures output
 
will index the contents of `/home/Pictures` and save the index as `output.html` in the present working directory.

### Extra options

There are two optional flags. `--hidden` to include hidden files and directories, and `--links` to make the HTML link to the files directly.

By user request, newly introduced in v1.4.0 are a stacking `--startswith`and `--child` parameters. For example,

    linuxdir2html --startswith 'dev' --child 'Pictures' ~ ~/output

will select directories that start with 'dev' and the directory named 'Pictures' from the the user's home directory. The `--startswith` filter only affects the root search directory, all subdirectories and files will be indexed. The hidden flag is usable with the startswith flag.


## License
The LinuxDir2HTML.py file is licensed under GPLv2.

The template.html file Copyright (C) by Dan and is licensed as GPLv3.

## Notes

- There are no plans to implement a GUI.
- The up-to-date template uses epoch time and converts to your locale. If you'd like to change this behavior, update the JS function `timestampToDate` in the template.
- Certain characters like `\n` I've chosen to not implement handling for. In my humble opinion, just don't use new lines in file names :)
- Files with * in their names will not break the html output, but it may cause issues with the --links feature, and truncate the file names and cause minor metadata issues.
- LinuxDir2HTML requires Python 3.6 or greater, but if you modify the code to remove string interpolation and the barely used pathlib, the minimum required version will be much lower.

## Similar programs

I have long used an excellent program called [ncdu](https://dev.yorhel.nl/ncdu/man) to perform a similar function to WinDirStat or Disk Inventory X. I recently learned it has an export feature which you may find useful. Consider using it!

Export a directory and browse it once scanning is done:

    ncdu -o- ~/book | tee ~/ncduscan.file | ncdu -f-

Browse the contents of the file, without rescanning:

    ncdu -f ~/ncduscan.file