#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii


# Rapport: Ceci sert à encoder et décoder l'ascii et UTF-8


class AsciiEncoder:
    def encode_in_ascii(self, content):

        utf8_content = content.encode('UTF-8')
        contenu_encode = binascii.b2a_base64(utf8_content)
        ascii_content = contenu_encode.decode()

        return ascii_content

    def decode_ascii(self, content):
        ascii_content = content.encode('ascii')
        contenu_encode = binascii.a2b_base64(ascii_content)
        utf8_content = contenu_encode.decode('UTF-8')

        return utf8_content
