from xml.dom.minidom import Document, parseString

from protocole import Protocole


class ProtocoleXml(Protocole):
    """Interface du langage de communication XML"""

    def __init__(self, file_system):
        super(Protocole, self).__init__()
        self.file_system = file_system

    def respond(self, request):
        if '<questionListeDossiers>' in request:
            document = self.get_folder_list(request)
        elif '<questionListeFichiers>' in request:
            document = self.get_file_list(request)
        elif '<questionFichierRecent>' in request:
            document = self.verify_file_more_recent(request)
        elif '<quitter/>' in request:
            document = self.quit()
        else:
            document = self.invalid()

        return document.toxml()

    def get_request_content(self, request, parent_tag_name, child_tag_name=''):
        document = parseString(request)

        if child_tag_name:
            return self.get_complex_request_content(document, parent_tag_name, child_tag_name)
        else:
            return self.get_simple_request_content(document, parent_tag_name)

    def get_simple_request_content(self, document, tag_name):
        return document.getElementsByTagName(tag_name)[0].childNodes[0].data

    def get_complex_request_content(self, document, parent_tag, child_tag):
        node = document.getElementsByTagName(parent_tag)[0]
        child_node = node.getElementsByTagName(child_tag)[0]
        return child_node.firstChild.data
        # for node in document.getElementsByTagName(parent_tag):
        #     if node is not None:
        #         # for child_node in node.getElementsByTagName(child_tag):
        #         #     data.append(child_node.firstChild.data)
        #         data =
        #

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
            response_tag_name = 'erreurDossierInexistant'
            document = self.element_to_xml(response_tag_name)

        return document

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

    def element_to_xml(self, tag, text=''):
        document = Document()

        texte_a_retourner = document.createElement(tag)
        document.appendChild(texte_a_retourner)
        if text:
            texte_xml = document.createTextNode(text)
            texte_a_retourner.appendChild(texte_xml)

        return document


    def get_folder_name(self, path):
        return path.replace(self.file_system.root, '') + '/'
