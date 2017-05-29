#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
from unittest.mock import Mock

from protocole_json import ProtocoleJson

from client_tp6 import Client


class JsonTest(unittest.TestCase):

    XML_PREFIX = '<?xml version="1.0" ?>'
    QUIT_REQUEST = b'<quitter/>'

    mock_connexion = Mock
    mock_file_system = Mock
    protocol = ProtocoleJson
    client = Client
    thread_name = 'client_name'
    server_root = 'server_root'

    def setUp(self):
        self.mock_connexion = Mock()
        self.mock_file_system = Mock()
        self.mock_ascii_encoder = Mock()
        self.protocol = ProtocoleJson(self.mock_file_system, self.mock_ascii_encoder)
        self.client = Client(self.thread_name, self.mock_connexion, self.protocol)

    def testClientRequestsToQuit_ShouldSendByeToClient(self):
        expected_answer = '{"response": "bye"}'
        self.mock_connexion.recv.return_value = '{"action": "quitter"}'

        self.client.run()

        self.mock_connexion.send.assert_called_with(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsToQuit_ShouldCloseConnection(self):
        self.mock_connexion.recv.return_value = '{"action": "quitter"}'

        self.client.run()

        self.mock_connexion.close.assert_called_once()

    def testClientRequestsDeleteFile_ShouldReturnResponseOk(self):
        expected_answer = '{"reponse": "ok"}'
        delete_file_request = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        delete_file_request['supprimerFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(delete_file_request), quit_request]
        self.mock_file_system.folder_exists.return_value = True

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsDeleteFile_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = '{"reponse": "erreurDossierInexistant"}'
        delete_file_request = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        delete_file_request['supprimerFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(delete_file_request), quit_request]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsDeleteFile_FileDoesntExist_ShouldReturnError(self):
        expected_answer = '{"reponse": "erreurFichierInexistant"}'
        delete_file_request = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        delete_file_request['supprimerFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(delete_file_request), quit_request]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.file_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsDownloadFile_ShouldReturnFile(self):
        expected_answer = '{"fichier": {' \
                          '"signature": "12341234", ' \
                          '"contenu": "ok", ' \
                          '"date": "12.234234"}}'
        download_file_request = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        download_file_request['telechargerFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(download_file_request), quit_request]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_md5_signature.return_value = "12341234"
        self.mock_file_system.get_file_content.return_value = "ok"
        self.mock_file_system.get_file_modification_date.return_value = "12.234234"

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsDownloadFile_FileDoesntExist_ShouldReturnError(self):
        expected_answer = '{"reponse": "erreurFichierInexistant"}'
        download_file_request = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        download_file_request['telechargerFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(download_file_request), quit_request]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.file_exists.return_value = False
        self.mock_file_system.get_md5_signature.return_value = "12341234"
        self.mock_file_system.get_file_content.return_value = "ok"
        self.mock_file_system.get_file_modification_date.return_value = "12.234234"

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsDownloadFile_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = '{"reponse": "erreurDossierInexistant"}'
        download_file_request = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        download_file_request['telechargerFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(download_file_request), quit_request]
        self.mock_file_system.folder_exists.return_value = False
        self.mock_file_system.file_exists.return_value = True
        self.mock_file_system.get_md5_signature.return_value = "12341234"
        self.mock_file_system.get_file_content.return_value = "ok"
        self.mock_file_system.get_file_modification_date.return_value = "12.234234"

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsUploadFile_ShouldReturnOk(self):
        expected_answer = '{"reponse": "ok"}'
        uploadFileRequest = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        fileData['signature'] = 'wow'
        fileData['contenu'] = 'wow'
        fileData['date'] = 12.41241
        uploadFileRequest['televerserFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(uploadFileRequest), quit_request]
        self.mock_file_system.file_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsUploadFile_ShouldCallCreateFile(self):
        uploadFileRequest = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        fileData['signature'] = 'wow'
        fileData['contenu'] = 'wow'
        fileData['date'] = 12.41241
        uploadFileRequest['televerserFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(uploadFileRequest), quit_request]
        self.mock_file_system.file_exists.return_value = False

        self.client.run()

        self.mock_file_system.create_file.assert_any_call(fileData['dossier'], fileData['nom'])

    def testClientRequestsUploadFile_FileAlreadyExists_ShouldReturnError(self):
        expected_answer = '{"reponse": "erreurFichierExiste"}'
        uploadFileRequest = {}
        fileData = {}
        fileData['nom'] = 'f1'
        fileData['dossier'] = 'd1'
        fileData['signature'] = 'wow'
        fileData['contenu'] = 'wow'
        fileData['date'] = 12.41241
        uploadFileRequest['televerserFichier'] = fileData
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [json.dumps(uploadFileRequest), quit_request]
        self.mock_file_system.file_exists.return_value = True

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFolderList_ShouldReturnFolderList(self):
        expected_answer = '{"listeDossiers": {"dossier": ["d1/d2", "d1/d2/d3"]}}'
        get_folder_list_request = '{"questionListeDossiers": "d1"}'
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [get_folder_list_request, quit_request]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_folder_list.return_value = ['d1/d2', 'd1/d2/d3']

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFolderList_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = '{"reponse": "erreurDossierInexistant"}'

        get_folder_list_request = '{"questionListeDossiers": "d1"}'
        quit_request = '{"action": "quitter"}'
        self.mock_connexion.recv.side_effect = [get_folder_list_request, quit_request]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientRequestsCreateFolder_ShouldCreateFolder(self):
    #     expected_folder_name = 'd1/'
    #     create_folder_list_request = b'<creerDossier>d1</creerDossier>'
    #     self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
    #     self.mock_file_system.folder_exists.side_effect = [True, False]  # Le dossier parent existe,
    #     #  mais le dossier à créer n'existe pas
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_file_system.create_folder.assert_called_once_with(expected_folder_name)
    #
    # def testClientRequestsCreateFolder_ShouldReturnOk(self):
    #     expected_answer = self.XML_PREFIX + '<ok/>'
    #     create_folder_list_request = b'<creerDossier>d1</creerDossier>'
    #     self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
    #     self.mock_file_system.folder_exists.side_effect = [True, False]  # Le dossier parent existe,
    #     #  mais le dossier à créer n'existe pas
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientRequestsCreateFolder_FolderAlreadyExists_ShouldReturnFolderExists(self):
    #     expected_answer = self.XML_PREFIX + '<erreurDossierExiste/>'
    #     create_folder_list_request = b'<creerDossier>d1</creerDossier>'
    #     self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
    #     self.mock_file_system.folder_exists.side_effect = [True, True]  # Le dossier parent existe,
    #     #  mais le dossier à créer existe aussi
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientRequestsCreateFolder_ParentFolderDoesntExist_ShouldReturnFolderDoesntExist(self):
    #     expected_answer = self.XML_PREFIX + '<erreurDossierInexistant/>'
    #     create_folder_list_request = b'<creerDossier>d1</creerDossier>'
    #     self.mock_connexion.recv.side_effect = [create_folder_list_request, self.QUIT_REQUEST]
    #     self.mock_file_system.folder_exists.return_value = False
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientRequestsFileList_ShouldReturnFileList(self):
    #     expected_answer = self.XML_PREFIX + \
    #                       '<listeFichiers>' \
    #                       '<fichier>d1/f1</fichier>' \
    #                       '<fichier>d1/d2/f2</fichier>' \
    #                       '</listeFichiers>'
    #     get_file_list_request = b'<questionListeFichiers>d1</questionListeFichiers>'
    #     quit_request = b'<quitter/>'
    #     self.mock_connexion.recv.side_effect = [get_file_list_request, quit_request]
    #     self.mock_file_system.folder_exists.return_value = True
    #     self.mock_file_system.get_file_list.return_value = ['d1/f1', 'd1/d2/f2']
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientRequestsFileList_FolderDoesntExist_ShouldReturnError(self):
    #     expected_answer = self.XML_PREFIX + \
    #                       '<erreurDossierInexistant/>'
    #
    #     get_file_list_request = b'<questionListeFichiers>d1</questionListeFichiers>'
    #     quit_request = b'<quitter/>'
    #     self.mock_connexion.recv.side_effect = [get_file_list_request, quit_request]
    #     self.mock_file_system.folder_exists.return_value = False
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientAsksIfFileMoreRecent_FileMoreRecent_ShouldReturnYes(self):
    #     expected_answer = self.XML_PREFIX + '<oui/>'
    #     request = b'<questionFichierRecent>' \
    #                 b'<nom>f1</nom>' \
    #                 b'<dossier>d1</dossier>' \
    #                 b'<date>2222.2222</date>' \
    #                 b'</questionFichierRecent>'
    #     self.mock_connexion.recv.side_effect = [request, self.QUIT_REQUEST]
    #     self.mock_file_system.file_exists.return_value = True
    #     self.mock_file_system.get_file_modification_date.return_value = '1111.1111'
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientAsksIfFileMoreRecent_FileNotMoreRecent_ShouldReturnNo(self):
    #     expected_answer = self.XML_PREFIX + '<non/>'
    #     request = b'<questionFichierRecent>' \
    #                 b'<nom>f1</nom>' \
    #                 b'<dossier>d1</dossier>' \
    #                 b'<date>1111.1111</date>' \
    #                 b'</questionFichierRecent>'
    #     self.mock_connexion.recv.side_effect = [request, self.QUIT_REQUEST]
    #     self.mock_file_system.file_exists.return_value = True
    #     self.mock_file_system.get_file_modification_date.return_value = '2222.2222'
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))
    #
    # def testClientAsksIfFileMoreRecent_FileDoesNotExist_ShouldReturnFileDoesNotExist(self):
    #     expected_answer = self.XML_PREFIX + '<erreurFichierInexistant/>'
    #     request = b'<questionFichierRecent>' \
    #                 b'<nom>f1</nom>' \
    #                 b'<dossier>d1</dossier>' \
    #                 b'<date>1111.1111</date>' \
    #                 b'</questionFichierRecent>'
    #     self.mock_connexion.recv.side_effect = [request, self.QUIT_REQUEST]
    #     self.mock_file_system.file_exists.return_value = False
    #     self.mock_file_system.root = 'root'
    #
    #     self.client.run()
    #
    #     self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))


if __name__ == '__main__':
    unittest.main()
