# Neural Net Crossword Solver

## IDEA

This is a python application which inlcudes functionality to automatically solve crossword puzzles.
This consists of two steps:

1. Use a neural network based on NLP methods to parse the clues of the puzzle and output a distibution over possible answers.
Here we constrain the length of the word based on the grid, but do not take into account that different entries which intersect be consistent.
2. Using this probability distribution, use a priority search to find the most likely consistent solution to the puzzle.

In more detail, the input and output puzzles are taken in the *.puz format, and we use the ["puz" package](https://github.com/alexdej/puzpy) to parse these files.

We will experiment with several ways of parsing the input, with a goal to fine tune the BERT model.  
For the priority search, we will experiment with several heuristics to try to find an optimal or near-optimal solution as quickly as possible 

## FILES

**board.py** - main GUI for user to solve crosswords, loaded as a puz file

**puz_scaper.py** - downloads crossword puz files from web, saves into folder ./puzzles

**clue_scraper.py** - extracts clues and answers from puz files, assembles into dataset used for training classifier

**clue_model.py** - neural net model that outputs candidate answers given a clue sentence

**clue_solvers.py** - various algorithms that generate a list of candidate answers from the list of clues. includes:

 - oracle - has access to correct answer, can add alternative (wrong) answers as well, used for testing
 - web solver - searches www.wordplays.com for most likely answers for a given clue
 - bert solver - uses BERT model to find candidate answers
 
**solver.py**  - main algorithm to solve crossword using a clue solver to generate candidate clues

## SOLVER ALGORITHM:

### Backtracking

input: 
- crossword puzzle grid with list of clues
- integer parameter 'NUM_EXCLUDED' = maximum number of clues not coming from candidate list
- integer parameter 'MAX_ITERS' = maximum iterations of main loop before quitting

1. obtain list of candidate answers for each entry using a clue solver
2. initialize stack with empty grid
3. main loop:
    - pop element from stack
    - try candidate from most constrained remaining entry (least remaining candidates)
    - check if number of entries with no remaining possible candidates <= NUM_EXCLUDED
    - if so, add to stack and continue, otherwise try next candidate
    - when run out of candidates, try next entry
    - when run out of entries, backtrack
4. continue main loop until find solution or hit MAX_ITERS
5. exit into GUI with (partially) solved grid for inspection

<!---
## TODO:

 - BERT model
    - use as language model?
    - classifier?
    - generative version?
 - web scraper model
    - way to get around banning? (VPN, proxy?)
    - other websites/datasets?
 - solver
    - current backtracking algorithm somewhat slow, can improve?
    - priority queue faster? how to score?
    - way to enforce answers are english words?
    - better OOP? (depends on final algo and mergning with GUI)
 - GUI
    - incoporate better with solver
    - save as puz files upon close?
  
 - get working with gaffney email for fast solving!
!--->
    
## AUTHOR

Brian Willett

Email: bmwillett1 at gmail