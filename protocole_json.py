import os
import json

from protocole import Protocole
from pathlib import PurePath


class ProtocoleJson(Protocole):
    """Interface du langage de communication XML"""

    def __init__(self, file_system):
        super(Protocole, self).__init__()
        self.file_system = file_system

    def respond(self, request):
        if '<questionListeDossiers>' in request:
            document = self.get_folder_list(request)
        elif '<creerDossier>' in request:
            document = self.create_folder(request)
        elif '<questionListeFichiers>' in request:
            document = self.get_file_list(request)
        elif '<questionFichierRecent>' in request:
            document = self.verify_file_more_recent(request)
        elif 'supprimerFichier' in request:
            document = self.delete_file(request)
        elif '<quitter/>' in request:
            document = self.quit()
        else:
            document = self.invalid()

        return document

    def get_folder_list(self, request):
        request_tag_name = 'questionListeDossiers'
        folder = self.get_request_content(request, request_tag_name)

        if self.file_system.folder_exists(folder):
            folder_list = self.file_system.get_folder_list(folder)
            response_parent_tag_name = 'listeDossiers'
            response_child_tag_name = 'dossier'
            document = self.element_to_xml(response_parent_tag_name)
            for folder in folder_list:
                xml_file_name = self.element_to_xml(response_child_tag_name, folder)
                document.childNodes[0].appendChild(xml_file_name.childNodes[0])
        else:
            response_tag_name = "erreurDossierInexistant"
            document = self.element_to_xml(response_tag_name)

        return document

    def create_folder(self, request):
        request_tag_name = 'creerDossier'
        request_content = self.get_request_content(request, request_tag_name)
        folder_to_create = self.get_folder_name(request_content)
        folder_path = self.get_parent_folder_name(folder_to_create)

        if self.file_system.folder_exists(folder_path):
            if self.file_system.folder_exists(folder_to_create):
                response_tag = 'erreurDossierExiste'
            else:
                self.file_system.create_folder(folder_to_create)
                response_tag = 'ok'
        else:
            response_tag = 'erreurDossierInexistant'

        return self.element_to_xml(response_tag)

    def delete_file(self, request):
        request_tag_name = "supprimerFichier"
        request_content = self.interpret(request, request_tag_name)
        file_to_delete = request_content['dossier'] + '/' + request_content['nom']

        if self.file_system.folder_exists(request_content['dossier']):
            if self.file_system.file_exists(file_to_delete):
                self.file_system.delete_file(file_to_delete)
                response = "ok"
            else:
                response = "erreurFichierLecture"
        else:
            response = "erreurDossierInexistant"

        data = {}

        self.add_row_to_json_table('reponse', response, data)

        return self.json_table_to_json_text(data)

    def get_file_list(self, request):
        request_tag_name = 'questionListeFichiers'
        folder = self.get_request_content(request, request_tag_name)

        if self.file_system.folder_exists(folder):
            file_list = self.file_system.get_file_list(folder)
            response_parent_tag_name = 'listeFichiers'
            response_child_tag_name = 'fichier'
            document = self.element_to_xml(response_parent_tag_name)
            for file in file_list:
                xml_file_name = self.element_to_xml(response_child_tag_name, file)
                document.childNodes[0].appendChild(xml_file_name.childNodes[0])
        else:
            response_tag_name = 'erreurDossierInexistant'
            document = self.element_to_xml(response_tag_name)

        return document

    def verify_file_more_recent(self, request):
        request_tag_name = 'questionFichierRecent'
        folder_tag_name = 'dossier'
        file_tag_name = 'nom'
        date_tag_name = 'date'
        folder_path = self.get_request_content(request, request_tag_name, folder_tag_name)
        folder_name = self.get_folder_name(folder_path)
        file_name = self.get_request_content(request, request_tag_name, file_tag_name)
        file_path = folder_name + file_name

        if self.file_system.file_exists(file_path):
            client_file_date = self.get_request_content(request, request_tag_name, date_tag_name)
            server_file_date = self.file_system.get_file_modification_date(file_path)

            if client_file_date > server_file_date:
                response_tag = 'oui'
            else:  # On considère que c'est impossible que les deux dates soient égales.
                response_tag = 'non'
        else:
            response_tag = 'erreurFichierInexistant'

        return self.element_to_xml(response_tag)

    def quit(self):
        tag = 'bye'
        document = self.element_to_xml(tag)

        return document

    def invalid(self):
        tag = 'invalid'
        document = self.element_to_xml(tag)

        return document

    def interpret(self, json_data, parent_tag, child_tag=''):
        data = json.loads(json_data)

        if child_tag:
            return self.interpret_complex_json(data, parent_tag, child_tag)
        else:
            return self.interpret_simple_json(data, parent_tag)

    def interpret_simple_json(self, data, tag_name):
        return data[tag_name]

    def interpret_complex_json(self, data, parent_tag, child_tag):
        returned_data = []

        if 'contenu' not in data:
            returned_data.append(data[parent_tag][child_tag])
        else:
            for node in data[parent_tag][child_tag]:
                returned_data.append(node)

    def json_table_to_json_text(self, data):
        json_data = json.dumps(data)
        return json_data

    def add_row_to_json_table(self, key, value, data):
        data[key] = value

    def get_folder_name(self, path):
        return path.replace(self.file_system.root, '') + '/'

    def get_parent_folder_name(self, path):
        path = path[:-1]  # On enlève le dernier slash
        return os.path.dirname(path)

