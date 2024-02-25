from pathlib import Path
from indexfile import IndexFile
import time
import os
import datetime
import shutil

from file import File

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

def logger(logFile, message=''):
    """
    Send a message to a specific log file.
    @param logFile - File to write the log to.
    @param message (optional) - message to include in the log.
    """
    currTime = datetime.datetime.now()
    timestampString = f"[{currTime.strftime("%Y-%m-%d %H:%M:%S %z")}]"
    file = open(logFile,'w')
    file.write(f"{timestampString} {message}")
    file.close()
    print('logger called and completed')

def main():
    """
    Only method to be called.
    """
    print("MAIN METHOD STARTING----\n")

    start = time.time()
    
    # conduct backup procedure
    originalPath = Path('./test env/original')
    backupPath = Path('./test env/backup')
    indexPath = Path('./index.txt')
    backupResults = backup(originalPath,backupPath,indexPath)
    
    end = time.time()

    # show program statitics
    print('\nPROGRAM STATISTICS-----')
    print(f"total files found: {backupResults.get('numOfFiles')}")
    print(f"total directories found: {backupResults.get('numOfDirectories')}")
    print(f"total size of all files found: {backupResults.get('totalSize')} bytes ({round(backupResults.get('totalSize')/1000000,2)} MB | {round(backupResults.get('totalSize')/1000000000,2)} GB)")
    print(f"program execution time: {round(end - start, 3)} (Seconds)")
    print("MAIN METHOD COMPLETED----")

main()
