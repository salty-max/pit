class FileSystemException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("FileSystemException: " + self.message)


class GitException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("GitException: " + self.message)
