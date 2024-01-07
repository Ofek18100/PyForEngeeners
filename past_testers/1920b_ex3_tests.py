'''
Python for Engineers 2019-2020 Sem A&B Ex3
'''
import re
import editdistance
from collections import namedtuple
import numpy as np

INEXACT_PRINT_CODE = 'J'
INEXACT_CALCULATION_CODE = 'L'

########## Result Checkers ###########
'''
Here you can define custom checker functions that check the result of a single test case.
The checker function should receive the expected result and actual output (as two arguments).
After performing the check, it should return the following:
Return True if the check passes
Return False if fails
Otherwise, can also return a list of special codes (strings) for special comments/failures.
'''
def compareAnswer(student, expected, mustInclude=[]):
    '''

    :param student:
    :param expected:
    :param mustInclude:
    :return:
    '''
    p = r'\d+(?:\.\d+)?'
    #remove spaces
    student = student.strip()
    #find numbers int both answers and expected and compare them
    studNums, expNums = re.findall(p, student), re.findall(p, expected)
    #compare amount of numbers
    if len(studNums) != len(expNums):
        return False

    #compare values of numbers up to 3 decimals
    for studNum, expNum in zip(studNums, expNums):
        if round(float(studNum),3) != round(float(expNum),3): # Compare up to 3 decimals
            return False

    #search for minimal sub patterns that must be included
    for s in mustInclude:
        if s.lower() not in expected.lower():
            return False

    #remove all digits from text
    studText, expText = re.sub(p, '', student), re.sub(p, '', expected)

    #Compare the text after removal if they are equal return true
    if studText == expText:
        return True

    #else return True or False according to editdistance
    return int(editdistance.eval(studText.lower(), expText.lower()))


def compareNumsTexts(expected, studentOut):
    '''
    Extracts numbers and text from the output and expected result and checks each of them separately.
    Returns a tuple with 3 values:
    1. Result of comparing the numbers (Boolean)
    2. Boolean indicating whether the match is exact
    3. Edit distance (int) between the *lowered* versions of the expected and output string

    (If it'S only a case mismatch, the second value will be False even though the edit distance is 0)
    '''
    expected, studentOut = expected.strip(), studentOut.strip()
    p = R'\d+(?:\.\d+)?'  # Number pattern
    studNums, expNums = re.findall(p, studentOut), re.findall(p, expected)

    numsResults = False
    if len(studNums) == len(expNums):
        for studNum, expNum in zip(studNums, expNums):
            if round(float(studNum),5) != round(float(expNum),5): # Compare up to 5 decimals (can be used to avoid punishing those who rounded)
                break
        else:
            numsResults = True

    studText, expText = re.sub(p, '', studentOut), re.sub(p, '', expected)
    editDistance = int(editdistance.eval(studText.lower(), expText.lower()))

    return (numsResults, studText == expText, editDistance)

class TypeDiffError(TypeError):

    pass

def wrongAnsMsgGenerator(case_expected, stud_ans):
    return f'Wrong answer, expected output: {case_expected}, got: {stud_ans}.'

def CheckOutputType(stud_output, types_list):
    if type(stud_output) not in types_list:
        raise TypeDiffError

def simpleTester(student_func, case_args, case_expected):


    if not (type(case_args) == list or type(case_args) == tuple):
        stud_ans = student_func(case_args)

    else:
        stud_ans = student_func(case_args[0], case_args[1])

    CheckOutputType(stud_ans, [type(case_expected)])

    res = simpleNumsComparision(case_expected, stud_ans)

    return \
        (True, stud_ans) if res \
        else (False, wrongAnsMsgGenerator(case_expected, stud_ans))

def simpleNumsComparision(expected, studentOut):
    # The output is a simple integer in this question, nothing fancy
    return studentOut == expected


############## EX3 Specific Testers ##############


def testQ4(student_func, case_args, case_expected):


    pre_id = id(case_args)
    stud_ans = student_func(case_args)
    post_id = id(case_args)
    res = True


    # Check that the the student indeed preformed changes inplace exp=None is the sign for the pseudo test (D6)
    if(case_expected == None and pre_id != post_id):
        return ('Nsimi', f'Retuned new list instead of chainging inplace: prev id: {pre_id}, now: {post_id}')


    # Check the case the student had to return -1

    if type(case_expected) != list:
        res = (stud_ans == -1)
        return (True, stud_ans) if res \
                else (False, wrongAnsMsgGenerator(case_expected, stud_ans))

    # Check the case the student had to edit a list
    for exp, _stud_out in zip(case_expected, case_args):
        if exp!= _stud_out:
            res = False

    return \
        (True, stud_ans) if res \
        else (False, wrongAnsMsgGenerator(case_expected, stud_ans))



