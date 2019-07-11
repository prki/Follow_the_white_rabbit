from itertools import combinations, permutations
import hashlib
import sys
import multiprocessing
from joblib import Parallel, delayed
import numpy as np
import symbol_prime

CONTROL_HASHES = ['e4820b45d2277f3844eac66c903e84be',
                  '23170acc097c24edb98fc5488ab033fe',
                  '665e5bcb0c20062fe8abaaf4628bb154']

##############################################################################
#  Obsolete solution going through all combinations
##############################################################################

def check_hash(words):
    perms = permutations(words)
    string = ''
    for perm in perms:
        for word in perm:
            string += word + ' '
        string = string[:-1]
        md5 = hashlib.md5(string.encode('utf-8')).hexdigest()
        if md5 in CONTROL_HASHES:
            print(md5)
            return string
        string = ''

    return None


def suspicious_words(combs, tup):
    ret = []
    for comb in combs:
        ret.append(comb[0])
    ret.append(tup[0])

    return ret


def solve_puzzle(wordlist, anagram, combs):
    anagram_repr = symbol_prime.word_prime_product(anagram)
    print(anagram_repr)
    words_and_primes = []
    for word in wordlist:
        tup = (word, symbol_prime.word_prime_product(word))
        words_and_primes.append(tup)

    combs = combinations(words_and_primes, combs)

    for comb in combs:
        prod = 1
        for tup in comb:
            prod *= tup[1]
        if prod == anagram_repr:
            secret_phrase = check_hash(comb)
            if secret_phrase:
                print('---------------SOLUTION----------------')
                print(secret_phrase)
                print('---------------SOLUTION----------------')


def process_combination(comb, words_and_primes, anagram_repr):
    prod = 1
    for tup in comb:
        prod *= tup[1]

    for tup in words_and_primes:
        prod_new = prod * tup[1]
        if prod_new == anagram_repr:
            susp_words = suspicious_words(comb, tup)
            secret_phrase = check_hash(susp_words)
            if secret_phrase:
                print('SOLUTION:', secret_phrase)
        elif prod_new > anagram_repr:
            break


def solve_puzzle_cut(wordlist, anagram, combs):
    """ An advancement over the slightly more naive solution - Creates combinations of
    (combs - 1) words and sorts the words and their prime products into a
    non-decreasing sequence. Then iteratively adds every possible word to each of the
    combination (thus effectively going through all combinations), but cutting
    the branch once a word has been found which creates a product higher than the
    anagram representation, as no words after that can lead to a solution.
    """
    anagram_repr = symbol_prime.word_prime_product(anagram)
    words_and_primes = []
    for word in wordlist:
        tup = (word, symbol_prime.word_prime_product(word))
        words_and_primes.append(tup)
    words_and_primes.sort(key=lambda x: x[1])

    combs = combinations(words_and_primes, combs - 1)
    Parallel(n_jobs=-1)(delayed(process_combination)(comb, words_and_primes, anagram_repr) for comb in combs)


##############################################################################
#   Iterative solutions (building the combinations/branch and bound)
##############################################################################

def can_be_anagram(words_repr, anagram_repr):
    """ Function deciding whether a word combination can still lead to a
    solution, based on the fact that the prime representation of the
    anagram has to be divisible by the prime representation of the
    word combination.
    """
    if anagram_repr % words_repr != 0:
        return False
    return True


def decide_solution(solution):
    string = ''
    perms = permutations(solution)
    for perm in perms:
        for word in perm:
            string += word[0] + ' '
        string = string[:-1]
        md5 = hashlib.md5(string.encode('utf-8')).hexdigest()
        if md5 in CONTROL_HASHES:
            print('SOLUTION:', string, md5)
            return True
        string = ''

    return None


# A communicating queue for worker threads calculating MD5
QUEUE = multiprocessing.Queue()

