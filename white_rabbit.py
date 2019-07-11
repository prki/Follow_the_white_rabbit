""" Main script used for solving the Follow the white rabbit code challenge.

Contains functions pre-filtering the input wordlist before calling the
puzzle solver.
"""
from itertools import combinations
import puzzle_solver
import sys
import symbol_prime


def sort_on_word_probability(words, anagram):
    """ Sorts the words in a non-increasing sequence based on two factors:
        * The amount of total symbols in the word
        * The weight of these symbols (weight is based on occurence frequency
          in the anagram).

    This is done in order to first traverse words which are more likely to
    be the solution - as the words which contain many rare symbols are
    likelier to be a part of the solution than others - as well as words
    which are longer, rather than the ones which are short.
    """
    symbols_weights = {'p': 200,
                       'o': 125,
                       'u': 125,
                       'l': 200,
                       't': 50,
                       'r': 200,
                       'y': 200,
                       'w': 200,
                       'i': 200,
                       's': 125,
                       'a': 200,
                       'n': 200}
    lst = []
    for word in words:
        symbols_in_word = set(word)
        word_weight = 0
        for symbol in symbols_in_word:
            cnt = word.count(symbol)
            word_weight += symbols_weights[symbol] * cnt
        lst.append((word, word_weight))

    lst.sort(key=lambda x: x[1], reverse=True)

    ret = []
    for word in lst:
        ret.append(word[0])

    return ret


def list_product(lst):
    ret = 1
    for num in lst:
        ret *= num

    return ret


def read_dictionary(filepath):
    """ Reads the word list provided in the challenge and returns it in the
    form of a list of words.
    """
    with open(filepath, 'r') as fil:
        words = fil.read().splitlines()

    return words


def filter_characters(words, anagram):
    """ Filters out all the words from the wordlist which have symbols not
    appearing in the anagram.
    """
    ret = []
    append_flag = True
    for word in words:
        chars = set(word)
        for char in chars:
            if char not in anagram:
                append_flag = False
                break
        if append_flag:
            ret.append(word)
        append_flag = True

    return ret


def filter_more_characters(words, anagram):
    """ Filters the words which contain a symbol more times than it is present
    in the anagram.
    """
    ret = []
    append_flag = True
    for word in words:
        word_chars = list(word)
        anagram_chars = list(anagram)
        word_chars_set = set(word)
        for char in word_chars_set:
            if word_chars.count(char) > anagram_chars.count(char):
                append_flag = False
                break
        if append_flag:
            ret.append(word)
        append_flag = True

    return ret


def filter_words(words, anagram):
    words_filtered = filter_characters(words, anagram)
    words_filtered = filter_more_characters(words_filtered, anagram)

    return words_filtered


def main():
    if len(sys.argv) < 3:
        print('Usage: python filter.py wordlist num_of_combinations')
        raise SystemExit(1)
    anagram = 'poultry outwits ants'
    words = read_dictionary(sys.argv[1])
    words = set(words)

    words_filtered = filter_words(words, anagram)
    words_filtered = sort_on_word_probability(words_filtered, anagram)

    #puzzle_solver.find_anagram_triples(words_filtered, anagram)
    #puzzle_solver.solve_puzzle(words_filtered, anagram, 4)
    #puzzle_solver.solve_puzzle_bb(words_filtered, anagram, depth=4)
    #puzzle_solver.solve_puzzle_cut(words_filtered, anagram, 4)
    puzzle_solver.solve_puzzle_rec(words_filtered, anagram, int(sys.argv[2]))
    #puzzle_solver.solve_puzzle_numpy(words_filtered, anagram, 3)


if __name__ == '__main__':
    main()
