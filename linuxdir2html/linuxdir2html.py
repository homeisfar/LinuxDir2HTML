# Licensed GPL-3.0-only
# Copyright (C) Ali Homafar 2020-2026 https://github.com/homeisfar/LinuxDir2HTML

# Short Changelog
# v1.3.0             - Initial release
# v1.4.0 (Aug. 2020) - Safety, logging, and --startswith and --child options.
# v1.5.0 (Oct. 2022) - Write errors fix (thanks Jarvis-3-0). Handle " in filenames.
# v1.6.0 (Dec. 2022) - Introduce the --symlink and --silent options.
# v1.6.1 (Mar. 2025) - Fixed lingering issues w.r.t. certain file names breaking the output.
#                    - Fixed issues with files or directories which do not have read rights.
# v2.0.0 (Apr. 2026) - Refactored code. Remove the --startswith and --child flags. Add --include, --exclude.

# Prior to v1.6.1, symlinked filesizes were erroneously counted as the full files.
# Now symlinked files are counted for the size of the symlink itself is. If the symlink
# points to a non-file then it probably will not be in the output (e.g. the wine drive_c dir).
# v1.6.1 finally fixes files with new lines and * breaking the output.

import argparse
import datetime
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

# Application constants
APP_NAME = "LinuxDir2HTML"
APP_VER  = "2.0.0"
APP_URL  = "https://github.com/homeisfar/LinuxDir2HTML"

@dataclass
class Config:
    """Holds all configuration and accumulated state."""
    # Input/Output
    path_to_index: Path = None
    output_file: str = ""

    # Filter options
    include_hidden: bool = False
    follow_symlink: bool = False
    exclude_pattern: str = ""
    include_pattern: str = ""
    dexclude_pattern: str = ""
    dinclude_pattern: str = ""

    # HTML output options
    file_links: str = "false" # This is a string because it's outputted in the html template.
    links_protocol: str = "file://"

    # Results & accumulators
    dir_results = []
    total_num_files = 0
    total_num_dirs = 0
    grand_total_size = 0
    
    # Metadata
    gen_date = datetime.datetime.now().strftime("%m/%d/%Y")
    gen_time = datetime.datetime.now().strftime("%H:%M")

def parse_args_and_prepare_program() -> Config:
    parser = argparse.ArgumentParser(description='Generate HTML view of the file system.\n')
    parser.add_argument('pathToIndex', help='Path of directory to index.')
    parser.add_argument('outputfile', help='Name of report file (without .html)')
    parser.add_argument('--exclude', help='Exclude files which match this regex pattern.')
    parser.add_argument('--include', help='Only include files which match this regex pattern.')
    parser.add_argument('--dexclude', help='Exclude directories which match this regex pattern.')
    parser.add_argument('--dinclude', help='Only include directories which match this regex pattern.')
    parser.add_argument('--hidden', help='Include hidden files (leading with .)', action="store_true")
    parser.add_argument('--links', help='Create links to files in HTML output', action="store_true")
    # parser.add_argument('--links_protocol', help='Change the links protocol. By default it is file://, ' +
    # 'but you can provide your own protocol. Use with --links.', default='file://')
    parser.add_argument('--symlink', help='Follow symlinks. WARN: This can cause infinite loops.', action="store_true")
    parser.add_argument('-v', '--verbose', help='increase output verbosity. -v, or -vv for more.', action="count")
    parser.add_argument('--silent', help='Suppress terminal output, except on error.', action="store_true")
    parser.add_argument('--version', help='Print version and exit', action="version", version=APP_VER)

    args = parser.parse_args()

    cfg = Config(
        path_to_index=Path(args.pathToIndex).resolve(),
        output_file=args.outputfile,
        include_hidden=args.hidden,
        follow_symlink=args.symlink,
        exclude_pattern=args.exclude,
        include_pattern=args.include,
        dexclude_pattern=args.dexclude,
        dinclude_pattern=args.dinclude,
        file_links="true" if args.links else "false"
        # links_protocol=args.links_protocol
    )

    # Initialize Logging
    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.DEBUG if args.verbose > 1 else logging.INFO
    if args.silent:
        log_level = logging.ERROR
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level=log_level)

    # Validation
    if not cfg.path_to_index.exists():
        logging.error(f"Directory to index [{cfg.path_to_index}] doesn't exist. Aborting.")
        exit(1)
    if Path(cfg.output_file).is_dir():
        logging.error(f"Chosen output file [{cfg.output_file}] is a directory. Aborting.")
        exit(1)

    if cfg.follow_symlink:
        logging.warn("Please be aware following symlinks can cause circular infinite loops.")

    return cfg

