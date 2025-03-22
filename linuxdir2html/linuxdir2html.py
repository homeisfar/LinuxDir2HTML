# Licensed GPL-3.0-only
# Copyright (C) Ali Homafar 2020-2025 https://github.com/homeisfar/LinuxDir2HTML
# Contributions Bruce Riddle 2020

# Short Changelog
# v1.3.0             - Initial release
# v1.4.0 (Aug. 2020) - Safety, logging, and --startswith and --child options.
# v1.5.0 (Oct. 2022) - Write errors fix (thanks Jarvis-3-0). Handle " in filenames.
# v1.6.0 (Dec. 2022) - Introduce the --symlink and --silent options.
# v1.6.1 (Mar. 2025) - Fixed lingering issues w.r.t. certain file names breaking the output.
#                    - Fixed issues with files or directories which do not have read rights.
# v1.7.0 (Planned) - Remove the --startswith and --child flags. I've never liked these.

# Prior to v1.6.1 symlinks filesizes were erroneously counted as the full files.
# Now symlinked files are counted for however long the symlink itself is. If the symlink
# points to a non-file then it probably will not be in the output (e.g. wine drive_c dir).
# v1.6.1 finally fixes files with new lines and * breaking the output.

import argparse
import datetime
import json
import logging
import os
from pathlib import Path
import re

# Most of the following variables are to replace placeholders in template.html
appName = "LinuxDir2HTML"
app_ver = "1.6.1"
gen_date = datetime.datetime.now().strftime("%m/%d/%Y")
gen_time = datetime.datetime.now().strftime("%H:%M")
app_link = "https://github.com/homeisfar/LinuxDir2HTML"
dir_data = ""
total_numFiles = 0
total_numDirs = 0
grand_total_size = 0
file_links = "false"  # This is a string b/c it's used in the html template.
link_protocol = ""
include_hidden = False
follow_symlink = False
dir_results = []
childList_names = []  # names supplied from --child options
startsList_names = []  # dir's generated from --startsfrom options

parser = argparse.ArgumentParser(description='Generate HTML view of the file system.\n')
parser.add_argument('pathToIndex', help='Path of Directory to Index')
parser.add_argument('outputfile', help='Name of report file (without .html)')
parser.add_argument('--child', action='append', help='[DEPRECATED] Exact name(s) of children directories to include')
parser.add_argument('--startswith', action='append', help='[DEPRECATED] Start of name(s) of children dirs to include')
parser.add_argument('--hidden', help='Include hidden files (leading with .)', action="store_true")
parser.add_argument('--links', help='Create links to files in HTML output', action="store_true")
parser.add_argument('--protocol', help='Protocol used for links (used with --links)', default="http://")
parser.add_argument('--symlink', help='Follow symlinks. WARN: This can cause infinite loops.', action="store_true")
parser.add_argument('-v', '--verbose', help='increase output verbosity. -v or -vv for more.', action="count")
parser.add_argument('--silent', help='Suppress terminal output except on error.', action="store_true")
parser.add_argument('--version', help='Print version and exit', action="version", version=app_ver)


