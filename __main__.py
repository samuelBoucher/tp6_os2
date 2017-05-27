import socket

from client_tp6 import Client
from file_system import FileSystem
from protocole_xml import ProtocoleXml

if __name__ == '__main__':

    s = socket.socket()
    host = ''
    port = 50002
    server_root = 'dropbox/'
    s.bind((host, port))
    s.listen(5)

    nb_clients = 0

    while True:
        print("Attente d'un autre client...")
        connect, addr = s.accept()
        print('Connexion venant de ', addr)
        file_system = FileSystem(server_root)
        protocole = ProtocoleXml(file_system)
        cli = Client("Client " + str(nb_clients), connect, protocole)
        cli.start()
        nb_clients += 1
