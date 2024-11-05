from file import File

class IndexFile(File):
    """
    ## IndexFile (Extends File)
    The IndexFile class is a File object that has been created by reading the
    index file. This is where information and metadata are stored, regarding
    files that are stored in the backup location for a profile.
    """
    def __init__(self, indexData: str):
        """
        Create indexFile object from data stored in the index file. 

        @type indexData: str
        @param indexData: Formatted string read from the `index.txt` file.
        """
        formattedMap = self.handleDataString(indexData)
        self.st_ino = int(formattedMap.get('st_ino'))
        self.real_path = formattedMap.get('real_path')
        self.stored_path = formattedMap.get('stored_path')
        self.st_mtime_ns = int(formattedMap.get('st_mtime_ns'))

    def handleDataString(self, indexString: str) -> dict[str, str]:
        """
        Returns a dictionary from the passed string, read from the index file.

        @type indexString: str
        @param indexString: `index.txt` file string to be parsed. 
        """
        separatorString = '[index-sep]'
        separatorCount = indexString.count(separatorString)
        if (separatorCount > 0):
            splitList = indexString.split(separatorString)
        else:
            splitList = indexString.split(',')

        returnMap = {}
        returnMap.update({'st_ino':splitList[0]})
        returnMap.update({'st_mtime_ns':splitList[1]})
        returnMap.update({'real_path':splitList[2]})
        returnMap.update({'stored_path':splitList[3].strip('\n')})

        return returnMap

    def getAll(self) -> dict[str, str]:
        """
        Returns dictionary with all instance attributes. 
        """
        returnMap = {
            'st_ino': self.st_ino,
            'real_path': self.real_path,
            'stored_path': self.stored_path,
            'st_mtime_ns': self.st_mtime_ns
        }

        return returnMap