import os

class File:
    def __init__(self,path):
        """
        ## File constructor
        Takes a path which is used to gather detailed information on the file.
        This class should not be used when reading from the index file.
        ## TODO
        - If there is a path passed that does not exist, the program should be
        able to handle that.
        """
        self.passed_path = path
        self.real_path = os.path.realpath(self.passed_path)
        self.is_dir = os.path.isdir(self.real_path)
        self.stored_path = ''
        # https://docs.python.org/3/library/os.html#os.stat
        stats = os.stat(self.passed_path)
        self.st_mode = stats.st_mode
        self.st_ino = stats.st_ino
        self.st_dev = stats.st_dev
        self.st_uid = stats.st_uid
        self.st_gid = stats.st_gid
        self.st_size = stats.st_size
        self.st_nlink = stats.st_nlink
        self.st_atime = stats.st_atime
        self.st_mtime = stats.st_mtime
        self.st_ctime = stats.st_ctime
        self.st_atime_ns = stats.st_atime_ns
        self.st_mtime_ns = stats.st_mtime_ns
        self.st_ctime_ns = stats.st_ctime_ns

        try:
            self.st_birthtime_ns = stats.st_birthtime
            self.st_birthtime = stats.st_birthtime
        except AttributeError:
            self.st_birthtime_ns = None
            self.st_birthtime = None

        # Unix specific attributes
        try:
            self.st_blocks = stats.st_blocks
            self.st_blksize = stats.st_blksize
            self.st_rdev = stats.st_rdev
            self.st_flags = stats.st_flags
            self.st_gen = stats.st_gen
            self.st_fstype = stats.st_fstype
            self.st_rsize = stats.st_rsize
            self.st_creator = stats.st_creator
            self.st_type = stats.st_creator
        except AttributeError:
            self.st_blocks = None
            self.st_blksize = None
            self.st_rdev = None
            self.st_flags = None
            self.st_gen = None
            self.st_fstype = None
            self.st_rsize = None
            self.st_creator = None
            self.st_type = None

        # Windows specific attributes
        try:
            self.st_file_attributes = stats.st_file_attributes
            self.st_reparse_tag = stats.st_reparse_tag
        except AttributeError:
            self.st_file_attributes = None
            self.st_reparse_tag = None


    def getAll(self):
        """
        Returns all class attributes. 
        """
        returnMap = {
            "passed_path": self.passed_path,
            "real_path": self.real_path,
            "is_dir": self.is_dir,
            "st_mode": self.st_mode,
            "st_ino": self.st_ino,
            "st_dev": self.st_dev,
            "st_gid": self.st_gid,
            "st_size": self.st_size,
            "st_nlink": self.st_nlink,
            "st_atime": self.st_atime,
            "st_mtime": self.st_mtime,
            "st_ctime": self.st_ctime,
            "st_atime_ns": self.st_atime_ns,
            "st_mtime_ns": self.st_mtime_ns,
            "st_birthtime_ns": self.st_birthtime,
            "st_birthtime": self.st_birthtime,
            "st_blocks": self.st_blocks,
            "st_blksize": self.st_blksize,
            "st_rdev": self.st_rdev,
            "st_flags": self.st_flags,
            "st_gen": self.st_gen,
            "st_fstype": self.st_fstype,
            "st_rsize": self.st_rsize,
            "st_creator": self.st_creator,
            "st_type": self.st_creator,
            "st_file_attributes": self.st_file_attributes,
            "st_reparse_tag": self.st_reparse_tag,
        }

        return returnMap

    def setStoredPath(self, originalPath, backupPath):
        """
        Determines the stored path for a File object and sets the instance's variable.
        @param originalPath - The path leading to the original file location.
        @param backupPath - The path leading to the root where the backup files are stored. 
        @return string - Returns the self.store_path of the instance after setting it.
        """
        tail = os.path.relpath(self.real_path,originalPath)
        finalBackupPath = os.path.join(backupPath,tail)
        self.stored_path = os.path.realpath(finalBackupPath)

        return self.stored_path

    def getIndexPrint(self):
        """
        Return string containing all necessary data for writing to the index file.
        Format is: "{st_ino}[index-sep]{st_mtime_ns}[index-sep]{real_path}[index-sep]{store_path}"
        """
        returnStr = f"{self.st_ino}[index-sep]{self.st_mtime_ns}[index-sep]{self.real_path}[index-sep]{self.stored_path}"

        return returnStr

    def newStoredPath(self, originalPath, backupPath, indexPath):
        """
        Returns true if the current file has been moved/renamed and the change needs to 
        be reflected in the backup.
        @param originalPath - The path leading to the original file location.
        @param backupPath - The path leading to the root where the backup files are stored.
        @param indexPath - The full stored path, read from the index.
        @return boolean
        """
        commonPath = os.path.relpath(self.real_path,originalPath)
        indexCommonPath = os.path.relpath(indexPath,backupPath)
        if (commonPath != indexCommonPath):
            return True
        return False