def main():
    global include_hidden, file_links, childList_names, startsList_names, follow_symlink, link_protocol
    args = parser.parse_args()

    ## Initialize logging facilities
    log_level = logging.WARNING
    if args.verbose:
        if args.verbose > 1:
            log_level = logging.DEBUG
        elif args.verbose == 1:
            log_level = logging.INFO
    if args.silent:
        log_level = logging.ERROR
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level=log_level)
    log_name = logging.getLevelName(logging.getLogger().getEffectiveLevel())
    logging.info(f'Logging Level {log_name}')

    # Handle user input flags and options
    pathToIndex = args.pathToIndex
    title = args.outputfile
    if args.links:
        file_links = "true"
        link_protocol = args.protocol
        logging.info(f"Using protocol for links: {link_protocol}")

    if args.hidden:
        include_hidden = True
    if args.symlink:
        follow_symlink = True
        logging.warning(f"Please be aware following symlinks can cause circular infinite loops.")
    if not os.path.exists(pathToIndex):
        logging.error(f"Directory specified to index [{pathToIndex}] doesn't exist. Aborting.")
        exit(1)
    if os.path.isdir(title):
        logging.error(f"Chosen output file [{title}] is a directory. Aborting.")
        exit(1)
    logging.info(f"Creating file links is [{file_links}]")
    logging.info(f"Showing hidden items is [{include_hidden}]")
    logging.info(f"Following symlinks is [{follow_symlink}]")

    # check that no child or startswith arg include a path separator
    for child_val in args.child or []:
        if os.sep in child_val:
            logging.error(f"child argument [{child_val}] contains a path separator.")
            exit(1)
        childList_names.append(os.path.normcase(child_val))
    for start_val in args.startswith or []:
        if os.sep in start_val:
            logging.error(f"startswith argument [{start_val}] contains a path separator.")
            exit(1)
        startsList_names.append(os.path.normcase(start_val))
    # Time to do the real work. Generate array with our file & dir entries,
    # then generate the resulting HTML
    pathToIndex = Path(pathToIndex).resolve()
    logging.warning(f'Root index directory: [{pathToIndex}]')
    generateDirArray(pathToIndex)
    logging.info('Outputting HTML...')
    generateHTML(
        dir_data, appName, app_ver, gen_date, gen_time, title, app_link,
        total_numFiles, total_numDirs, grand_total_size, file_links
    )
    return


def generateDirArray(root_dir):  # root i.e. user-provided root path, not "/"
    global dir_data, total_numFiles, total_numDirs, grand_total_size, \
        dir_results, childList_names, startsList_names
    id = 0
    dirs_dictionary = {}

    # Convert root_dir to string for path operations
    root_str = str(root_dir)
    # Ensure root_str does end with a separator to properly build path
    if not root_str.endswith(os.sep):
        root_str += os.sep

    # We enumerate every unique directory, ignoring symlinks by default.
    first_iteration = True
    for current_dir, dirs, files in os.walk(root_dir, True, None, follow_symlink):
        logging.debug(f'Walking Dir [{current_dir}]')

        # If --child or --startswith are used, only add the requested
        # directories. This will only be performed on the root_dir
        if first_iteration:
            first_iteration = False
            if childList_names or startsList_names:
                selectDirs(current_dir, dirs, include_hidden)
                files = []
        if include_hidden is False:
            dirs[:] = [d for d in dirs if not d[0] == '.']
            files = [f for f in files if not f[0] == '.']
        dirs = sorted(dirs, key=str.casefold)
        files = sorted(files, key=str.casefold)

        # Create a relative path by removing root_dir from current_dir
        rel_dir = str(current_dir)
        if rel_dir.startswith(root_str):
            rel_dir = rel_dir[len(root_str):]
        elif rel_dir == root_str[:-1]:  # If it's the root directory itself
            rel_dir = "/"

        if not rel_dir.startswith("/"):
            rel_dir = "/" + rel_dir

        # The key is the current dir, and the value is described as follows.
        # A four index array like so:
        # |  0 |      1     |         2           |    3     |
        # | id | file_attrs | dir total file size | sub dirs |
        # [1] is an array with the current directory path and modification time, then
        # is followed by the directory's files. Each file has a size and modtime.
        # Id is unused but could be useful for future features.
        dirs_dictionary[current_dir] = [id, [], 0, '']
        arr = dirs_dictionary[current_dir][1]
        dir_mod_time = int(
            datetime.datetime.fromtimestamp(
                os.path.getmtime(current_dir)).timestamp())
        arr.append(f'{json.dumps(rel_dir)[1:-1]}\0000\0{dir_mod_time}')
        ##### Enumerate FILES #####
        total_size = 0
        for file in files:
            full_file_path = os.path.join(current_dir, file)

            if os.path.isfile(full_file_path):
                total_numFiles += 1
                file_size = os.path.getsize(full_file_path)
                if (os.path.islink(full_file_path)):
                    file_size = os.lstat(full_file_path).st_size
                total_size += file_size
                grand_total_size += file_size
                try:  # Avoid possible invalid mtimes
                    mod_time = int(datetime.datetime.fromtimestamp
                                   (os.path.getmtime(full_file_path)).timestamp())
                except:
                    logging.warning(f'----fromtimestamp timestamp invalid [{full_file_path}]')
                    mod_time = 1
                arr.append(f'{json.dumps(file)[1:-1]}\0{file_size}\0{mod_time}')
        dirs_dictionary[current_dir][2] = total_size
        ##### Enumerate DIRS #####
        dir_links = ''
        for dir in dirs:
            full_dir_path = os.path.join(current_dir, dir)
            if (not follow_symlink and os.path.isdir(full_dir_path) and not os.path.islink(full_dir_path)) or \
                    (follow_symlink and os.path.isdir(full_dir_path)):
                id += 1
                total_numDirs += 1
                dirs_dictionary[full_dir_path] = [id, [dir], 0, '']
                dir_links += f'{id}\0'
        dirs_dictionary[current_dir][3] = dir_links[:-1]
    ## Output format follows:
    # "FILE_PATH\00\0MODIFIED_TIME","FILE_NAME\0FILE_SIZE\0MODIFIED_TIME",DIR_SIZE,"DIR1\0DIR2..."
    # To get a practical sense of what this means, look at a generated output after using the program.
    for entry in dirs_dictionary:
        logging.debug(f'entry in dirs_dictionary [{str(entry)}]')
        dir_data = f'D.p(['
        for data in dirs_dictionary[entry][1]:
            dir_data += f'"{data}",'
        dir_data += f'{dirs_dictionary[entry][2]},"{dirs_dictionary[entry][3]}"])\n'
        dir_results.append(dir_data)
    return