def md5_worker(queue):
    while True:
        sol = queue.get(True)
        if sol == 'DEATHPILL':
            return
        decide_solution(sol)



def solve_puzzle_aux(idx, words, to_add, curr_solution, max_len, anagram_repr, current_product):
    new_solution = curr_solution[:]
    if idx >= len(words):
        return
    if to_add:
        new_solution.append(words[idx])
        current_product *= words[idx][1]
        if not can_be_anagram(current_product, anagram_repr):
            return
        if len(new_solution) == max_len:
            if anagram_repr == current_product:
                #decide_solution(new_solution)
                QUEUE.put(new_solution)
            return
    
    solve_puzzle_aux(idx=idx+1, words=words, to_add=True, curr_solution=new_solution, max_len=max_len,
                     anagram_repr=anagram_repr, current_product=current_product)
    solve_puzzle_aux(idx=idx+1, words=words, to_add=False, curr_solution=new_solution, max_len=max_len,
                     anagram_repr=anagram_repr, current_product=current_product)


def solve_puzzle_rec(wordlist, anagram, max_len):
    sys.setrecursionlimit(len(wordlist) + 200)
    anagram_repr = symbol_prime.word_prime_product(anagram)
    words_and_primes = []
    for word in wordlist:
        tup = (word, symbol_prime.word_prime_product(word))
        words_and_primes.append(tup)

    pool_size = 1
    pool = multiprocessing.Pool(pool_size, md5_worker, (QUEUE,))

    solve_puzzle_aux(idx=-1, words=words_and_primes, to_add=False, curr_solution=[], max_len=max_len, anagram_repr=anagram_repr,
                     current_product=1)

    for i in range(pool_size):
        QUEUE.put('DEATHPILL')

##############################################################################
#  Numpy/vector variation
##############################################################################

def build_occurences_vector(word, symbols):
    occs = []
    for symbol in symbols:
        occs.append(word.count(symbol))

    return np.array(occs)


def solve_puzzle_numpy_aux(idx, words, to_add, curr_solution, max_len, anagram_occs, current_occs):
    new_sol = curr_solution[:]
    if idx >= len(words):
        return
    if to_add:
        new_occs = current_occs + words[idx][1]
        new_sol.append(words[idx])
        diff = anagram_occs - new_occs
        if np.any(diff < 0):
            return
        if len(new_sol) == max_len:
            if np.array_equal(anagram_occs, new_occs):
                decide_solution(new_sol)
            return
    else:
        new_occs = np.copy(current_occs)

    solve_puzzle_numpy_aux(idx=idx+1, words=words, to_add=True, curr_solution=new_sol, max_len=max_len,
                           anagram_occs=anagram_occs, current_occs=new_occs)
    solve_puzzle_numpy_aux(idx=idx+1, words=words, to_add=False, curr_solution=new_sol, max_len=max_len,
                           anagram_occs=anagram_occs, current_occs=new_occs)



def solve_puzzle_numpy(wordlist, anagram, max_len):
    """ Anagrams are recognized as vectors where each element represents
    frequency of a symbol in a word. A solution is found by adding the found
    vectors together. If the vector is equal to the vector in anagram, a
    potential solution has been found. If the vector contains any
    negative values, it cannot lead to a solution.
    """
    sys.setrecursionlimit(len(wordlist) + 200)
    no_ws_anagram = anagram.replace(' ', '')
    symbol_count = len(set(no_ws_anagram))
    symbols = list(set(no_ws_anagram))
    symbols.sort()
    anagram_occurences = build_occurences_vector(anagram, symbols)
    
    words_and_occs = []
    for word in wordlist:
        tup = (word, build_occurences_vector(word, symbols))
        words_and_occs.append(tup)

    curr_occs = np.array([0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0])

    solve_puzzle_numpy_aux(idx=-1, words=words_and_occs, to_add=False, curr_solution=[],
                           max_len=max_len, anagram_occs=anagram_occurences, current_occs=curr_occs)
