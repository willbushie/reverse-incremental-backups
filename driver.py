# package imports
from pathlib import Path

# local imports
from file import File

def main():
    print("MAIN METHOD STARTING----")
    
    originalFile = File(Path('./test env/original/test.txt'))
    backupFile = File(Path('./test env/backup/test.txt'))
    backupDir = File(Path('./test env/backup'))

    print(originalFile.getAll())
    print(backupFile.getAll())
    print(backupDir.getAll())




main()