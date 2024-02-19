from pathlib import Path
import time
import os

from file import File


def backup():
    """
    Conduct backup procedure.
    """
    return None

def restore():
    """
    Conduct restore procedure.
    """
    return None

def main():
    """
    Main process that handles all possible actions. 
    """
    start = time.time()
    print("MAIN METHOD STARTING----\n")
    
    # originalFile = File(Path('./test env/original/test.txt'))
    # backupFile = File(Path('./test env/backup/test.txt'))
    # backupDir = File(Path('./test env/backup'))

    # print(originalFile.getAll())
    # print(backupFile.getAll())
    # print(backupDir.getAll())

    numOfFiles = 0
    numOfDirectories = 0
    totalSize = 0

    # memory held queues
    Index = {}
    Files = []

    indexFileLarge = open('./index-large.txt','w')
    indexFileSmall = open('./index-small.txt','w')
    for dirpath, dirnames, files in os.walk('./test env'):
        # print(f'Found directory: {dirpath}')
        numOfDirectories += 1
        for file_name in files:
            numOfFiles += 1
            full_file_path = Path(dirpath + "/" + file_name)
            if (os.path.exists(full_file_path)):
                currFile = File(full_file_path)
            else:
                print('file not found:',full_file_path) 
            totalSize += currFile.st_size
            Files.append(currFile)
            Index.update({currFile.st_ino: currFile})
            indexFileLarge.write(f"{currFile.getAll()}\n")
            indexFileSmall.write(f"{currFile.st_ino},{currFile.st_mtime_ns}")
            # print(file_name)
            # print(full_file_path)
    indexFileLarge.close()
    indexFileSmall.close()

    # add new line to second file
    # time.sleep(1)
    # print(Files[1].st_mtime_ns, ' - original last modification time')
    # file = open(Files[1].real_path,'a')
    # file.write('\nnew data')
    # file.close()
    # print(os.stat(Files[1].passed_path).st_mtime_ns,' - open, close, and write')
    # # time.sleep(1)
    # file = open(Files[1].real_path,'a')
    # file.close()
    # print(os.stat(Files[1].passed_path).st_mtime_ns, ' - open and close, no modifications')

    # for file in Files:
    #     fileFromIndex = Index.get(file.st_ino)
    #     if (fileFromIndex.st_mtime_ns != file.st_mtime_ns):
    #         print('files do not match')
    #         print('index file: ',fileFromIndex.getAll())
    #         print('current file: ',file.getAll())
    #     else: 
    #         print('modification times match',fileFromIndex.st_mtime_ns,'|',file.st_mtime_ns)
        
    end = time.time()
    indexFileLargeSize = os.stat('./index-large.txt').st_size
    indexFileSmallSize = os.stat('./index-small.txt').st_size
    print(f"size of large index file: {indexFileLargeSize} bytes ({round(indexFileLargeSize/1000000)} MB)")
    print(f"size of small index file: {indexFileSmallSize} bytes ({round(indexFileSmallSize/1000000)} MB)")
    print('PROGRAM STATISTICS-----')
    print(f"total files found: {numOfFiles}")
    print(f"total directories found: {numOfDirectories}")
    print(f"total size of all files found: {totalSize} bytes ({round(totalSize/1000000,2)} MB | {round(totalSize/1000000000,2)} GB)")
    print(f"program execution time: {round(end - start, 3)} (Seconds)")
    print("MAIN METHOD COMPLETED----")

main()