def testQ5(student_func, case_args, case_expected):

    # Check that the the student indeed preformed changes inplace
    # The use of None is to create a pseaudo test and to raise this error in addition to all else
    if(case_expected is None):
        old_mat = np.array(case_args)
        stud_mat = student_func(case_args[0], case_args[1])
        new_mat = np.array(case_args)

        if not np.array_equal(old_mat, new_mat):
            return ('N', f'{old_mat}, changed original matrix to: {new_mat}')
        else:
            return (True, stud_mat)


    stud_mat = student_func(case_args[0], case_args[1])
    CheckOutputType(stud_mat, [list])
    stud_mat = np.array(stud_mat)

    res = (np.array_equal(stud_mat, case_expected), stud_mat)
    return \
        (True, stud_mat) if res \
            else (False, wrongAnsMsgGenerator(case_expected, stud_mat))

def testQ6(student_func, case_args, case_expected):

    # Check that the the student indeed preformed changes inplace
    # The use of None is to create a pseaudo test and to raise this error in addition to all else
    if (case_expected is None):
        old_mat = np.array(case_args)
        stud_mat = student_func(case_args)
        new_mat = np.array(case_args)
        if not np.array_equal(old_mat, new_mat):
            return ('N', f'{old_mat}, changed original matrix to: {new_mat}')
        else:
            return (True, stud_mat)

    stud_ans = (student_func(case_args))
    CheckOutputType(stud_ans, [list])
    stud_mat = np.array(stud_ans)

    res = (np.array_equal(stud_mat, case_expected), stud_mat)
    return \
        (True, stud_mat) if res \
            else (False, wrongAnsMsgGenerator(case_expected, stud_mat))



############## EX3 Specific variables ##############

M1 = [[1, 2], [3, 4], [5, 6]]
M2 = [[1], [2], [3]]
M3 = [[355]]
M4 = [[9, 8, 3], [4, 6, 6], [5, -1, 5]]

NUM_OF_QUESTIONS = 6


QuestionHandler = namedtuple('QuestionHandler', ['func_name', 'args', 'expected', 'testerFunc', 'err_code'])

Q1_handler = QuestionHandler('sum_divisible_by_k', [
                        #Args lists
                         ([1, 2, 3], 5),
                         ([], 5),
                         ([20, 17, -100, 25, 16], 4),
                         ([5, 50, 500, 100], 5),
                         ([1, 2, 3, 4], 0.5)],
                         # Expected values list
                         [0, 0, -64, 655, 10],
                 simpleTester, 'A')




Q2_handler = QuestionHandler('mult_odd_digits',
                     [5, 4, 872394561, 300000],  #Args lists
                     [5, 1, 945, 3], # Expected values list
                     simpleTester,
                     'B')

Q3_handler = QuestionHandler('count_longest_repetition',
                             [ #Args lists
                                 ['no numbers', '1'],
                                 ['r', 'r'],
                                 ['rrawrrrawrrar', 'r'],
                                 ['rraaarrrrr', 'r'],
                                 ['rrrraaarrr', 'r']
                                 ],
                             [0, 1, 3, 5, 4], # Expected values list
                             simpleTester, 'C')

Q4_handler = QuestionHandler('upper_strings',
                             [ #Args lists
                                 [2.4, None, ['dont change me']],
                                 ['change me', 13, 15, 'and me', [45]],
                                 None,
                                 1.1],
                                 # Expected values list
                                 [
                                 [2.4, None, ['dont change me']],
                                 ['CHANGE ME', 13, 15, 'AND ME', [45]],
                                  None,
                                  None ],
                             testQ4, 'D')

Q5_handler = QuestionHandler('div_mat_by_scalar',
                             [ #Args lists
                                 (M1, -2),
                                 (M2, 2),
                                 (M3, 9),
                                 (M4, 5),
                                 (M4, 5)],
                             [ # Expected values list
                                 [[-1, -1],[-2,-2], [-3, -3]],
                                 [[0], [1], [1]],
                                 [[39]],
                                 [[1, 1, 0], [0, 1, 1], [1, -1, 1]],
                                  None],
                             testQ5, 'E')

Q6_handler = QuestionHandler('mat_transpose',
                               [#Args lists
                                M1, M2, M3, M4, M4],
                                # Expected values list
                                [np.array(M1).T,
                                  np.array(M2).T,
                                  np.array(M3).T,
                                  np.array(M4).T,
                                  None],
                             testQ6, 'F')

QHandler_lst = [Q1_handler, Q2_handler, Q3_handler, Q4_handler, Q5_handler, Q6_handler]
