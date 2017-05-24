#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock

from client_tp6 import Client
from protocole_xml import ProtocoleXml


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
        self.protocol = ProtocoleXml(self.server_root)
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


if __name__ == '__main__':
    unittest.main()
