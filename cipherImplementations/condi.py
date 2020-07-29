from cipherImplementations.cipher import Cipher
import random
import numpy as np


class Condi(Cipher):
    """Adapted implementation from https://github.com/tigertv/secretpy"""
    def __init__(self, alphabet, unknown_symbol, unknown_symbol_number):
        self.alphabet = alphabet
        self.unknown_symbol = unknown_symbol
        self.unknown_symbol_number = unknown_symbol_number

    def generate_random_key(self, length=None):
        alphabet2 = b'' + self.alphabet
        key = b''
        for _ in range(len(self.alphabet)):
            position = int(random.randrange(0, len(alphabet2)))
            char = bytes([alphabet2[position]])
            key = key + char
            alphabet2 = alphabet2.replace(char, b'')
        return [key, random.randint(0, len(self.alphabet)-1)]

    def encrypt(self, plaintext, key):
        ciphertext = []
        alphabet = key[0]
        offset = key[1]
        for c in plaintext:
            offset = (np.where(alphabet == c)[0][0] + offset) % len(alphabet)
            ciphertext.append(alphabet[offset])
            offset = np.where(alphabet == c)[0][0] + 1
        return np.array(ciphertext)

    def decrypt(self, ciphertext, key):
        plaintext = []
        ciphertext = list(ciphertext)
        alphabet = list(key[0])
        offset = key[1]
        for i in range(0, len(ciphertext), 1):
            plaintext.append(alphabet[(alphabet.index(ciphertext[i]) - offset) % len(alphabet)])
            offset = (alphabet.index(ciphertext[i]) - offset + 1) % len(alphabet)
        return np.array(plaintext)