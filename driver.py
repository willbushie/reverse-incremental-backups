# package imports
from pathlib import Path
import time
import os

# local imports
from file import File

def main():
    start = time.time()
    print("MAIN METHOD STARTING----")
    
    # originalFile = File(Path('./test env/original/test.txt'))
    # backupFile = File(Path('./test env/backup/test.txt'))
    # backupDir = File(Path('./test env/backup'))

    # print(originalFile.getAll())
    # print(backupFile.getAll())
    # print(backupDir.getAll())

    numOfFiles = 0
    numOfDirectories = 0
    totalSize = 0

    for dirpath, dirnames, files in os.walk('./test env'):
        # print(f'Found directory: {dirpath}')
        numOfDirectories += 1
        for file_name in files:
            full_file_path = Path(dirpath + "/" + file_name)
            totalSize += os.stat(full_file_path).st_size
            numOfFiles += 1
            # print(file_name)
            # print(full_file_path)

    end = time.time()
    print(f"total files found: {numOfFiles}")
    print(f"total directories found: {numOfDirectories}")
    print(f"total size of all files found: {totalSize} bytes ({totalSize/1000000} MB | {totalSize/1000000000} GB)")
    print(f"program execution time: {round(end - start, 3)} (Seconds)")
    print("MAIN METHOD COMPLETED----")

main()
