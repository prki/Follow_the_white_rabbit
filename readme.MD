# TRUSTPILOT CODE CHALLENGE
## Repository description
This repository contains a solution to the [Follow the white rabbit](https://followthewhiterabbit.trustpilot.com/)
code challenge by Trustpilot. The solution was written in Python and is able to find all three solutions in
feasible time (order of seconds).

Multiple solutions were found and implemented. Some of them still have their remnants in the code
and are described below.

The implementation is by no means absolutely optimal and allows for further optimization to achieve better
times - some of the potential points highlighted in sections below. An important note here is that
while the solutions are found fast, the entire state space is searched for far
longer than that, making the solution efficiency highly dependent on the input, although the later
states searched are less likely to be actual solutions.

## Running the scripts

    python white_rabbit.py wordlist_path num_of_word_combinations

Where num\_of\_word\_combinations is a value containing the number of words which are to
be used for finding a solution.

## Solution
### Recognizing anagrams
Before the algorithmic solutions to the puzzle are presented, the first big question to
tackle is the actual recognization of anagrams. Two options considered (and both implemented)
were the following:
  * Assigning each symbol a prime number and representing a word as a product of its prime numbers.
  Words are anagrams of each other if their prime products are equal.
  * Assigning each word a vector containing the frequency of each symbol. Words are anagrams if these
  vectors are equal.

While the first option is much simpler, it leads to a significant problem when working with large
numbers, especially once they cannot be represented with 32/64bit integers and require bignum
precision, which is far slower, especially [in Python which does not seem to use GMP by default](https://jasonstitt.com/c-extension-n-choose-k).

The other option, on paper, is better suited for Python, thanks to NumPy providing high-performance
vector calculations as it vectorizes the SIMD operations. However, this has not proven to be the
case in the implementation provided in this repository, most likely due to still low values of
prime products as well as many copies performed of the NumPy arrays - however, without running
a profiler, this cannot be determined.

### Filtering words
The original wordlist contains far too many words with many of them not leading to
solutions - either due to being duplicates of words already present or due to
containing symbols which do not appear in the anagram or contain a symbol with
higher frequency than in the anagram (thus not leading to a possible solution).
All these words are filtered out.

### Solution 1 - Traversing all combinations (naive)
The first solution which was explored was generating all the combinations of n words and
seeing if they lead to a solution. While not very efficient time-wise, the solution
was fairly memory-efficient thanks to using Pythonic functions for generating combinations,
which use generators.

A possible solution is then permutated and has the MD5 hash of all the permutations calculated.

The solution was able to find the first two solutions (but not the hard one) in over a minute.
The hard word was not found in a feasible time.

### Solution 2 - Traversing all combinations (slightly less naive)
A large problem with solution 1 is that certain combinations cannot lead to a solution.
However, unless constructing the solutions and going through them (as done in solutions 3/4),
this cannot be decided. Therefore, the solution becomes a mixture - generating combinations
of n-1 words and then adding a new word to them. (This can be further optimized by throwing out combinations
which couldn't lead to a solution immediately). The words are however sorted by their
prime product value in a nondecreasing way. Therefore, once a word is found which results in a prime product value higher than
the prime product of the anagram, the calculation of that specific combination can stop, as no next
word will be able to be the solution.

This solution was found to be slightly better - but importantly, very trivial to parallelize. After
parallelization, the solutions to the first 2 words were found very fast, although not the hard word.

### Solution 3 - Building the combinations recursively
The solution which has showed itself to be the most effective (especially after sorting the original wordlist,
as described in the section below) was a recursive branch & bound solution to the problem, building
the word combinations from each word and cutting the branch whenever it could not lead to a solution.
A combination which cannot lead to a solution is one which does not divide the anagram product value (meaning
it contains one of the primes more than the anagram).

#### Sorting the original wordlist
The original wordlist was sorted to be searched more efficiently with the solution. Building combinations from
certain words first can lead to finding the solution faster, as certain combinations are more likely to lead
to a solution. More specifically the ones which:
  * Are longer.
  * Contain symbols which have rare occurence in the anagram.

Based on these two parameters, the weight of each word is calculated and the word list is sorted based on
these weights. Performing this lead to a significant speed of finding the solutions.

### Solution 4 - Building the combinations recursively (NumPy)
This solution is the same as solution 3, but based on assigning each word a frequency vector (as noted in the sections
above). However, this solution was slower than the previous one.

## Optimizations
During the course of implementation, many optimizations were necessary to look into - such as not repeating
certain calculations too often (i.e. not calculating a combination product with each new word but retaining it
as a parameter), in order to decrease the calculation time in the main loop.

Two possible optimization points are faster work with MD5 hash control (since many anagrams were found - and
the calculation of MD5 is as naive as possible) and good parallelization.

Parallelization was attempted in the second solution as well as with the MD5 hash evaluation (by creating new
worker processes which would decide whether a potential solution is one of the solutions) in the recursive ones.
While task parallelism could be implemented, the way Python handles parallelization is not ideal for
task parallelism of a recursive case where each task is very simple - this problem being better suited for
example for OpenMP.

For further optimization, a profiler should be used.
