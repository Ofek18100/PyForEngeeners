'''
Python for Engineers 2019-2020 Sem A&B Ex4
'''
import re
import editdistance
from collections import namedtuple
from copy import deepcopy

QuestionHandler = namedtuple('QuestionHandler', ['func_name', 'args', 'expected', 'testerFunc', 'err_code'])
INEXACT_PRINT_CODE = 'J'
INEXACT_CALCULATION_CODE = 'L'
class TypeDiffError(TypeError):
    pass

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



def wrongAnsMsgGenerator(case_expected, stud_ans):
    return f'Wrong answer, expected output: {case_expected}, got: {stud_ans}.'

def CheckOutputType(stud_output, types_list):
    if type(stud_output) not in types_list:
        raise TypeDiffError

def simpleTester(student_func, case_args, case_expected):

    case_args = deepcopy(case_args)

    if not (type(case_args) == list or type(case_args) == tuple):
        stud_ans = student_func(case_args)

    elif len(case_args) == 1:
        stud_ans = student_func(case_args[0])
    else:
        stud_ans = student_func(case_args[0], case_args[1])

    CheckOutputType(stud_ans, [type(case_expected)])

    res = simpleObjComparision(case_expected, stud_ans)

    return \
        (True, stud_ans) if res \
        else \
            (False, wrongAnsMsgGenerator(case_expected, stud_ans))

def simpleObjComparision(expected, studentOut):
    # The output is a simple integer in this question, nothing fancy
    return studentOut == expected


def MockTester(student_func, err_code):
    return {} if student_func(txt1) == 'z' else {f"{err_code}a": 'Wrong answer'}



############## EX4 Specific Testers ##############

############## EX4 Specific variables ##############


NUM_OF_QUESTIONS = 5

txt1 = 'z'
txt2 = 'CCbccccbbb'
# txt3 = "Computer programming can be a hassle " \
#        "It's like trying to take a defended castle " \
#        "When the program runs you shout with glee " \
#        "But when you get errors you cry with plea"
# txt3 = txt3.replace(' ', '')
#
# with open('/Users/dror/PycharmProjects/PyProg1920Bex4/Ex4 Grading Key - מפתח ציונים תרגיל 4/sources/q1_A4_input.txt', 'r') as myfile:
#     txt4 = myfile.read()
# txt4 = txt4.replace(' ', '')

# Sparse Matrcies
M1 = {(1, 1): 1}
M2 = {(2, 2): 2}
M3 = {(1, 1): 2, (5, 5): -5, (5, 4): 2}
M4 = {(1, 1): -1}
M5 = {(5, 5): -1, (5, 4): 2}

Q1_handler = QuestionHandler('most_popular_character', [
                        #Args lists
                         [txt1],
                         [txt2]],
                         # [txt3]],
                         # [txt4]],
                         # Expected values list, decided to use the function from the solution this time
                         ['z', 'b'],
                 simpleTester, 'A')



Q2_handler = QuestionHandler('diff_sparse_matrices',
                     [
                         [[M1, M1, M1]],
                             [[M1, M1]],
                             [[M1, M3]],
                             [[M1, M2, M5, M1]]],
                    [{(1, 1): -1}, # Expected values list
                     {},
                     {(1, 1): -1, (5, 5): 5, (5, 4): -2},
                     {(5, 5): 1, (5, 4): -2, (2, 2): -2}],
                     simpleTester,
                     'B')



Q3_handler = QuestionHandler('find_substring_locations',
                             [ #Args lists
                                 ['whole', 5],
                                 ['single', 1],
                                 ['aaaaaa', 3],
                                 ['abacaba', 2],
                                 ],
                             [{'whole': [0]}, # Expected values list
                              {'s': [0], 'i': [1], 'n': [2], 'g': [3], 'l': [4], 'e': [5]},
                              {'aaa': [0, 1, 2, 3]},
                              {'ab': [0, 4], 'ba': [1, 5], 'ac': [2], 'ca': [3]}],
                             simpleTester, 'C')


q4a = [('Rina', 'Math'), ('Yossi', 'Chemistry'),
                            ('Riki', 'python'), ('Rina', 'pYthon'), ('Yossi', 'biology')]
q4b = [('Rina', 'Math'), ('Rina', 'Calculus'), ('Rina', 'Algebra')]
q4c = [('Rina', 'Math'), ('rina', 'Calculus'), ('RINA', 'ALGEBRA')]


Q4_handler = QuestionHandler('courses_per_student',
                             [ #Args lists
                                 [q4a], [q4b], [q4c]],
                             # Expected values list
                             [{'rina': ['math', 'python'], 'yossi': ['chemistry', 'biology'], 'riki': ['python']},
                                  {'rina': ['math', 'calculus', 'algebra']},
                                  {'rina': ['math', 'calculus', 'algebra']}],
                             simpleTester, 'D')

Q5_handler = QuestionHandler('students_per_course',
                             [ #Args lists
                                 [q4a], [q4b], [q4c]],
                             # Expected values list
                             [{'rina': 2, 'yossi': 2, 'riki': 1},
                              {'rina': 3},
                              {'rina': 3}],
                             simpleTester, 'E')



QHandler_lst = [Q1_handler, Q2_handler, Q3_handler, Q4_handler, Q5_handler]
