#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
from xml.dom.minidom import parseString


class Client(threading.Thread):
    def __init__(self, threadName, connection):
        threading.Thread.__init__(self, name=threadName)
        self.connection = connection

    def run(self):
        while True:
            print("En attente d'une réponse...")
            response = self.connection.recv(1024).decode('UTF-8')
            print(response)
            self.connection.send(bytes(response, 'UTF-8'))
            break
        self.connection.close()


