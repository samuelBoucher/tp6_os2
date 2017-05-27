#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock

from protocole_xml import ProtocoleXml

from client_tp6 import Client


class XmlTest(unittest.TestCase):

    XML_PREFIX = '<?xml version="1.0" ?>'
    QUIT_REQUEST = b'<quitter/>'
    GET_FOLDER_LIST_REQUEST = b'<questionListeDossiers>d1</questionListeDossiers>'
    CREATE_FOLDER_REQUEST = b'<creerDossier>d1</creerDossier>'
    GET_FILE_LIST_REQUEST = b'<questionListeFichiers>d1</questionListeFichiers>'
    FILE_MORE_RECENT_REQUEST = \
        b'<questionFichierRecent>' \
        b'<nom>f1</nom>' \
        b'<dossier>d1</dossier>' \
        b'<date>2222.2222</date>' \
        b'</questionFichierRecent>'
    DELETE_FILE_REQUEST = \
        b'<supprimerFichier>' \
        b'<nom>f1</nom>' \
        b'<dossier>d1</dossier>' \
        b'</supprimerFichier>'

    mock_connexion = Mock
    mock_file_system = Mock
    protocol = ProtocoleXml
    client = Client
    thread_name = 'client_name'
    server_root = 'server_root'

    def setUp(self):
        self.mock_connexion = Mock()
        self.mock_file_system = Mock()
        self.mock_file_system.root = 'root'
        self.protocol = ProtocoleXml(self.mock_file_system)
        self.client = Client(self.thread_name, self.mock_connexion, self.protocol)

    def testClientRequestsToQuit_ShouldSendByeToClient(self):
        expected_answer = self.XML_PREFIX + '<bye/>'
        self.mock_connexion.recv.return_value = self.QUIT_REQUEST

        self.client.run()

        self.mock_connexion.send.assert_called_with(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsToQuit_ShouldCloseConnection(self):
        self.mock_connexion.recv.return_value = self.QUIT_REQUEST

        self.client.run()

        self.mock_connexion.close.assert_called_once()

    def testClientRequestsFolderList_ShouldReturnFolderList(self):
        expected_answer = self.XML_PREFIX + \
                          '<listeDossiers>' \
                          '<dossier>d1/d2</dossier>' \
                          '<dossier>d1/d2/d3</dossier>' \
                          '</listeDossiers>'
        self.mock_connexion.recv.side_effect = [self.GET_FOLDER_LIST_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_folder_list.return_value = ['d1/d2', 'd1/d2/d3']

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFolderList_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierInexistant/>'
        self.mock_connexion.recv.side_effect = [self.GET_FOLDER_LIST_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFolderList_CouldNotReadFolder_ShouldReturnCouldNotReadFolder(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierLecture/>'
        self.mock_connexion.recv.side_effect = [self.GET_FOLDER_LIST_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_folder_list.side_effect = IOError()

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsCreateFolder_ShouldCreateFolder(self):
        expected_folder_name = 'd1/'
        self.mock_connexion.recv.side_effect = [self.CREATE_FOLDER_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.side_effect = [True, False]  # Le dossier parent existe,
        #  mais le dossier à créer n'existe pas

        self.client.run()

        self.mock_file_system.create_folder.assert_called_once_with(expected_folder_name)

    def testClientRequestsCreateFolder_ShouldReturnOk(self):
        expected_answer = self.XML_PREFIX + '<ok/>'
        self.mock_connexion.recv.side_effect = [self.CREATE_FOLDER_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.side_effect = [True, False]  # Le dossier parent existe,
        #  mais le dossier à créer n'existe pas

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsCreateFolder_FolderAlreadyExists_ShouldReturnFolderExists(self):
        expected_answer = self.XML_PREFIX + '<erreurDossierExiste/>'
        self.mock_connexion.recv.side_effect = [self.CREATE_FOLDER_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.side_effect = [True, True]  # Le dossier parent existe,
        #  mais le dossier à créer existe aussi

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsCreateFolder_ParentFolderDoesntExist_ShouldReturnFolderDoesntExist(self):
        expected_answer = self.XML_PREFIX + '<erreurDossierInexistant/>'
        self.mock_connexion.recv.side_effect = [self.CREATE_FOLDER_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFileList_ShouldReturnFileList(self):
        expected_answer = self.XML_PREFIX + \
                          '<listeFichiers>' \
                          '<fichier>d1/f1</fichier>' \
                          '<fichier>d1/d2/f2</fichier>' \
                          '</listeFichiers>'
        self.mock_connexion.recv.side_effect = [self.GET_FILE_LIST_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_file_list.return_value = ['d1/f1', 'd1/d2/f2']

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFileList_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierInexistant/>'
        self.mock_connexion.recv.side_effect = [self.GET_FILE_LIST_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testGetFileList_CouldNotReadFolder_ShouldReturnCouldNotReadFolder(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierLecture/>'
        self.mock_connexion.recv.side_effect = [self.GET_FILE_LIST_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_file_list.side_effect = IOError()

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientAsksIfFileMoreRecent_FileMoreRecent_ShouldReturnYes(self):
        expected_answer = self.XML_PREFIX + '<oui/>'
        self.mock_connexion.recv.side_effect = [self.FILE_MORE_RECENT_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_file_modification_date.return_value = '1111.1111'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientAsksIfFileMoreRecent_FileNotMoreRecent_ShouldReturnNo(self):
        expected_answer = self.XML_PREFIX + '<non/>'
        self.mock_connexion.recv.side_effect = [self.FILE_MORE_RECENT_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_file_modification_date.return_value = '2222.2222'

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientAsksIfFileMoreRecent_FileDoesNotExist_ShouldReturnFileDoesNotExist(self):
        expected_answer = self.XML_PREFIX + '<erreurFichierInexistant/>'
        self.mock_connexion.recv.side_effect = [self.FILE_MORE_RECENT_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testVerifyFileMoreRecent_CouldNotReadFile_ShouldReturnCouldNotReadFile(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurFichierLecture/>'
        self.mock_connexion.recv.side_effect = [self.FILE_MORE_RECENT_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_file_modification_date.side_effect = IOError()

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testDeleteFile_ShouldDeleteFile(self):
        expected_file_name = 'd1/f1'
        self.mock_connexion.recv.side_effect = [self.DELETE_FILE_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.file_exists.return_value = True

        self.client.run()

        self.mock_file_system.delete_file.assert_called_once_with(expected_file_name)

    def testDeleteFile_ShouldReturnOk(self):
        expected_answer = self.XML_PREFIX + '<ok/>'
        self.mock_connexion.recv.side_effect = [self.DELETE_FILE_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.file_exists.return_value = True

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testDeleteFile_FolderDoesntExist_ShouldReturnFolderDoesntExist(self):
        expected_answer = self.XML_PREFIX + '<erreurDossierInexistant/>'
        self.mock_connexion.recv.side_effect = [self.DELETE_FILE_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testDeleteFile_FileDoesntExist_ShouldReturnFileDoesntExist(self):
        expected_answer = self.XML_PREFIX + '<erreurFichierInexistant/>'
        self.mock_connexion.recv.side_effect = [self.DELETE_FILE_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.file_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testDeleteFile_CouldNotReadFile_ShouldReturnCouldNotReadFile(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurFichierLecture/>'
        self.mock_connexion.recv.side_effect = [self.DELETE_FILE_REQUEST, self.QUIT_REQUEST]
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.delete_file.side_effect = IOError()

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))


if __name__ == '__main__':
    unittest.main()
