#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
from xml.dom.minidom import parseString


class Client(threading.Thread):
    def __init__(self, threadName, connection):
        threading.Thread.__init__(self, name=threadName)
        self.connection = connection

    def run(self):
        dom = parseString("<monMessage>Merci de vous connecter</monMessage>")
        self.connection.send(bytes(dom.toxml(), 'UTF-8'))
        self.connection.close()


