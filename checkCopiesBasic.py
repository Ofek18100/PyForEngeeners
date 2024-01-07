import os
import subprocess
import sys
from multiprocessing import Pool
import itertools
import pycode_similar
import glob
import pandas as pd
from configparser import ConfigParser, ExtendedInterpolation
'''
Requirements:
19.04 - adapted to python 3.6+ by Dror 
*Install pycode-similar (https://pypi.org/project/pycode-similar/)
*There must be no syntax errors in the compared files!
'''
get_name = lambda filepath: filepath.split('assign')[0].split('/')[-1].split('_')[0]
THR = 80  # Threshold


def main(file_list):
    print("Preforming copy-testing for files")

    tasks = filter(lambda ex_pair: all(ex.endswith('.py') for ex in ex_pair), itertools.combinations(file_list, 2))
    p = Pool(processes=4)
    res = p.map(check_pair, tasks)
    # Keep high similiarty
    # res = filter(lambda x: x[0] >= THR, res)


    res = map(lambda r: (r[0], get_name(r[1]), get_name(r[2])), res)

    # for result in sorted(res, reverse=True):
    #     print(result)

    OUT_PATH = configParser["paths"]["out_path"]
    EX_NUM = configParser["misc"]["EX_NUM"]
    df = pd.DataFrame(res, columns =['Max similarity', 'Student 1', 'Student 2'])
    df.to_csv(f'{OUT_PATH}/student_similarities_ex{EX_NUM}.csv')
    print(df.describe())
    return res

def check_pair(exs):
    '''

    :param exs:
    :return:
    '''

    ex1, ex2 = exs
    print(f"Now verifying: {get_name(ex1)}, {get_name(ex2)}.")
    # Run pycode similar
    try:
        res = subprocess.check_output(['pycode_similar', ex1, ex2])
        # Decode answer from bytes object back to string
        res = str(res, 'utf-8')
        # Isolate the number representing the similarity score
        score1 = float(res.split('\n')[2].split('%')[0])

        # Repeat vice versa because this is not similiar
        res = subprocess.check_output(['pycode_similar', ex1, ex2])
        # Decode answer from bytes object back to string
        res = str(res, 'utf-8')
        # Isolate the number representing the similarity score
        score2 = float(res.split('\n')[2].split('%')[0])

    except:
        print(f"Skipping: {get_name(ex1)}, {get_name(ex2)}. due to exception")
        return (0, ex1, ex2)


    ret = (max(score1, score2), ex1, ex2)
    return ret


if __name__ == '__main__':

    global config_parser
    configParser = ConfigParser(interpolation=ExtendedInterpolation())
    configParser.read("config.ini")

    main_path = configParser["misc"]["resource_path"]
    # Read from here
    submissions_dir = configParser["paths"]["main_path"]

    sys.path.append(submissions_dir)
    files_list = [os.path.abspath(file) for file in glob.glob(os.path.join(submissions_dir, "*.py"))]
    main(files_list)
