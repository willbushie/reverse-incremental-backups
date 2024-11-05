from pathlib import Path
import time
import os
import datetime
import shutil
import traceback

from file import File
from indexfile import IndexFile
from backup_profile import Profile
from tracker import Tracker

def readPreferences(path: str) -> dict[str, str]:
    """
    Read `preferences.txt` and return a dictionary with the preferences.

    @type path: str
    @param path: Path to the `preferences.txt` file.
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

def readProfiles(path: str) -> dict[str, list[Profile]]:
    """
    Read `profiles.txt` file and return a dictionary containing both a list
    of the executable profiles, and a list of all profiles. 

    @type path: str
    @param path: Path to the `profiles.txt` file. 
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

def readIndex(path: str) -> dict[str, IndexFile]:
    """
    Read the index file, create IndexFile objects with the stored metadata,
    and returns a dictionary.

    @type path: str
    @param path: Path to the `index.txt` file.
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

def backup(profile: Profile) -> dict[str, int]:
    """
    Conduct backup procedure for a given profile and return a statistical
    summary dictionary.

    @type profile: Profile
    @param profile: Desired profile string the backup should reference.
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
    tracker = Tracker(indexCount)

    print('Walking through files...')
    for dirpath, dirnames, files in os.walk(originalPath):
        if (indexCount > 0):
            tracker.progressBar(numOfFiles)
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
        tracker.setComplete()
        tracker.progressBar(numOfFiles)
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

def restore() -> None:
    """
    Conduct restore procedure.
    """
    return None

def writeToIndex(path: str, data: list[str]) -> None:
    """
    Write to `index.txt` with the new IndexFile data. 

    @type path: str
    @param path: Path to the `index.txt` file. 
    @type data: list[str]
    @param data: List of strings to write to the `index.txt` file. 

    *Note: If the index file does not exist, it will be generated at the provided path.*
    """
    file = open(path,'w')

    for line in data:
        file.write(line + '\n')
    
    file.close()

def moveFiles(operations: list[str]) -> dict[str, str]:
    """
    Given a list of operations `["/old/stored/path,/new/stored/path",..]`, try to move
    the files from the old location to the new location (to match source structure).

    @type operations: list[str]
    @param operations: List of strings describing move operations. 
    
    *Note: On Windows, some metadata will not be retained.
    See [here](https://docs.python.org/3/library/shutil.html) for more information.*
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

def copyFiles(operations: list[str], size: int) -> dict[str, str]:
    """
    Given a list of strings `["/original/path{custom-separator}/stored/path"]` and
    the total number of bytes to copy, copy the files from source location to the
    backup location. 

    @type operations: list[str]
    @param operations: List of strings describing copy operations.
    @type size: int
    @param size: Total number of operations to be completed. 

    *Note: On Windows, some metadata will not be retained.
    See [here](https://docs.python.org/3/library/shutil.html) for more information.*
    """
    copyStatDirs = {}
    operationsNum = len(operations)
    operationsCompleted = 0
    currSizeComplete = 0
    tracker = Tracker(size)

    print('Copying files...')
    for copy in operations:
        tracker.progressBar(currSizeComplete, data=True)
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

    tracker.setComplete()
    tracker.progressBar(currSizeComplete, data=True)
    logger(f"Copy Operations Completed: {operationsCompleted}/{operationsNum}")
    return copyStatDirs

def removeDeletedFiles(index: dict[str, IndexFile]) -> None:
    """
    Remove the deleted source files from the backup location. 

    @type index: dict[str, IndexFile]
    @param index: Dictionary of index files that need to be removed. 
    """
    files = index.values()
    for indexFileObject in files:
        os.remove(indexFileObject.stored_path)

def copyDirStats(dirMap: dict[str, str]) -> None:
    """
    Copies directory stats/attributes from source directories to destination 
    directories from the passed dictionary. 

    @type dirMap: dict[str, str]
    @param dirMap:
    """
    print('Copying directory stats...')
    keys = dirMap.keys()
    for key in keys:
        currVal = dirMap.get(key)
        shutil.copystat(key,currVal)

def logger(message: str = '') -> None:
    """
    Writes a formatted log message to a specified log file. 

    @type message: str
    @param message: Message to be logged. 
        (Default is `''`)
    """
    currTime = datetime.datetime.now()
    # timestampString = f"[{currTime.strftime("%Y-%m-%d %H:%M:%S %z")}]" # UTC offset does not display
    timestampString = f"[{currTime.strftime('%Y-%m-%d %H:%M:%S')}]"
    file = open('backup.log','a+')
    file.write(f"{timestampString} {message}\n")
    file.close()

def main() -> None:
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
