from file import File

class IndexFile(File):
    def __init__(self,indexData):
        # call in class method to handle index data string
        formattedMap = self.handleDataString(indexData)
        # set instance variables with the returned data
        self.passed_path = formattedMap.get('passed_path')
        self.real_path = formattedMap.get('real_path')
        self.is_dir = formattedMap.get('is_dir')
        self.st_mode = formattedMap.get('st_mode')
        self.st_ino = formattedMap.get('st_ino')
        self.st_dev = formattedMap.get('st_dev')
        self.st_gid = formattedMap.get('st_gid')
        self.st_size = formattedMap.get('st_size')
        self.st_nlink = formattedMap.get('st_nlink')
        self.st_atime = formattedMap.get('st_atime')
        self.st_mtime = formattedMap.get('st_mtime')
        self.st_ctime = formattedMap.get('st_ctime')
        self.st_atime_ns = formattedMap.get('st_atime_ns')
        self.st_mtime_ns = formattedMap.get('st_mtime_ns')
        self.st_birthtime_ns = formattedMap.get('st_birthtime')
        self.st_birthtime = formattedMap.get('st_birthtime')
        self.st_blocks = formattedMap.get('st_blocks')
        self.st_blksize = formattedMap.get('st_blksize')
        self.st_rdev = formattedMap.get('st_rdev')
        self.st_flags = formattedMap.get('st_flags')
        self.st_gen = formattedMap.get('st_gen')
        self.st_fstype = formattedMap.get('st_fstype')
        self.st_rsize = formattedMap.get('st_rsize')
        self.st_creator = formattedMap.get('st_creator')
        self.st_type = formattedMap.get('st_creator')
        self.st_file_attributes = formattedMap.get('st_file_attributes')
        self.st_reparse_tag = formattedMap.get('st_reparse_tag')


    def handleDataString(indexData):
        return None