# This function will execute only on the first iteration of the directory walk.
# It only has an effect if --child or --startswith are used.
def selectDirs(current_dir, dirs, include_hidden):
    if childList_names:
        logging.warning(f'Using dirs Named [{str(childList_names)[1:-1]}]')
    hidden_dirs = []
    if startsList_names:
        logging.warning(f'Using dirs starting with [{str(startsList_names)[1:-1]}]')
        if include_hidden:
            hidden_dirs = ["." + d for d in startsList_names]
            logging.warning(f'Hidden flag set. Using dirs starting with [{str(hidden_dirs)[1:-1]}]')

    desired_dirs = startsList_names + hidden_dirs
    for i in range(len(dirs) - 1, -1, -1):
        keep_dir = '?'
        for desired in desired_dirs:
            if re.match(desired, dirs[i], re.I) or dirs[i] in childList_names:
                keep_dir = 'Y'
        if keep_dir != 'Y':
            logging.debug('..Unselecting: %s', dirs[i])
            del dirs[i]
    logging.info(f'Dirs selected:\n{dirs}')
    return


def generateHTML(
        dir_data, appName, app_ver, gen_date, gen_time, title,
        app_link, numFiles, numDirs, grand_total_size, file_links
):
    template_file = open((Path(__file__).parent / 'template.html'), 'r', encoding="utf-8")
    output_file = open(f'{title}.html', 'w', encoding="utf-8", errors='xmlcharrefreplace')
    for line in template_file:
        modified_line = line
        if '[DIR DATA]' in modified_line:
            for line in dir_results:
                try:  # can error if encoding mismatch; can't fix, just report
                    # TODO: investigate if the above is true after v1.6.1
                    output_file.write(f'{line}')
                except:
                    logging.warning(f'----output_file.write error [{line}]')
            continue
        modified_line = modified_line.replace('[APP NAME]', appName)
        modified_line = modified_line.replace('[APP VER]', app_ver)
        modified_line = modified_line.replace('[GEN DATE]', gen_date)
        modified_line = modified_line.replace('[GEN TIME]', gen_time)
        modified_line = modified_line.replace('[TITLE]', title)
        modified_line = modified_line.replace('[APP LINK]', app_link)
        modified_line = modified_line.replace('[NUM FILES]', str(numFiles))
        modified_line = modified_line.replace('[NUM DIRS]', str(numDirs))
        modified_line = modified_line.replace('[TOT SIZE]', str(grand_total_size))
        modified_line = modified_line.replace('[LINK FILES]', file_links)
        modified_line = modified_line.replace('[LINK PROTOCOL]', link_protocol)
        modified_line = modified_line.replace('[SOURCE ROOT]', '')
        modified_line = modified_line.replace('[LINK ROOT]', '')
        output_file.write(modified_line)
    template_file.close()
    output_file.close()
    logging.warning("Wrote output to: " + os.path.realpath(output_file.name))
    return


if __name__ == '__main__':
    main()