#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
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

if __name__ == '__main__':

    s = socket.socket()
    host = ''
    port = 50001
    s.bind((host, port))
    s.listen(5)

    nb_clients = 0

    while True:
        print("Attente d'un autre client...")
        connect, addr = s.accept()
        print('Connexion venant de ', addr)
        cli = Client("Client " + str(nb_clients), connect)
        cli.start()
        nb_clients += 1
        print("Il y a en ce moment " + str(nb_clients) + " clients")

