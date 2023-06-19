class FileReader:
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self._open_file()
        
    def _open_file(self):
        self.file = open(self.log_file, "r")
        
    def read_lines(self):
        return self.file.readlines()
        