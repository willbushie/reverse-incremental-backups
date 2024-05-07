from pathlib import Path
from indexfile import IndexFile
import time
import os
import datetime
import shutil
import traceback

from file import File
from backup_profile import Profile

def readPreferences(path):
    """
    Read the application preferences.
    @param path - Path to preferences file.
    @return - Dictionary containing the application preferences.
    """
    specialChars = ['\n', '#']
    preferences = {}

    try:
        prefFile = open(path,'r')
        for line in prefFile:
            firstChar = line[0]
            if (firstChar not in specialChars):
                splitLine = line.split('=')
                preferences.update({splitLine[0]:splitLine[1].strip('\n')})
    except (FileNotFoundError):
        raise FileNotFoundError
    
    prefFile.close()
    return preferences

def readProfiles(path):
    """
    Read backup profiles file & return a list of executable profiles,
    in the order they are to be executed.
    @param path - Path to the profile file. 
    @return - Dictionary that contains a list of executable profiles
    in addition to a list of all profiles.
    """
    specialChars = ['\n', '#', '=']
    profiles = {'executable':[], 'all':[]}
    profile = {}

    try:
        profileFile = open(path,'r')
        for line in profileFile:
            firstChar = line[0]
            if (firstChar not in specialChars):
                splitLine = line.split('=')
                profile.update({splitLine[0]:splitLine[1].strip('\n')})
            elif (firstChar == '='):
                tempProfile = Profile(profile)
                profiles.get('all').append(tempProfile)
                if (tempProfile.executable == True):
                    profiles.get('executable').append(tempProfile)
                profile.clear()
        tempProfile = Profile(profile)
        profiles.get('all').append(tempProfile)
        if (tempProfile.executable == True):
            profiles.get('executable').append(tempProfile)
    except (FileNotFoundError):
        raise FileNotFoundError

    profileFile.close()
    return profiles

def readIndex(path):
    """
    Read the current index file, creating File objects and adding them to an
    index to be held in memory for quick searching. 
    @param path - Path to the index file.
    @return - Returns indexed map of index files.
    """
    Index = {}

    try:
        indexFile = open(path,'r')
        for line in indexFile:
            if (line != '\n'):
                currIndexFile = IndexFile(line)
                Index.update({currIndexFile.st_ino:currIndexFile})
    except (FileNotFoundError):
        return Index
    finally:
        indexFile.close()

    return Index

def backup(profile):
    """
    Conduct backup procedure.
    @param profile - Backup Profile object.
    @return dict
    """
    # profile attributes
    indexPath = profile.getIndexPath()
    originalPath = profile.getOriginalPath()
    backupPath = profile.getBackupPath()
    blacklist = profile.getBlacklist()

    # used for program statistics
    numOfDirectories = 0
    numOfFiles = 0
    totalSize = 0

    # used to store future operations
    copyOperations = []
    copyOperationsSize = 0
    moveOperations = []
    moveOperationsSize = 0
    indexWrites = []

    index = readIndex(indexPath)
    indexCount = len(index)

    print('Walking through files...')
    for dirpath, dirnames, files in os.walk(originalPath):
        if (indexCount > 0):
            progressBar(indexCount, numOfFiles, label='Files')
        else:
            print(f"{numOfFiles} Files Found", end='\r')
        if (not any(path in dirpath for path in blacklist)):
            numOfDirectories += 1
            for file_name in files:
                fullPath = Path(dirpath + '/' + file_name)
                if (os.path.exists(fullPath)):
                    numOfFiles += 1
                    currFile = File(fullPath)
                    currFile.setStoredPath(originalPath,backupPath)
                    totalSize += currFile.st_size
                    if (len(index.keys()) != 0):
                        indexSearchResult = index.get(currFile.st_ino,None)
                        if (indexSearchResult != None):
                            if (currFile.st_mtime_ns > indexSearchResult.st_mtime_ns):
                                indexWrites.append(currFile.getIndexPrint())
                                copyOperations.append({'paths':currFile.real_path + '{copy-operation-separator}' + currFile.stored_path,'size':currFile.st_size})
                                copyOperationsSize += currFile.st_size
                            elif (currFile.st_mtime_ns == indexSearchResult.st_mtime_ns):
                                indexWrites.append(currFile.getIndexPrint())
                        else:
                            indexWrites.append(currFile.getIndexPrint())
                            copyOperations.append({'paths':currFile.real_path + '{copy-operation-separator}' + currFile.stored_path,'size':currFile.st_size})
                            copyOperationsSize += currFile.st_size
                    else:
                        indexWrites.append(currFile.getIndexPrint())
                        copyOperations.append({'paths':currFile.real_path + '{copy-operation-separator}' + currFile.stored_path,'size':currFile.st_size})
                        copyOperationsSize += currFile.st_size
                else:
                    # handle file not found error (should continue if the file does not exist)
                    # print('FileNotFoundError:', fullPath)
                    logger(f"backup() > FileNotFoundError: {fullPath}")
        else:
            del dirnames[:]
    
    if (indexCount > 0):
        progressBar(indexCount, numOfFiles, label='Files', complete=True)
    else:
        print(f"{numOfFiles} Files Found {' ' * 10}")
   
    logger('Write updates to index.')
    writeToIndex(indexPath,indexWrites)
    logger(f"Move files to correct destinations ({round(moveOperationsSize/1000000,3)} MB)")
    moveFileStats = moveFiles(moveOperations)
    copyDirStats(moveFileStats)
    logger(f"Copy files to backup destination ({round(copyOperationsSize/1000000,3)} MB)")
    copyStatDirs = copyFiles(copyOperations, copyOperationsSize)
    copyDirStats(copyStatDirs)

    return {
        'numOfDirectories': numOfDirectories,
        'numOfFiles': numOfFiles,
        'totalSize': totalSize
    }

