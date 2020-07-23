# Licensed GPLv2
# Copyright (C) ZapperDJ    2017 https://github.com/ZapperDJ/DiogenesList
# Copyright (C) Ali Homafar 2020 https://github.com/homeisfar/LinuxDir2HTML

import os
import sys
import datetime
from os.path import getsize

# global variables definition
appName = "LinuxDir2HTML"
appVer = "1.1"
genDate = datetime.datetime.now().strftime("%m/%d/%Y")
genTime = datetime.datetime.now().strftime("%H:%M")
appLink = "https://github.com/homeisfar/LinuxDir2HTML"
dir_results = []
dirData = ""
numFiles=0 
numDirs=0 
grandTotalSize=0
linkFiles="false" # file linking not yet implemented

# functions definition
def generateDirArray(dirToScan):
    global dirData
    global numFiles
    global numDirs
    global grandTotalSize
    global dir_results
    # assign a number identifier to each directory
    i = 1
    dirIDsDictionary = {}
    dirIDsDictionary[dirToScan] = 0
    for currentDir, dirs, files in os.walk(dirToScan):
        for dir in dirs:
            full_dir_path = os.path.join(currentDir, dir)
            if os.path.islink(full_dir_path):
                continue
            if os.path.isdir(full_dir_path):
                dirIDsDictionary[full_dir_path] = i
                i = i + 1
    # Initialize array to hold all dir data, dimensioning it to hold the total number of dirs
    allDirArray=[]
    for p in range(i):
        allDirArray.append(p)

    # Traverse the directory tree
    for currentDir, dirs, files in os.walk(dirToScan):
        dirs = sorted(dirs, key=str.casefold)
        files = sorted(files, key=str.casefold)
        currentDirId=dirIDsDictionary[currentDir]
        currentDirArray=[]
        currentDirModifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(currentDir))
        currentDirModifiedTime = currentDirModifiedTime.strftime("%m/%d/%Y %H:%M:%S")
        currentDirFixed = currentDir.replace("/","\\\\")  # Replace / with \\ in the dir path (necessary for JavaScript functions to work properly)
        currentDirArray.append(currentDirFixed+'*0*'+currentDirModifiedTime)
        totalSize = 0
        for file in files:
            full_file_path = os.path.join(currentDir, file)
            # Don't count symlinks or other oddities
            if os.path.isfile(full_file_path):
                numFiles = numFiles + 1
                fileSize = getsize(full_file_path)
                totalSize = totalSize + fileSize
                grandTotalSize = grandTotalSize + fileSize
                fileModifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(full_file_path))
                fileModifiedTime = fileModifiedTime.strftime("%m/%d/%Y %H:%M:%S")
                currentDirArray.append(f'{file}*{fileSize}*{fileModifiedTime}')
        currentDirArray.append(totalSize)
        # Create the list of directory IDs correspondent to the subdirs present on the current directory
        # This acts as a list of links to the subdirectories on the JavaScript code
        dirLinks = ''
        for dir in dirs:
            full_dir_path = os.path.join(currentDir, dir)
            if os.path.islink(full_dir_path):
                continue
            numDirs = numDirs + 1
            dirLinks = dirLinks + str(dirIDsDictionary[full_dir_path]) + '*'
        dirLinks = dirLinks[:-1]    # remove last *
        currentDirArray.append(dirLinks)
        allDirArray[currentDirId]=currentDirArray

    # from allDirArray, generate the text to replace [DIR DATA] on HTML file
    #
    # dirData format:
    #
    #   dirs[DIRECTORY_ID] =
    #   "DIRECTORY_PATH*0*MODIFIED_TIME",
    #   "FILENAME*FILESIZE*MODIFIED_TIME",
    #   ...
    #   TOTAL_FILE_SIZE,
    #   "SUBDIRECTORY_ID*SUBDIRECTORY_ID*SUBDIRECTORY_ID*...",
    #   ];

    for d in range(len(allDirArray)):
        dirData = f"dirs[{d}] = [\n"
        for g in range(len(allDirArray[d])):
            if type(allDirArray[d][g]) == int:
                dirData += f"{allDirArray[d][g]},\n"
            else:
                dirData += f'"{allDirArray[d][g]}",\n'
        dirData += "];\n\n"
        dir_results.append(dirData)
    return


def generateHTML(dirData,appName,appVer,genDate,genTime,title,appLink,numFiles,numDirs,grandTotalSize,linkFiles):
    templateFile = open(os.path.join(sys.path[0], 'template.html'), 'r')
    outputFile = open(f'{title}.html', 'w')
    for line in templateFile:
        modifiedLine = line
        if '[DIR DATA]' in modifiedLine:
            for line in dir_results:
                outputFile.write(line)
            continue
        modifiedLine = modifiedLine.replace('[APP NAME]', appName)
        modifiedLine = modifiedLine.replace('[APP VER]', appVer)
        modifiedLine = modifiedLine.replace('[GEN DATE]', genDate)
        modifiedLine = modifiedLine.replace('[GEN TIME]', genTime)
        modifiedLine = modifiedLine.replace('[TITLE]', title)
        modifiedLine = modifiedLine.replace('[APP LINK]', appLink)
        modifiedLine = modifiedLine.replace('[NUM FILES]', str(numFiles))
        modifiedLine = modifiedLine.replace('[NUM DIRS]', str(numDirs))
        modifiedLine = modifiedLine.replace('[TOT SIZE]', str(grandTotalSize))
        modifiedLine = modifiedLine.replace('[LINK FILES]', linkFiles)
        outputFile.write(modifiedLine)
    templateFile.close()
    outputFile.close()
    print("Wrote output to: " + os.path.realpath(outputFile.name))

# main program start point
if len(sys.argv) < 3:
    print("Missing arguments. This tool should be used as follows:")
    print("     LinuxDir2HTML pathToIndex outputFileName")
else:
    pathToIndex = str(sys.argv[1])
    title = str(sys.argv[2])
    if os.path.exists(pathToIndex):
        pathToIndex = os.path.abspath(pathToIndex)
        print("Indexing directories...")
        generateDirArray(pathToIndex)
        print("Outputting HTML...")
        generateHTML(dirData,appName,appVer,genDate,genTime,title,appLink,numFiles,numDirs,grandTotalSize,linkFiles)
    else:
        print("The specified directory doesn't exist. Aborting.")
