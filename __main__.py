import socket

from serveur import Client

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
