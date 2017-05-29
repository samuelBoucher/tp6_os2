import genericpath
import os
from signature_generator import SignatureGenerator


class FileSystem:

    def __init__(self, root):
        self.root = root

    def folder_exists(self, directory):
        complete_directory = self.root + directory
        return os.path.exists(complete_directory)

    def file_exists(self, file):
        complete_file_path = self.root + file
        fileExists = genericpath.isfile(complete_file_path)
        if fileExists:
            return True
        else:
            return False

    def get_folder_list(self, folder_name):
        complete_folder_name = self.get_complete_folder_path(folder_name)
        folder_list = []
        for root, directories, filenames in os.walk(complete_folder_name):
            for directory in directories:
                path = os.path.join(root, directory)
                path = path.replace(self.root, '')# On enlève la racine commune 'dropbox\'
                path = path.replace('\\', '/')
                folder_list.append(path)

        return folder_list

    def create_folder(self, directory):
        complete_directory = self.get_complete_folder_path(directory)
        os.mkdir(complete_directory)

    def create_file(self, directory, content):
        complete_directory = self.get_complete_folder_path(directory)
        file = open(complete_directory, "w+")
        file.write(content)

    def delete_file(self, directory):
        complete_directory = self.get_complete_folder_path(directory)
        os.remove(complete_directory)

    def get_md5_signature(self, file_name):
        content = self.get_file_content(file_name)
        signature = SignatureGenerator.generate_signature(content)

        return signature

    def get_file_content(self, file_name):
        complete_file_name = self.get_complete_file_path(file_name)
        content = open(complete_file_name).read()

        return content

    def get_file_modification_date(self, file_name):
        complete_file_name = self.get_complete_file_path(file_name)
        file_stat = os.stat(complete_file_name)
        modification_date = str(file_stat.st_mtime)

        return modification_date

    def get_file_list(self, folder_name):
        complete_file_name = self.get_complete_folder_path(folder_name)
        file_list = []
        for root, directories, filenames in os.walk(complete_file_name):
            for filename in filenames:
                path = os.path.join(root, filename)
                path = path.replace(self.root, '')  # On enlève la racine commune 'dropbox\'
                path = path.replace('\\', '/')
                file_list.append(path)

        return file_list

    def get_complete_folder_path(self, folder_name):
        return self.root + folder_name

    def get_complete_file_path(self, file_name):
        return self.root + file_name

