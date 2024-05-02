import os

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
        # generated attributes
        self.executable = self.isExecutable()

    def getName(self):
        return self.name
    
    def getOriginalPath(self):
        return self.originalPath
    
    def getBackupPath(self):
        return self.backupPath
    
    def getIndexPath(self):
        return self.indexPath

    def isExecutable(self):
        """
        Returns true if the profile is executable in the current system setup.
        @return boolean
        """
        originalPathExists = os.path.exists(self.originalPath)
        backupPathExists = os.path.exists(self.originalPath)
        indexPathExists = os.path.exists(self.indexPath)
        if (originalPathExists == False or backupPathExists == False or indexPathExists == False):
            return False
        return True
