import os


class FileSystem:

    def __init__(self, root):
        self.root = root

    def folder_exists(self, directory):
        complete_directory = self.root + directory
        return os.path.exists(complete_directory)

    def get_folder_list(self, folder_name):
        complete_folder_name = self.get_complete_path(folder_name)
        folder_list = []
        for root, directories, filenames in os.walk(complete_folder_name):
            for directory in directories:
                path = os.path.join(root, directory)
                path = path.replace(self.root, '')  # On enlève la racine commune 'dropbox\'
                folder_list.append(path)

        return folder_list

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
