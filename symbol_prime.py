""" Module containing functions which are used as a part of the solution.
Contains the mapping between symbols and prime numbers and other relevant
functions.
"""

PRIME_MAPPING = {' ': 1,  # Anagram contains whitespace - multiplying by 1
                 'a': 2,
                 'b': 3,
                 'c': 5,
                 'd': 7,
                 'e': 11,
                 'f': 13,
                 'g': 17,
                 'h': 19,
                 'i': 23,
                 'j': 29,
                 'k': 31,
                 'l': 37,
                 'm': 41,
                 'n': 43,
                 'o': 47,
                 'p': 53,
                 'q': 59,
                 'r': 61,
                 's': 67,
                 't': 71,
                 'u': 73,
                 'v': 79,
                 'w': 83,
                 'x': 89,
                 'y': 97,
                 'z': 101}


def word_prime_product(word):
    val = 1
    for char in word:
        prime = PRIME_MAPPING[char]
        val *= prime

    return val
