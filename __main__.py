import socket

from protocole import Protocole
from protocole_xml import ProtocoleXml
from client_tp6 import Client

if __name__ == '__main__':

    s = socket.socket()
    host = ''
    port = 50001
    server_root = 'dropbox/'
    s.bind((host, port))
    s.listen(5)

    nb_clients = 0

    while True:
        print("Attente d'un autre client...")
        connect, addr = s.accept()
        print('Connexion venant de ', addr)
        protocole = ProtocoleXml(server_root)
        cli = Client("Client " + str(nb_clients), connect, protocole)
        cli.start()
        nb_clients += 1
