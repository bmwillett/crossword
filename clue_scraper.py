import puz
import os

def get_clues(filename):
    p = puz.read(filename)

    # check if has a solution, otherwise skip
    if p.solution_state > 0:
        return []

    solution = p.solution
    width = p.width
    numbering = p.clue_numbering()

    res = []

    for elem in numbering.across:
        cell, length, clue = elem['cell'], elem['len'], elem['clue']
        answer = ''.join([solution[cell + i] for i in range(length)])
        res.append([clue, answer])

    for elem in numbering.down:
        cell, length, clue = elem['cell'], elem['len'], elem['clue']
        answer = ''.join([solution[cell + i*width] for i in range(length)])
        res.append([clue, answer])

    return res

def get_all_clues(dir):
    res = []
    for fname in os.listdir(dir):
        res.extend(get_clues(dir + fname))

    return res

if __name__ == '__main__':
    res = get_all_clues('./puzzles/')
    import IPython; IPython.embed(); exit(1)