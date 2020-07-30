"""
Given a crossword (DECIDE FORMAT), and a model to produce candidate words (DECIDE FORMAT), generate most likely solution

for each clue, the model presents a set of candidate answers with probabilities
then the algorithm tries to generate a globally consistent solution with the highest likelihood

--------------------------------
EXAMPLE 2x2 crossword:

clue probabilities:
1A. {'aa': 0.9, 'ab': 0.1}
2A. {'ab': 0.9, 'bb': 0.1}
1D. {'aa': 0.9, 'ab': 0.1}
2D. {'bb': 0.9, 'ab': 0.1}

possible consitent solutions:

AA
BB

probability =  0.9 * 0.1 * 0.1 * 0.1

AB
AB

probability = 0.1 * 0.9 * 0.9 * 0.9

-> second solution is preferred

-------------------------------

Algorithm (first attempt):

1. generate top k answers and probabilites for each clue
2. create a priority queue of partial solutions to explore, initially populated with empty grid
  -> each partial solution is given a score based on likeliness to generate full solution
3. pick highest scoring partial solution.  generate possible extensions to solution (HOW TO TRUNCATE?)
 put these in the priority queue
4. repeat 3 until a solution is found

Open issues:
 - what is a good score function for a partial solution?
    * product of probabilities of all words in grid -> downweights having more words
    * same as above, but also include factor for unsolved words -> factor is parameter of algorithm?
    * should intersections be given positive score? or only consider connected partial solutions?
 - how to add to partial solution? should we restrict to words intersecting words already in the grid?
 - what happens if answer is not among candidates? (especially possible for long clues)


"""