#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import json


class Client(threading.Thread):
    def __init__(self, thread_name, connection, protocole):
        threading.Thread.__init__(self, name=thread_name)
        self.connection = connection
        self.protocole = protocole

    def run(self):
        while True:
            response = self.wait_for_request()
            if type(response) is dict:
                response = json.dumps(response)
            self.connection.send(bytes(response, 'UTF-8'))
            if 'bye' in response:
                break
        self.connection.close()

    def wait_for_request(self):
        print("En attente d'une réponse...")
        request = self.connection.recv(1024)
        if type(request) is bytes:
            request = request.decode('UTF-8')
        print('requete = ' + str(request))
        response = self.protocole.respond(request)
        print('reponse = ' + str(response))

        return response
