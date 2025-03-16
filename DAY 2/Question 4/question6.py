import os
from datetime import datetime,date

class File:
    def __init__(self, directory):
        self.directory = directory

    def getMaxSizeFile(self, count=1):

        files = [(f, os.path.getsize(os.path.join(self.directory, f))) 
                 for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
        
        sorted_files = sorted(files, key=lambda x: x[1], reverse=True)
        
        return sorted_files[:count]
    def getLatestFiles(self,target_date):
        result_files = []
        for file in os.listdir(self.directory):
            file_path=os.path.join(self.directory,file)
            if os.path.isfile(file_path):
                creation_date=datetime.fromtimestamp(os.path.getctime(file_path))
                if creation_date.date() > target_date:
                    result_files.append(file)
        return result_files



fs = File(".")
largest_files = fs.getMaxSizeFile(2)
print("Largest files:", largest_files)
target_date = date(2025,3, 10)
files = fs.getLatestFiles(target_date)
print(f"Files created after {date}:", files)
