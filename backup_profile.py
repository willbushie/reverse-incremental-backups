import os
from pathlib import Path

class Profile:
    def __init__(self, map):
        """"""
        missingAttributes = []
        # required profile attributes
        self.name = map.get('name')
        if self.name == None: missingAttributes.append('name')
        self.originalPath = map.get('originalPath')
        if self.originalPath == None: missingAttributes.append('originalPath')
        self.backupPath = map.get('backupPath')
        if self.backupPath == None: missingAttributes.append('backupPath')
        self.indexPath = map.get('indexPath')
        if self.indexPath == None: missingAttributes.append('indexPath')
        if (len(missingAttributes) > 0):
            raise KeyError(f'Missing Profile Attributes: {missingAttributes}')
        # optional profile attributes
        self.description = map.get('description')
        self.blacklist = self.generateBlacklist(map.get('blacklist'))
        # generated attributes
        self.executable = self.isExecutable()

    def generateBlacklist(self, blacklistString):
        """
        Generate a list of files/directories to avoid from a string.
        @param blacklistString - String from profiles that lists items to blacklist.
        @param list
        """
        originalPathItems = os.listdir(self.originalPath)
        blacklist = []
        if (blacklistString != None):
            items = blacklistString.split(',')
            for item in items:
                if (item in originalPathItems):
                    fullPath = os.path.join(self.originalPath, item)
                    dir = os.path.basename(fullPath)
                    blacklist.append(dir)
                else:
                    # make user aware of non-existent path?
                    continue
        return blacklist

    def getName(self):
        return self.name
    
    def getOriginalPath(self):
        return self.originalPath
    
    def getBackupPath(self):
        return self.backupPath
    
    def getIndexPath(self):
        return self.indexPath
    
    def getBlacklist(self):
        return self.blacklist
    
    def getRequired(self):
        """
        Returns dictionary of required profile attributes.
        @return dict
        """
        returnDict = {
            'Name': self.name,
            'Original Path': self.originalPath,
            'Backup Path': self.backupPath,
            'Index Path': self.indexPath
        }
        return returnDict

    def isExecutable(self):
        """
        Returns true if the profile is executable in the current system setup.
        @return boolean
        """
        try:
            self.createIndexFile()
        except PermissionError:
            return False

        originalPathExists = os.path.exists(self.originalPath)
        backupPathExists = os.path.exists(self.originalPath)
        indexPathExists = os.path.exists(self.indexPath)
        if (originalPathExists == False or backupPathExists == False or indexPathExists == False):
            return False
        return True
    
    def createIndexFile(self):
        """
        Creates index file and parent path if it does not already exist.
        """
        fullPath = Path(self.indexPath)
        dirPath = fullPath.parent
        if not dirPath.exists():
            dirPath.mkdir(parents=True, exist_ok=True)
        fullPath.touch()
