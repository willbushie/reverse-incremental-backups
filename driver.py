from pathlib import Path
from indexfile import IndexFile
import time
import os
import datetime
import shutil

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
    indexWrites = []

    index = readIndex(pathToIndex)

    for dirpath, dirnames, files in os.walk(pathToOriginal):
        numOfDirectories += 1
        for file_name in files:
            fullPath = Path(dirpath + '/' + file_name)
            if (os.path.exists(fullPath)):
                numOfFiles += 1
                currFile = File(fullPath)
                currFile.setStoredPath(pathToOriginal,pathToBackup)
                totalSize += currFile.st_size
                if (len(index.keys()) != 0):
                    indexSearchResult = index.get(currFile.st_ino,None)
                    if (indexSearchResult != None):
                        if (currFile.st_mtime_ns > indexSearchResult.st_mtime_ns):
                            indexWrites.append(currFile.getIndexPrint())
                            copyOperations.append(currFile.real_path + ',' + currFile.stored_path)
                            copyOperationsSize += currFile.st_size
                        elif (currFile.st_mtime_ns == indexSearchResult.st_mtime_ns):
                            indexWrites.append(indexSearchResult.getIndexPrint())
                    else:
                        indexWrites.append(currFile.getIndexPrint())
                        copyOperations.append(currFile.real_path + ',' + currFile.stored_path)
                        copyOperationsSize += currFile.st_size
                else:
                    indexWrites.append(currFile.getIndexPrint())
                    copyOperations.append(currFile.real_path + ',' + currFile.stored_path)
                    copyOperationsSize += currFile.st_size
            else:
                # handle file not found error (should continue if the file does not exist)
                print('FileNotFoundError:', fullPath)
   
    writeToIndex(pathToIndex,indexWrites)
    copyFiles(copyOperations)

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
    Note: On Windows, some metadata will not be retained. See [here](https://docs.python.org/3/library/shutil.html) for more information.
    """
    for copy in operations:
        operationList = copy.split(',')
        source = operationList[0]
        destination = operationList[1]
        destPathHead = os.path.split(destination)
        os.makedirs(destPathHead[0],exist_ok=True)
        shutil.copy2(source,destination)

def logger(message=''):
    """
    Send a message to a specific log file.
    @param message (optional) - message to include in the log.
    """
    currTime = datetime.datetime.now()
    # timestampString = f"[{currTime.strftime("%Y-%m-%d %H:%M:%S %z")}]" # UTC offset does not display
    timestampString = f"[{currTime.strftime("%Y-%m-%d %H:%M:%S")}]"
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
    usrPrefs = readPreferences('preferences.txt')
    originalPath = Path(usrPrefs.get('originalPath'))
    backupPath = Path(usrPrefs.get('backupPath'))
    indexPath = Path(usrPrefs.get('indexPath'))
    print(f"usrPrefs: {originalPath}, {backupPath}, {indexPath}")
    backupResults = backup(originalPath,backupPath,indexPath)
    
    end = time.time()

    # show program statistics
    numOfFiles = f"Total Files Found: {backupResults.get('numOfFiles')}"
    numOfDirectories = f"Total Directories Found: {backupResults.get('numOfDirectories')}"
    totalSizeBytes = backupResults.get('totalSize')
    totalSizeMegaBytes = round(totalSizeBytes/1000000,3)
    totalSizeGigaBytes = round(totalSizeBytes/1000000000,3)
    totalSize = f"Total Size Of Original Files: {totalSizeBytes} bytes | {totalSizeMegaBytes} MB | {totalSizeGigaBytes} GB"
    totalTime = f"Total Program Execution Time: {round(end - start),3} Seconds"
    logger(f"PROGRAM STATS:\n{numOfFiles}\n{numOfDirectories}\n{totalSize}\n{totalTime}")
    
    logger('MAIN METHOD COMPLETED')

main()