def restore():
    """
    Conduct restore procedure.
    """
    return None

def writeToIndex(path,data):
    """
    Conduct all writes to the index file from data held in a list. The index file will
    be created if it does not already exist. 
    @param path - Path to where the index file is held/desired to be placed.
    @param data - List containing strings of line data to write to the index file.
    """
    file = open(path,'w')

    for line in data:
        file.write(line + '\n')
    
    file.close()

def moveFiles(operations):
    """
    Conduct all move operations in the backup location (to match source location).
    @param operations - List containing "<old stored path>,<new stored path>" strings.
    @return - Map containing the source and destinations for directory attributes copies to occur.
    Note: On Windows, some metadata will not be retained. See [here](https://docs.python.org/3/library/shutil.html) for more information.
    """
    moveStatsDirs = {}
    operationsNum = len(operations)
    operationsCompleted = 0

    for move in operations:
        operationList = move.split('{move-op}')
        oldStoredLoc = operationList[0]
        newStoredLoc = operationList[1]
        oldStoredLocHead = os.path.split(oldStoredLoc)[0]
        newStoredLocHead = os.path.split(newStoredLoc)[0]
        try:
            os.makedirs(newStoredLocHead,exist_ok=True)
            if (moveStatsDirs.get(oldStoredLoc,None) == None):
                moveStatsDirs.update({oldStoredLocHead:newStoredLocHead})
        except:
            logger(f"moveFiles() > Error creating directories | move: {move}")
            traceback.print_exc()
        try:
            shutil.move(oldStoredLoc,newStoredLoc)
            operationsCompleted += 1
        except (FileNotFoundError):
            logger(f"moveFiles() > FileNotFoundError: {newStoredLoc}")
            continue
        except (PermissionError):
            logger(f"moveFiles() > PermissionError: {newStoredLoc}")
            continue
    
    logger(f"Move Operations Completed {operationsCompleted}/{operationsNum}")
    return moveStatsDirs

def copyFiles(operations, size):
    """
    Conduct all copy operations held within a list.
    @param operations - List containing "<original path>{custom-separator}<stored path>" strings.
    @param size - Int of bytes for total copy operations.
    @return - Dict containing the source and destinations for directory attribute copies to occur.
    Note: On Windows, some metadata will not be retained. See [here](https://docs.python.org/3/library/shutil.html) for more information.
    """
    copyStatDirs = {}
    operationsNum = len(operations)
    operationsCompleted = 0
    currSizeComplete = 0

    print('Copying files...')
    for copy in operations:
        progressBar(round(size/1000,2),round(currSizeComplete/1000,2),label='KB')
        paths = copy.get('paths')
        operationList = paths.split('{copy-operation-separator}')
        source = operationList[0]
        destination = operationList[1]
        sourcePathHead = os.path.split(source)
        destPathHead = os.path.split(destination)
        try:
            os.makedirs(destPathHead[0],exist_ok=True)
            if (copyStatDirs.get(sourcePathHead[0],None) == None):
                copyStatDirs.update({sourcePathHead[0]:destPathHead[0]})
        except:
            logger(f"copyFiles() > Error created directories | operationList: {operationList}")
            traceback.print_exc()
        try:
            shutil.copy2(source,destination)
            operationsCompleted += 1
            currSizeComplete += copy.get('size')
        except (FileNotFoundError):
            logger(f"copyFiles() > FileNotFoundError: {source}")
        except (PermissionError):
            logger(f"copyFiles() > PermissionError: {source}")
        except (shutil.SameFileError):
            logger(f"copyFiles() > shutil.SameFileError: {source} {destination}")

    progressBar(round(size/1000,2),round(currSizeComplete/1000,2),label='KB', complete=True)
    logger(f"Copy Operations Completed: {operationsCompleted}/{operationsNum}")
    return copyStatDirs

