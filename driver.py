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
    indexWrites = []

    index = readIndex(indexPath)

    for dirpath, dirnames, files in os.walk(originalPath):
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
                                copyOperations.append(currFile.real_path + '{copy-operation-separator}' + currFile.stored_path)
                                copyOperationsSize += currFile.st_size
                            elif (currFile.st_mtime_ns == indexSearchResult.st_mtime_ns):
                                indexWrites.append(currFile.getIndexPrint())
                        else:
                            indexWrites.append(currFile.getIndexPrint())
                            copyOperations.append(currFile.real_path + '{copy-operation-separator}' + currFile.stored_path)
                            copyOperationsSize += currFile.st_size
                    else:
                        indexWrites.append(currFile.getIndexPrint())
                        copyOperations.append(currFile.real_path + '{copy-operation-separator}' + currFile.stored_path)
                        copyOperationsSize += currFile.st_size
                else:
                    # handle file not found error (should continue if the file does not exist)
                    # print('FileNotFoundError:', fullPath)
                    logger(f"backup() > FileNotFoundError: {fullPath}")
        else:
            del dirnames[:]
   
    logger('Write updates to index.')
    writeToIndex(indexPath,indexWrites)
    logger(f"Copy files to backup destination ({round(copyOperationsSize/1000000,3)} MB)")
    copyStatDirs = copyFiles(copyOperations)
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

def copyFiles(operations):
    """
    Conduct all copy operations held within a list.
    @param operations - List containing "<original path>,<stored path>" strings.
    @return - Map containing the source and destinations for directory attribute copies to occur.
    Note: On Windows, some metadata will not be retained. See [here](https://docs.python.org/3/library/shutil.html) for more information.
    """
    copyStatDirs = {}
    operationsNum = len(operations)
    operationsCompleted = 0

    for copy in operations:
        operationList = copy.split('{copy-operation-separator}')
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
        except (FileNotFoundError):
            logger(f"copyFiles() > FileNotFoundError: {source}")
            continue
        except (PermissionError):
            logger(f"copyFiles() > PermissionError: {source}")
            continue

    logger(f"Operations Completed: {operationsCompleted}/{operationsNum}")
    return copyStatDirs

def copyDirStats(dirMap):
    """
    Copies directory stats/attributes from source dirs to destination dirs given a map. 
    @param dirMap - Dictionary containing the sources and destinations for copying (syncing) dir stats.
    """
    keys = dirMap.keys()
    for key in keys:
        currVal = dirMap.get(key)
        shutil.copystat(key,currVal)


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
        except:
            logger(f"Profile backup failed due to an error.")
            traceback.print_exc()

    programEnd = time.time()
    logger(f"PROGRAM RUNTIME: {round(programEnd - programStart, 3)} Seconds")
    logger('MAIN METHOD COMPLETED')

main()
