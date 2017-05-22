from xml.dom.minidom import Document

from protocole import Protocole


class ProtocoleXml(Protocole):
    """Interface du langage de communication XML"""

    def __init__(self, server_root):
        super(Protocole, self).__init__()
        self.server_root = server_root

    def respond(self, request):
        if '<quitter/>' in request:
            document = self.quit()
        else:
            document = self.invalid()

        return document.toxml()

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