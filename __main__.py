import socket
import sys

from ascii_encoder import AsciiEncoder
from client_tp6 import Client
from file_system import FileSystem
from protocole_xml import ProtocoleXml
from protocole_json import ProtocoleJson

if __name__ == '__main__':

    args = sys.argv
    s = socket.socket()
    host = ''
    port = int(args[1])
    server_root = 'dropbox/'
    s.bind((host, port))
    s.listen(5)

    nb_clients = 0

    while True:
        print("Attente d'un autre client...")
        connect, addr = s.accept()
        print('Connexion venant de ', addr)
        file_system = FileSystem(server_root)
        ascii_encoder = AsciiEncoder()
        if args[2] == 'xml':
            protocole = ProtocoleXml(file_system, ascii_encoder)
        else:
            protocole = ProtocoleJson(file_system, ascii_encoder)
        cli = Client("Client " + str(nb_clients), connect, protocole)
        cli.start()
        nb_clients += 1
