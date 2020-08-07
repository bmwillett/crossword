import puz
import os
import pandas as pd
from sklearn.model_selection import train_test_split

# string appearing between clue and answer, used to prime language model
JOIN_STRING = ' is the answer to: '

def get_clues(filename):
    p = puz.read(filename)

    # check if has a solution, otherwise skip
    if p.solution_state > 0:
        return []

    solution = p.solution
    width = p.width
    numbering = p.clue_numbering()

    clues, answers, clue_answers = [], [], []

    for elem in numbering.across:
        cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
        answer = ''.join([solution[cell + i] for i in range(length)]).lower()
        clues.append(clue)
        answers.append(answer)
        clue_answers.append(answer + JOIN_STRING + clue)

    for elem in numbering.down:
        cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
        answer = ''.join([solution[cell + i] for i in range(length)]).lower()
        clues.append(clue)
        answers.append(answer)
        clue_answers.append(answer + JOIN_STRING + clue)

    return pd.DataFrame(data={'clue': clues, 'answer': answers, 'merged': clue_answers})

def get_all_clues(dir):
    res = [get_clues(dir + fname) for fname in os.listdir(dir)]
    res_df = pd.concat([df for df in res if type(df) is not list])
    train_df, test_df = train_test_split(res_df, test_size=0.2)
    return train_df, test_df

if __name__ == '__main__':
    train_df, test_df = get_all_clues('./data/puzzles/')
    train_df.to_csv('./data/clues_train.csv')
    test_df.to_csv('./data/clues_test.csv')