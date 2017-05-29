import os
import json

from protocole import Protocole


class ProtocoleJson(Protocole):

    def __init__(self, file_system, ascii_encoder):
        super(Protocole, self).__init__()
        self.file_system = file_system
        self.ascii_encoder = ascii_encoder

    def respond(self, request):
        if 'questionListeDossiers' in request:
            document = self.get_folder_list(request)
        elif 'creerDossier' in request:
            document = self.create_folder(request)
        elif 'questionListeFichiers' in request:
            document = self.get_file_list(request)
        elif '<questionFichierRecent>' in request:
            document = self.verify_file_more_recent(request)
        elif 'supprimerFichier' in request:
            document = self.delete_file(request)
        elif 'telechargerFichier' in request:
            document = self.download_file(request)
        elif 'televerserFichier' in request:
            document = self.upload_file(request)
        elif 'quitter' in request:
            document = self.quit()
        else:
            document = self.invalid()

        return document

    def get_folder_list(self, request):
        request_tag_name = 'questionListeDossiers'
        request_content = self.interpret(request, request_tag_name)

        data = {}

        if self.file_system.folder_exists(request_content):
            folder_list = self.file_system.get_folder_list(request_content)
            listeDossier = {}
            self.add_row_to_json_table('dossier', folder_list, listeDossier)
            self.add_row_to_json_table('listeDossiers', listeDossier, data)
        else:
            self.add_row_to_json_table('reponse', 'erreurDossierInexistant', data)

        return data

    def create_folder(self, request):
        request_tag_name = 'creerDossier'
        request_content = self.interpret(request, request_tag_name)
        folder_to_create = self.get_folder_name(request_content)
        folder_path = self.get_parent_folder_name(folder_to_create)

        data = {}

        if self.file_system.folder_exists(folder_path):
            if self.file_system.folder_exists(folder_to_create):
                response = 'erreurDossierExiste'
            else:
                self.file_system.create_folder(folder_to_create)
                response = 'ok'
        else:
            response = 'erreurDossierInexistant'

        self.add_row_to_json_table('reponse', response, data)
        return data

    def delete_file(self, request):
        request_tag_name = "supprimerFichier"
        request_content = self.interpret(request, request_tag_name)
        file_to_delete = request_content['dossier'] + '/' + request_content['nom']

        if self.file_system.folder_exists(request_content['dossier']):
            if self.file_system.file_exists(file_to_delete):
                self.file_system.delete_file(file_to_delete)
                response = "ok"
            else:
                response = "erreurFichierInexistant"
        else:
            response = "erreurDossierInexistant"

        data = {}

        self.add_row_to_json_table('reponse', response, data)

        return self.json_table_to_json_text(data)

    def download_file(self, request):
        request_tag_name = "telechargerFichier"
        request_content = self.interpret(request, request_tag_name)
        file_to_send = request_content['dossier'] + '/' + request_content['nom']

        data = {}

        if self.file_system.folder_exists(request_content['dossier']):
            if self.file_system.file_exists(file_to_send):
                signature = self.file_system.get_md5_signature(file_to_send)
                content = self.file_system.get_file_content(file_to_send)
                date = self.file_system.get_file_modification_date(file_to_send)

                fichier = {}
                self.add_row_to_json_table('signature', signature, fichier)
                self.add_row_to_json_table('contenu', content, fichier)
                self.add_row_to_json_table('date', date, fichier)

                self.add_row_to_json_table('fichier', fichier, data)
            else:
                response = "erreurFichierInexistant"
                self.add_row_to_json_table('reponse', response, data)
        else:
            response = "erreurDossierInexistant"
            self.add_row_to_json_table('reponse', response, data)

        return self.json_table_to_json_text(data)

    def upload_file(self, request):
        request_tag_name = "televerserFichier"
        request_content = self.interpret(request, request_tag_name)
        file_path = request_content['dossier'] + '/' + request_content['nom']

        data = {}

        if not self.file_system.file_exists(file_path):
            self.file_system.create_file(request_content['dossier'], request_content['nom'])
            response = "ok"
        else:
            response = "erreurFichierExiste"

        self.add_row_to_json_table('reponse', response, data)
        return self.json_table_to_json_text(data)

    def get_file_list(self, request):
        request_tag_name = 'questionListeFichiers'
        request_content = self.interpret(request, request_tag_name)

        data = {}

        if self.file_system.folder_exists(request_content):
            file_list = self.file_system.get_file_list(request_content)
            listeFichiers = {}
            self.add_row_to_json_table('fichier', file_list, listeFichiers)
            self.add_row_to_json_table('listeFichiers', listeFichiers, data)
        else:
            self.add_row_to_json_table('reponse', 'erreurDossierInexistant', data)

        return data

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
        data = {}
        self.add_row_to_json_table('response', 'bye', data)

        return data;

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

