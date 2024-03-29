from pathlib import Path
from indexfile import IndexFile
import time
import os
import datetime
import shutil
import traceback

from file import File

def readPreferences(path):
    """
    Read backup specific preferences file & return map.
    @param path - Path to the preferences file. 
    @return - Map containing the user preferences. 
    """
    preferences = {}

    try:
        prefFile = open(path,'r')
        for line in prefFile:
            if (line != '\n' and line.startswith('#') == False):
                splitLine = line.split('=')
                preferences.update({splitLine[0]:splitLine[1].strip('\n')})
            elif (line.startswith('#')):
                continue
    except (FileNotFoundError):
        return preferences
    finally:
        prefFile.close()
    
    return preferences

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

def backup(pathToOriginal,pathToBackup,pathToIndex):
    """
    Conduct backup procedure.
    @param pathToOriginal - Path to the files/directories to be backed up.
    @param pathToBackup - Path to where the backups will be stored.
    @param pathToIndex - Path to where the index file is store.
    """
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

    index = readIndex(pathToIndex)

    for dirpath, dirnames, files in os.walk(pathToOriginal):
        numOfDirectories += 1
        for file_name in files:
            fullPath = Path(dirpath + '/' + file_name)
            if (os.path.exists(fullPath) and os.path.islink(fullPath) == False):
                numOfFiles += 1
                currFile = File(fullPath)
                currFile.setStoredPath(pathToOriginal,pathToBackup)
                totalSize += currFile.st_size
                if (len(index.keys()) != 0):
                    indexSearchResult = index.get(currFile.st_ino,None)
                    if (indexSearchResult != None):
                        if (currFile.st_mtime_ns > indexSearchResult.st_mtime_ns):
                            indexWrites.append(currFile.getIndexPrint())
                            copyOperations.append(currFile.real_path + '{copy-operation-separator}' + currFile.stored_path)
                            copyOperationsSize += currFile.st_size
                            index.pop(currFile.st_ino, None)
                        elif (currFile.st_mtime_ns == indexSearchResult.st_mtime_ns):
                            indexWrites.append(currFile.getIndexPrint())
                            index.pop(currFile.st_ino, None)
                        if (currFile.newStoredPath(pathToOriginal, pathToBackup, indexSearchResult.stored_path)):
                            moveOperations.append(indexSearchResult.stored_path + '{move-op}' + currFile.stored_path)
                            moveOperationsSize += currFile.st_size
                            index.pop(currFile.st_ino, None)
                    else:
                        indexWrites.append(currFile.getIndexPrint())
                        copyOperations.append(currFile.real_path + '{copy-operation-separator}' + currFile.stored_path)
                        copyOperationsSize += currFile.st_size
                else:
                    indexWrites.append(currFile.getIndexPrint())
                    copyOperations.append(currFile.real_path + '{copy-operation-separator}' + currFile.stored_path)
                    copyOperationsSize += currFile.st_size
            elif (os.path.exists(fullPath) and os.path.islink(fullPath) == True):
                logger(f"backup() > Symlink Found: {fullPath}")
            elif(os.path.exists(fullPath) == False):
                logger(f"backup() > Path Does Not Exist: {fullPath}")
   
    logger('Remove deleted files')
    removeDeletedFiles(index)
    logger('Write updates to index.')
    writeToIndex(pathToIndex,indexWrites)
    logger(f"Move files to correct destinations ({round(moveOperationsSize/1000000,3)} MB)")
    moveFileStats = moveFiles(moveOperations)
    copyDirStats(moveFileStats)
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
        except (PermissionError):
            logger(f"copyFiles() > PermissionError: {source}")
        except (shutil.SameFileError):
            logger(f"copyFiles() > shutil.SameFileError: {source} {destination}")

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
    start = time.time()
    
    # conduct backup procedure
    logger('Reading preferences file')
    usrPrefs = readPreferences('preferences.txt')
    originalPath = Path(usrPrefs.get('originalPath'))
    backupPath = Path(usrPrefs.get('backupPath'))
    indexPath = Path(usrPrefs.get('indexPath'))
    logger('Begin backup process')
    try:
        backupResults = backup(originalPath,backupPath,indexPath)
        end = time.time()
        numOfFiles = f"Total Files Found: {backupResults.get('numOfFiles')}"
        numOfDirectories = f"Total Directories Found: {backupResults.get('numOfDirectories')}"
        totalSizeBytes = backupResults.get('totalSize')
        totalSizeMegaBytes = round(totalSizeBytes/1000000,3)
        totalSizeGigaBytes = round(totalSizeBytes/1000000000,3)
        totalSize = f"Total Size Of Original Files: {totalSizeBytes} bytes | {totalSizeMegaBytes} MB | {totalSizeGigaBytes} GB"
        totalTime = f"Total Program Execution Time: {round(end - start,3)} Seconds"
        logger(f"PROGRAM STATS:\n{numOfFiles}\n{numOfDirectories}\n{totalSize}\n{totalTime}")
    except:
        logger(f"Backup failed due to an error")
        traceback.print_exc()

    logger('MAIN METHOD COMPLETED')

main()
