#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock

from protocole_xml import ProtocoleXml

from client_tp6 import Client


class XmlTest(unittest.TestCase):

    XML_PREFIX = '<?xml version="1.0" ?>'

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

    def testClientRequestsFileList_ShouldReturnFileList(self):
        expected_answer = self.XML_PREFIX + \
                          '<listeFichiers>' \
                          '<fichier>d1/f1</fichier>' \
                          '<fichier>d1/d2/f2</fichier>' \
                          '</listeFichiers>'
        get_file_list_request = b'<questionListeFichiers>d1</questionListeFichiers>'
        quit_request = b'<quitter/>'
        self.mock_connexion.recv.side_effect = [get_file_list_request, quit_request]
        self.mock_file_system.folder_exists.return_value = True
        self.mock_file_system.get_file_list.return_value = ['d1/f1', 'd1/d2/f2']

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

    def testClientRequestsFileList_FolderDoesntExist_ShouldReturnError(self):
        expected_answer = self.XML_PREFIX + \
                          '<erreurDossierInexistant/>'

        get_file_list_request = b'<questionListeFichiers>d1</questionListeFichiers>'
        quit_request = b'<quitter/>'
        self.mock_connexion.recv.side_effect = [get_file_list_request, quit_request]
        self.mock_file_system.folder_exists.return_value = False

        self.client.run()

        self.mock_connexion.send.assert_any_call(bytes(expected_answer, 'UTF-8'))

if __name__ == '__main__':
    unittest.main()
