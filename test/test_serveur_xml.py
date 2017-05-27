#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock

from protocole_xml import ProtocoleXml

from client_tp6 import Client


class XmlTest(unittest.TestCase):

    XML_PREFIX = '<?xml version="1.0" ?>'
    QUIT_REQUEST = b'<quitter/>'

    mock_connexion = Mock
    mock_file_system = Mock
    protocol = ProtocoleXml
    client = Client
    thread_name = 'client_name'
    server_root = 'server_root'

    def setUp(self):
        self.mock_connexion = Mock()
        self.mock_file_system = Mock()
        self.protocol = ProtocoleXml(self.mock_file_system)
        self.client = Client(self.thread_name, self.mock_connexion, self.protocol)

    def testClientRequestsToQuit_ShouldSendByeToClient(self):
        expected_answer = self.XML_PREFIX + '<bye/>'
        self.mock_connexion.recv.return_value = b'<quitter/>'

        self.client.run()

        self.mock_connexion.send.assert_called_with(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsToQuit_ShouldCloseConnection(self):
        self.mock_connexion.recv.return_value = b'<quitter/>'

        self.client.run()

        self.mock_connexion.close.assert_called_once()

    def testClientRequestsFolderList_ShouldReturnFolderList(self):
        expected_answer = self.XML_PREFIX + \
                          '<listeDossiers>' \
                          '<dossier>d1/d2</dossier>' \
                          '<dossier>d1/d2/d3</dossier>' \
                          '</listeDossiers>'
        get_folder_list_request = b'<questionListeDossiers>d1</questionListeDossiers>'
        self.mock_connexion.recv.side_effect = [get_folder_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_folder_list.return_value = ['d1/d2', 'd1/d2/d3']

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFolderList_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierInexistant/>'

        get_folder_list_request = b'<questionListeDossiers>d1</questionListeDossiers>'
        quit_request = b'<quitter/>'
        self.mock_connexion.recv.side_effect = [get_folder_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsCreateFolder_ShouldCreateFolder(self):
        expected_folder_name = 'd1/'
        create_folder_list_request = b'<creerDossier>d1</creerDossier>'
        self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.side_effect = [True, False]  # Le dossier parent existe,
        #  mais le dossier à créer n'existe pas
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_file_system.create_folder.assert_called_once_with(expected_folder_name)

    def testClientRequestsCreateFolder_ShouldReturnOk(self):
        expected_answer = self.XML_PREFIX + '<ok/>'
        create_folder_list_request = b'<creerDossier>d1</creerDossier>'
        self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.side_effect = [True, False]  # Le dossier parent existe,
        #  mais le dossier à créer n'existe pas
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsCreateFolder_FolderAlreadyExists_ShouldReturnFolderExists(self):
        expected_answer = self.XML_PREFIX + '<erreurDossierExiste/>'
        create_folder_list_request = b'<creerDossier>d1</creerDossier>'
        self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.side_effect = [True, True]  # Le dossier parent existe,
        #  mais le dossier à créer existe aussi
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsCreateFolder_ParentFolderDoesntExist_ShouldReturnFolderDoesntExist(self):
        expected_answer = self.XML_PREFIX + '<erreurDossierInexistant/>'
        create_folder_list_request = b'<creerDossier>d1</creerDossier>'
        self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFileList_ShouldReturnFileList(self):
        expected_answer = self.XML_PREFIX + \
                          '<listeFichiers>' \
                          '<fichier>d1/f1</fichier>' \
                          '<fichier>d1/d2/f2</fichier>' \
                          '</listeFichiers>'
        get_file_list_request = b'<questionListeFichiers>d1</questionListeFichiers>'
        self.mock_connexion.recv.side_effect = [get_file_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_file_list.return_value = ['d1/f1', 'd1/d2/f2']

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFileList_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierInexistant/>'

        get_file_list_request = b'<questionListeFichiers>d1</questionListeFichiers>'
        self.mock_connexion.recv.side_effect = [get_file_list_request, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientAsksIfFileMoreRecent_FileMoreRecent_ShouldReturnYes(self):
        expected_answer = self.XML_PREFIX + '<oui/>'
        request = b'<questionFichierRecent>' \
                    b'<nom>f1</nom>' \
                    b'<dossier>d1</dossier>' \
                    b'<date>2222.2222</date>' \
                    b'</questionFichierRecent>'
        self.mock_connexion.recv.side_effect = [request, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_file_modification_date.return_value = '1111.1111'
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientAsksIfFileMoreRecent_FileNotMoreRecent_ShouldReturnNo(self):
        expected_answer = self.XML_PREFIX + '<non/>'
        request = b'<questionFichierRecent>' \
                    b'<nom>f1</nom>' \
                    b'<dossier>d1</dossier>' \
                    b'<date>1111.1111</date>' \
                    b'</questionFichierRecent>'
        self.mock_connexion.recv.side_effect = [request, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_file_modification_date.return_value = '2222.2222'
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientAsksIfFileMoreRecent_FileDoesNotExist_ShouldReturnFileDoesNotExist(self):
        expected_answer = self.XML_PREFIX + '<erreurFichierInexistant/>'
        request = b'<questionFichierRecent>' \
                    b'<nom>f1</nom>' \
                    b'<dossier>d1</dossier>' \
                    b'<date>1111.1111</date>' \
                    b'</questionFichierRecent>'
        self.mock_connexion.recv.side_effect = [request, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = False
        self.mock_file_system.root = 'root'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))


if __name__ == '__main__':
    unittest.main()
