import os


class FileSystem:

    def __init__(self, root):
        self.root = root

    def get_file_list(self, folder_name):
        complete_file_name = self.get_complete_path(folder_name)
        file_list = []
        for root, directories, filenames in os.walk(complete_file_name):
            for filename in filenames:
                path = os.path.join(root, filename)
                path = path.replace(self.root, '')  # On enlève la racine commune 'dropbox\'
                file_list.append(path)

        return file_list

    def get_complete_path(self, path):
        return self.root + path + '/'
