from file import File

class IndexFile(File):
    def __init__(self,indexData):
        """
        Constructor for index. Object created from data stored in the index file.
        """
        formattedMap = self.handleDataString(indexData)
        self.st_ino = int(formattedMap.get('st_ino'))
        self.real_path = formattedMap.get('real_path')
        self.stored_path = formattedMap.get('stored_path')
        self.st_mtime_ns = int(formattedMap.get('st_mtime_ns'))

    def handleDataString(self,indexString):
        """
        Creates a map from the passed string, read from the index file.
        @param indexString - String read from the index file.
        @return - Return map with indexed file attributes.
        """
        splitList = indexString.split(',')
        returnMap = {}

        returnMap.update({'st_ino':splitList[0]})
        returnMap.update({'st_mtime_ns':splitList[1]})
        returnMap.update({'real_path':splitList[2]})
        returnMap.update({'stored_path':splitList[3]})

        return returnMap

    def getAll(self):
        """
        Returns all instance attributes.
        """
        returnMap = {
            'st_ino': self.st_ino,
            'real_path': self.real_path,
            'stored_path': self.stored_path,
            'st_mtime_ns': self.st_mtime_ns
        }

        return returnMap
