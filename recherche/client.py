#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

if __name__ == '__main__':
    s = socket.socket()
    s.connect(('127.0.0.1', 50001))
    message = s.recv(1024 * 1024 * 512).decode('UTF-8')
    print(message)
