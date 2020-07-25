# Licensed GPLv2
# Copyright (C) ZapperDJ    2017 https://github.com/ZapperDJ/DiogenesList
# Copyright (C) Ali Homafar 2020 https://github.com/homeisfar/LinuxDir2HTML

import argparse
import datetime
import os
from pathlib import Path

# Mostly variables to feed into template.html
appName     = "LinuxDir2HTML"
app_ver     = "1.2"
gen_date    = datetime.datetime.now().strftime("%m/%d/%Y")
gen_time    = datetime.datetime.now().strftime("%H:%M")
app_link    = "https://github.com/homeisfar/LinuxDir2HTML"
dir_data    = ""
total_numFiles  = 0 
total_numDirs   = 0 
grand_total_size= 0
file_links      = "false"
link_protocol   = "file://"
include_hidden  = False
dir_results     = []
# linkRoot = "/"

parser = argparse.ArgumentParser(description='Generate HTML view of file system.\n')
parser.add_argument('pathToIndex')
parser.add_argument('outputfile')
parser.add_argument('--hidden',
                    help='Include hidden files (leading with .)',
                    action="store_true")
parser.add_argument('--links', help='Create links to files in HTML output',
                    action="store_true")

def generateDirArray(root_dir): # root i.e. user-provided root path, not "/"
    global dir_data
    global total_numFiles
    global total_numDirs
    global grand_total_size
    global dir_results
    i = 0
    dirs_dictionary = {}
    
    # We enumerate every unique directory, ignoring symlinks.
    for currentDir, dirs, files in os.walk(root_dir):
        if include_hidden is False:
            dirs[:] = [d for d in dirs if not d[0] == '.']
            files = [f for f in files if not f[0] == '.']

        dirs = sorted(dirs, key=str.casefold)
        files = sorted(files, key=str.casefold)

        # The values in the dictionary are as follows.
        # |  0 |      1     |         2           |    3     |
        # | id | file_attrs | dir total file size | sub dirs |
        # [1] leads with the current directory path and modification time, and 
        # is followed by the directory's files and their attibutes.
        # Id is unused but could be useful for future features.
        dirs_dictionary[currentDir] = [i, [], 0, '']
        arr = dirs_dictionary[currentDir][1]
        dir_mod_time = int(datetime.datetime.fromtimestamp(os.path.getmtime(currentDir)).timestamp())
        arr.append(f'{currentDir}*0*{dir_mod_time}')

        ##### FILES #####
        total_size = 0
        for file in files:
            full_file_path = os.path.join(currentDir, file)
            if os.path.isfile(full_file_path):
                total_numFiles  += 1
                file_size        = os.path.getsize(full_file_path)
                total_size      += file_size
                grand_total_size += file_size
                mod_time    = datetime.datetime.fromtimestamp(os.path.getmtime(full_file_path))
                mod_time    = int(mod_time.timestamp())
                arr.append(f'{file}*{file_size}*{mod_time}')
        dirs_dictionary[currentDir][2] = total_size

        ##### DIRS #####
        dir_links = ''
        for dir in dirs:
            full_dir_path = os.path.join(currentDir, dir)
            if os.path.isdir(full_dir_path) and not os.path.islink(full_dir_path):
                i += 1
                total_numDirs += 1
                dirs_dictionary[full_dir_path] = (i, [], '')
                dir_links += f'{i}*'
        dirs_dictionary[currentDir][3] = dir_links[:-1]

    ## OUTPUT
    # Format
    # "FILE_PATH*0*MODIFIED_TIME","FILE_NAME*FILE_SIZE*MODIFIED_TIME",DIR_SIZE,"DIR1*DIR2..."
    for entry in dirs_dictionary:
        dir_data = f'D.p(['
        for data in dirs_dictionary[entry][1]:
            dir_data += f'"{data}",'
        dir_data += f'{dirs_dictionary[entry][2]},"{dirs_dictionary[entry][3]}"])\n'
        dir_results.append(dir_data)
    return

def generateHTML(
    dir_data, appName, app_ver,
    gen_date, gen_time, title,
    app_link, numFiles, numDirs,
    grand_total_size, file_links):
    templateFile = open(os.path.join(os.sys.path[0], 'template.html'), 'r')
    outputFile = open(f'{title}.html', 'w')
    for line in templateFile:
        modifiedLine = line
        if '[DIR DATA]' in modifiedLine:
            # I've seen one file from Steam with a crazy name...
            for line in dir_results:
                sane_format = line.replace('\r', '')
                outputFile.write(f'{sane_format}')
            continue
        modifiedLine = modifiedLine.replace('[APP NAME]', appName)
        modifiedLine = modifiedLine.replace('[APP VER]', app_ver)
        modifiedLine = modifiedLine.replace('[GEN DATE]', gen_date)
        modifiedLine = modifiedLine.replace('[GEN TIME]', gen_time)
        modifiedLine = modifiedLine.replace('[TITLE]', title)
        modifiedLine = modifiedLine.replace('[APP LINK]', app_link)
        modifiedLine = modifiedLine.replace('[NUM FILES]', str(numFiles))
        modifiedLine = modifiedLine.replace('[NUM DIRS]', str(numDirs))
        modifiedLine = modifiedLine.replace('[TOT SIZE]', str(grand_total_size))
        modifiedLine = modifiedLine.replace('[LINK FILES]', file_links)
        modifiedLine = modifiedLine.replace('[LINK PROTOCOL]', link_protocol)
        modifiedLine = modifiedLine.replace('[SOURCE ROOT]', '')
        modifiedLine = modifiedLine.replace('[LINK ROOT]', '')
        outputFile.write(modifiedLine)
    templateFile.close()
    outputFile.close()
    print("Wrote output to: " + os.path.realpath(outputFile.name))

# main program start point
args = parser.parse_args()
pathToIndex = args.pathToIndex
title = args.outputfile
if args.links:
    file_links = "true"
if args.hidden:
   include_hidden = True
if not os.path.exists(pathToIndex):
    print("The specified directory doesn't exist. Aborting.")
    exit(1)

pathToIndex = Path(pathToIndex).resolve()
print("Indexing directories...")
generateDirArray(pathToIndex)
print("Outputting HTML...")
generateHTML(
    dir_data,appName,app_ver,gen_date,gen_time,title,app_link,
    total_numFiles,total_numDirs,grand_total_size,file_links)
