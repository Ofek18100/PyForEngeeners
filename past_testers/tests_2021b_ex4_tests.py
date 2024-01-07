'''
Python for Engineers 2021a Ex4
'''
from copy import deepcopy
import numpy as np
from TestResults import TestResult


########## Result Checkers ###########

def handler(signum, frame):
    '''
    Register an handler for the timeout
    :param signum: SIGNAL number to handle
    :param frame:
    :return: None
    '''

    print("Infinite loop encountered!")
    raise TimeoutError("Infinite loop encountered!")

def wrongAnsMsgGenerator(case_expected, stud_ans):
    return f'Wrong answer, expected output: {case_expected}, got: {stud_ans}.'


def simpleTester(student_func, cases, expected_outputs, err_code) -> dict:
    err_dict = {}

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected_outputs), 1):
        res, msg = testSingleCase(student_func, case_args, case_expected)
        err_dict.update(proccessTestRes(err_code, case_num, res, msg))

    return err_dict


def testSingleCase(student_func, case_args, case_expected) -> tuple:
    # signal.signal(signal.SIGALRM, handler)
    try:
        # If case args is a tuple, such as in the case of a fucntion that recieves more than one args, then unpack it
        # signal.alarm(3)  # Make sure there are no infinite loops
        stud_ans = student_func(*case_args) if (type(case_args) == tuple) \
            else student_func(case_args)
        # signal.alarm(0)  # Turn off the timer
        compare = stud_ans == case_expected
        if not compare:
            return (TestResult.INCORRECT, wrongAnsMsgGenerator(case_args, case_expected))

    except Exception as e:
        return (TestResult.ERROR, f"Student_func raised: {e} on input {case_args}")

    return TestResult.OK, "Passed"


def proccessTestRes(err_code, case_num, res: TestResult, msg):
    if not res == TestResult.OK:  # If res was anything but ok mark an error and return it
        return {f'{err_code}{case_num}{res.value}': {msg}}

    return {}


############## EX3 Specific Testers ##############

def testQ1(student_func, err_code):
    cases = ['z', 'CCbccccbbb', 'CCaa']
    # Expected values list
    expected = ['z', 'b', 'C']

    return simpleTester(student_func, cases, expected, err_code)


def testQ2(student_func, err_code):
    # Sparse Matrcies
    M1 = {(1, 1): 1}
    M2 = {(2, 2): 2}
    M3 = {(1, 1): 2, (5, 5): -5, (5, 4): 2}
    M4 = {(1, 1): -1}
    M5 = {(5, 5): -1, (5, 4): 2}

    cases = [[deepcopy(M1), deepcopy(M1), deepcopy(M1)],
             [deepcopy(M1), deepcopy(M1)],
             [deepcopy(M1), deepcopy(M3)],
             [deepcopy(M1), deepcopy(M2), deepcopy(M5), deepcopy(M1)]]

    expected = [{(1, 1): -1},
                {},
                {(1, 1): -1, (5, 5): 5, (5, 4): -2},
                {(5, 5): 1, (5, 4): -2, (2, 2): -2}]

    return simpleTester(student_func, cases, expected, err_code)



def testQ3(student_func, err_code):
    cases = [('whole', 5),
             ('single', 1),
             ('aaaaaa', 3),
             ('abacaba', 2)]

    expected = [{'whole': [0]},
                {'s': [0], 'i': [1], 'n': [2], 'g': [3], 'l': [4], 'e': [5]},
                {'aaa': [0, 1, 2, 3]},
                {'ab': [0, 4], 'ba': [1, 5], 'ac': [2], 'ca': [3]}]

    return simpleTester(student_func, cases, expected, err_code)

q4a1 = [('Rina', 'Math'), ('Yossi', 'Chemistry'), ('Riki', 'python'), ('Rina', 'pYthon'), ('Yossi', 'biology')]
q4a2 = [('Rina', 'Math'), ('Rina', 'Calculus'), ('Rina', 'Algebra')]
q4a3 = [('Rina', 'Math'), ('rina', 'Calculus'), ('RINA', 'ALGEBRA')]


# def compare_dicts_q4(stud_ans, expected):
#     comp = True
#     if stud_ans.keys() != expected.keys():
#         return False
#
#     for key in stud_ans.keys():
#         if sorted(stud_ans[key])


def testQ4a(student_func, err_code):
    err_dict = {}
    cases = [deepcopy(q4a1), deepcopy(q4a2), deepcopy(q4a3)]
    expected = [{'rina': ['math', 'python'],  'yossi': ['biology', 'chemistry'], 'riki': ['python']},
                {'rina': ['algebra', 'calculus', 'math']},
                {'rina': ['algebra', 'calculus', 'math']}]

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected), 1):
        res = TestResult.OK
        msg = "Passed"
        try:
            stud_ans = student_func(case_args)
            # First we sort student ans in order to compare between the dicts
            for key in stud_ans.keys():
                stud_ans[key].sort()

            compare = stud_ans == case_expected
            if not compare:
                msg = wrongAnsMsgGenerator(case_expected, stud_ans)
                res = TestResult.INCORRECT

        except Exception as e:
            msg = f"Student_func raised: {e} on input {case_args}"
            res = TestResult.ERROR

        err_dict.update(proccessTestRes(err_code, case_num, res, msg))

    return err_dict


q4b1 = {'rina': ['math', 'python'],  'yossi': ['chemistry', 'biology'],  'riki': ['python']}
q4b2 = {'rina': ['math', 'calculus', 'algebra']}

def testQ4b(student_func, err_code):
    err_dict = {}
    cases = [deepcopy(q4b1), deepcopy(q4b2)]
    expected = [{'rina': 2, 'yossi': 2, 'riki': 1},
                {'rina': 3}]

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected), 1):
        res = TestResult.OK
        msg = "Passed"
        try:
            # If case args is a tuple, such as in the case of a fucntion that recieves more than one args, then unpack it
            stud_ans = student_func(case_args)
            #Student shouldn't return value it sohuld instead edit the input dict.
            compare = case_args == case_expected
            if not compare:
                msg = wrongAnsMsgGenerator(case_expected, case_args)
                res = TestResult.INCORRECT

            if(stud_ans!=None):
                msgNoneTest = "Student function returned a value instead of returning None/Not returning at all"
                err_dict.update(proccessTestRes(err_code, 0 , TestResult.INCORRECT, msgNoneTest))

        except Exception as e:
            msg = f"Student_func raised: {e} on input {case_args}"
            res = TestResult.ERROR

        err_dict.update(proccessTestRes(err_code, case_num, res, msg))



    return err_dict