def main():
    cfg = parse_args_and_prepare_program()
    
    logging.info(f"Setting: file links is [{cfg.file_links}]")
    logging.info(f"Setting: hidden items is [{cfg.include_hidden}]")
    logging.info(f"Settings: following symlink is [{cfg.follow_symlink}]")

    logging.warning(f'Indexing: [{cfg.path_to_index}]')
    generateDirArray(cfg)
    logging.info('Outputting HTML...')
    generateHTML(cfg)
    return
        
def generateDirArray(cfg: Config):
    dir_id = 0
    dirs_dictionary = {}
    
    # Enumerate every directory, ignoring symlinks by default.
    for current_dir, dirs, files in os.walk(cfg.path_to_index, True, None, cfg.follow_symlink):
        logging.debug( f'Walking Dir [{current_dir}]')
        
        if not cfg.include_hidden:
            dirs[:] = [d for d in dirs if not d[0] == '.']
            files = [f for f in files if not f[0] == '.']

        dirs = sorted(dirs, key=str.casefold)
        files = sorted(files, key=str.casefold)

        # The key is the current dir, and the value is described as follows.
        # A four index array like so:
        # |  0 |      1     |         2           |    3     |
        # | id | file_attrs | dir total file size | sub dirs |
        # [1] is an array with the current directory path and modification time, then 
        # is followed by the directory's files. Each file has a size and modtime.
        # Id is unused but could be useful for future features.
        # The null character, \0, is the delimiter between entries
        dirs_dictionary[current_dir] = [dir_id, [], 0, '']
        arr = dirs_dictionary[current_dir][1]
        dir_mod_time = int(os.path.getmtime(current_dir))
        arr.append(f'{json.dumps(current_dir)[1:-1]}\0000\0{dir_mod_time}')

        ##### Enumerate FILES #####
        total_size = 0
        for file in files:
            full_file_path = os.path.join(current_dir, file)
            if cfg.exclude_pattern and re.search(cfg.exclude_pattern, file):
                continue
            if cfg.include_pattern and not re.search(cfg.include_pattern, file):
                continue
            
            if os.path.isfile(full_file_path):
                cfg.total_num_files += 1
                file_size = os.path.getsize(full_file_path)
                if (os.path.islink(full_file_path)):
                    file_size = os.lstat(full_file_path).st_size
                total_size += file_size
                cfg.grand_total_size += file_size
                mod_time = int(os.path.getmtime(full_file_path))
                arr.append(f'{json.dumps(file)[1:-1]}\0{file_size}\0{mod_time}')
        dirs_dictionary[current_dir][2] = total_size

        ##### Enumerate DIRS #####
        dir_links = ''
        for dir in dirs:
            if cfg.dexclude_pattern and re.search(cfg.dexclude_pattern, dir):
                continue
            if cfg.dinclude_pattern and not re.search(cfg.dinclude_pattern, dir):
                continue

            full_dir_path = os.path.join(current_dir, dir)
            if (not cfg.follow_symlink and os.path.isdir(full_dir_path) and not os.path.islink(full_dir_path)) or \
                    (cfg.follow_symlink and os.path.isdir(full_dir_path)):
                dir_id += 1
                cfg.total_num_dirs += 1
                dirs_dictionary[full_dir_path] = [dir_id, [dir], 0, '']
                dir_links += f'{dir_id}\0'
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
        cfg.dir_results.append(dir_data)
    return

def generateHTML(cfg: Config):
    template_file = open((Path(__file__).parent / 'template.html'), 'r', encoding="utf-8")
    output_file = open(f'{cfg.output_file}.html', 'w', encoding="utf-8", errors='xmlcharrefreplace')

    for line in template_file:
        if '[DIR DATA]' in line:
            output_file.writelines(cfg.dir_results)
            continue

        line = line.replace('[APP NAME]', APP_NAME)
        line = line.replace('[APP VER]', APP_VER)
        line = line.replace('[GEN DATE]', cfg.gen_date)
        line = line.replace('[GEN TIME]', cfg.gen_time)
        line = line.replace('[TITLE]', cfg.output_file)
        line = line.replace('[APP LINK]', APP_URL)
        line = line.replace('[NUM FILES]', str(cfg.total_num_files))
        line = line.replace('[NUM DIRS]', str(cfg.total_num_dirs))
        line = line.replace('[TOT SIZE]', str(cfg.grand_total_size))
        line = line.replace('[LINK FILES]', cfg.file_links)
        line = line.replace('[LINK PROTOCOL]', cfg.links_protocol)
        line = line.replace('[SOURCE ROOT]', '')
        line = line.replace('[LINK ROOT]', '')
        output_file.write(line)

    template_file.close()
    output_file.close()
    logging.warning("Wrote output to: " + os.path.realpath(output_file.name))
    return

if __name__ == '__main__':
    main()
