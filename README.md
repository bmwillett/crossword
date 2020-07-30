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

**clue_scraper.py** (TBC) - extracts clues and answers from puz files, assembles into dataset used for training classifier

**clue_model.py** (TBC) - model that outputs candidate answers given a clue sentence

**solver.py** (TBC) - algorithm to solve crossword using clue_model to generate candidate clues

## TO DO:

 - create clue_model.py
    - parse output from clue_scraper
    - remove stop words
    - tokenize
    - look into training options (BERT? simpler things?)
    - get more data
    - train and test
 - create solver.py
    - think more about algorithm
    - start with small puzzles
    - start with set of answers provided
 - once both working reasonably well, integrate into GUI
 - get working with gaffney email for fast solving!
    
## AUTHOR

Brian Willett

Email: bmwillett1 at gmail