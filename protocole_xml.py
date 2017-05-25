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
        elif '<quitter/>' in request:
            document = self.quit()
        else:
            document = self.invalid()

        return document.toxml()

    def get_request_content(self, request, tag_name):
        document = parseString(request)
        return document.getElementsByTagName(tag_name)[0].childNodes[0].data

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
            tag_name = 'erreurDossierInexistant'
            document = self.element_to_xml(tag_name)

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
            tag_name = 'erreurDossierInexistant'
            document = self.element_to_xml(tag_name)

        return document

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