def removeDeletedFiles(index):
    """
    Remove deleted source files from the backup.
    @param index - index dictionary created in backup()
    """
    files = index.values()
    for indexFileObject in files:
        os.remove(indexFileObject.stored_path)

def copyDirStats(dirMap):
    """
    Copies directory stats/attributes from source dirs to destination dirs given a map. 
    @param dirMap - Dict containing the sources and destinations for copying (syncing) dir stats.
    """
    print('Copying directory stats...')
    keys = dirMap.keys()
    for key in keys:
        currVal = dirMap.get(key)
        shutil.copystat(key,currVal)

def progressBar(total, current, label='', complete=False):
    """
    Show a progress bar for amount of data moving/copying.
    @param total - Total copy/move data amount (in MB).
    @param current - Current total of copied/moved data amount (in MB).
    """
    barLength = 30
    filledLength = int(barLength * current / total)
    bar = ('=' * filledLength) + ' ' * (barLength - filledLength)
    if (complete):
        print(f"[{'=' * 30}] {total}/{total} {label} (100.0%) {' ' * 20}")
    else:
        print(f"[{bar}] {current}/{total} {label} ({round((current/total) * 100,1)}%) {' ' * 20}", end='\r')

def logger(message=''):
    """
    Send a message to a specific log file.
    @param message (optional) - message to include in the log.
    """
    currTime = datetime.datetime.now()
    # timestampString = f"[{currTime.strftime("%Y-%m-%d %H:%M:%S %z")}]" # UTC offset does not display
    timestampString = f"[{currTime.strftime('%Y-%m-%d %H:%M:%S')}]"
    file = open('backup.log','a+')
    file.write(f"{timestampString} {message}\n")
    file.close()

def main():
    """
    Only method to be called.
    """
    open('backup.log','w').close()

    logger('MAIN METHOD STARTING')
    programStart = time.time()
    
    # conduct backup procedure
    logger('Reading preferences file')
    try:
        # profiles = readProfiles('profiles.txt')
        prefs = readPreferences('preferences.txt')
    except FileNotFoundError:
        logger('Error reading preferences.txt. May be missing or is named incorrectly.')
        print('Error reading preferences.txt. May be missing or is named incorrectly.')
        exit()
    try:
        profiles = readProfiles(prefs.get('profiles'))
    except FileNotFoundError:
        logger('Error reading profiles file. May be missing or is named incorrectly.')
        print('Error reading profiles file. May be missing or is named incorrectly.')
    for profile in profiles.get('executable'):
        print(f"Executing '{profile.getName()}' ({profiles.get('executable').index(profile) + 1}/{len(profiles.get('executable'))})")
        start = time.time()
        logger(f"Begin backup process for profile {profile.getName()}")
        try:
            backupResults = backup(profile)
            end = time.time()
            numOfFiles = f"Total Files Found: {backupResults.get('numOfFiles')}"
            numOfDirectories = f"Total Directories Found: {backupResults.get('numOfDirectories')}"
            totalSizeBytes = backupResults.get('totalSize')
            totalSizeMegaBytes = round(totalSizeBytes/1000000,3)
            totalSizeGigaBytes = round(totalSizeBytes/1000000000,3)
            totalSize = f"Total Size Of Original Files: {totalSizeBytes} bytes | {totalSizeMegaBytes} MB | {totalSizeGigaBytes} GB"
            totalTime = f"Total Profile Execution Time: {round(end - start,3)} Seconds"
            logger(f"PROFILE STATS:\n{numOfFiles}\n{numOfDirectories}\n{totalSize}\n{totalTime}")
            print(f"PROFILE STATS:\n{numOfFiles}\n{numOfDirectories}\n{totalSize}\n{totalTime}")
        except:
            logger(f"Profile backup failed due to an error.")
            traceback.print_exc()

    programEnd = time.time()
    logger(f"PROGRAM RUNTIME: {round(programEnd - programStart, 3)} Seconds")
    logger('MAIN METHOD COMPLETED')

if (__name__ == '__main__'):
    main()
