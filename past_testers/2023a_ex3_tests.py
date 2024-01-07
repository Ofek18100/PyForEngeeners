'''
Python for Engineers 2021a Ex3
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
        stud_ans = student_func(*case_args) if (type(case_args) == tuple) else student_func(case_args)
        # signal.alarm(0)  # Turn off the timer
        compare = stud_ans == case_expected
        if not compare:
            return (TestResult.INCORRECT, wrongAnsMsgGenerator(case_expected, stud_ans))

    except Exception as e:
        return (TestResult.ERROR, f"Student_func raised: {e} on input {case_args}")

    return TestResult.OK, "Passed"


def proccessTestRes(err_code, case_num, res: TestResult, msg):
    if not res == TestResult.OK:  # If res was anything but ok mark an error and return it
        return {f'{err_code}{case_num}{res.value}': {msg}}

    return {}


############## EX3 Specific Testers ##############

def testQ1(student_func, err_code):
    cases = [([1, 2, 3], 5),
             ([], 5),
             ([20, 17, -100, 25, 16], 4),
             ([5, 50, 500, 100], 5),
             ([1.5, 2, 3, 4], 0.5)]

    # Expected values list
    expected = [0, 0, -64, 655, 10.5]

    return simpleTester(student_func, cases, expected, err_code)


def testQ2(student_func, err_code):
    cases = [5, 4, 872394561, 300000]
    expected = [5, 1, 945, 3]
    return simpleTester(student_func, cases, expected, err_code)


def testQ3(student_func, err_code):
    cases = [('no numbers', '1'),
             ('r', 'r'),
             ('rrawrrrawrrar', 'r'),
             ('rrraaarrr', 'r'),
             ('', 'z')]

    expected = [0, 1, 3, 3, 0]
    return simpleTester(student_func, cases, expected, err_code)


def testQ4(student_func, err_code):
    err_dict = {}
    cases = [[2.4, None, ['dont change me']],
             ['change me', 13, 15, 'and me', [45]],
             None,
             'x']
    expected = [[2.4, None, ['dont change me']],
                ['CHANGE ME', 13, 15, 'AND ME', [45]],
                -1,
                -1]

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected), 1):
        try:
            stud_ans = student_func(case_args)
            if (case_num in [1,2] and case_args != case_expected):
                msg = wrongAnsMsgGenerator(case_expected, stud_ans)
                err_dict.update(proccessTestRes(err_code, case_num, TestResult.INCORRECT, msg))

            elif (case_num in [3,4] and stud_ans!=case_expected):
                msg = wrongAnsMsgGenerator(case_expected, stud_ans)
                err_dict.update(proccessTestRes(err_code, case_num, TestResult.INCORRECT, msg))

        except Exception as e:
            err_dict.update(proccessTestRes(err_code, case_num, TestResult.ERROR, f"Student_func raised: {e} on input {case_args}"))

    return err_dict


M1 = [[1, 2], [3, 4], [5, 6]]  # Asymetical
M2 = [[1], [2], [3]]  # Column
M3 = [[355]]  # Singleton
M4 = [[9, 8, 3], [4, 6, 6], [5, -1, 5]]  # Symetrical
M5 = [[1, 2, 3, 4]]  # Row
mat_list = [M1, M2, M3, M4, M5]


def testQ5(student_func, err_code):
    err_dict = {}
    dividers = [-2, 2, 9, 5, 1]
    cases = [(deepcopy(mat), divider) for mat, divider in zip(mat_list, dividers)]
    expected = [np.array(mat)//divider for mat, divider in zip(mat_list, dividers)]

    # Check that the the student did not preform changes inplace
    try:
        old_mat = deepcopy(M1)
        student_func(old_mat, 1)
        new_mat = np.array(M1)

        if not np.array_equal(np.array(old_mat), new_mat):
            err_dict.update(proccessTestRes(err_code, len(cases) + 1, TestResult.INACCURATE,
                                            "The input matrix was changed during the function"))

    except Exception as e:
        err_dict.update(proccessTestRes(err_code, len(cases) + 1, TestResult.ERROR, f"Student_func raised: {e} on input {M1}"))

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected), 1):
        try:
            stud_mat = np.array(student_func(*case_args))
            res = np.array_equal(stud_mat, case_expected)

            if not res:
                msg = wrongAnsMsgGenerator(case_expected, case_args)
                err_dict.update(proccessTestRes(err_code, case_num, TestResult.INCORRECT, msg))

        except Exception as e:
            err_dict.update(
                proccessTestRes(err_code, case_num, TestResult.ERROR,
                                f"Student_func raised: {e} on input {case_args}"))


    return err_dict

def testQ6(student_func, err_code):
    err_dict = {}
    cases = [deepcopy(mat) for mat in mat_list]
    expected = [np.array(mat).T for mat in mat_list]

    try:
        old_mat = deepcopy(M1)
        student_func(old_mat)
        new_mat = np.array(M1)

        if not np.array_equal(np.array(old_mat), new_mat):
            err_dict.update(proccessTestRes(err_code, len(cases) + 1, TestResult.INACCURATE,
                                            "The input matrix was changed during the function"))
    except Exception as e:
        err_dict.update(
            proccessTestRes(err_code, len(cases) + 1, TestResult.ERROR, f"Student_func raised: {e} on input {M1}"))

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected), 1):
        try:
            stud_mat = np.array(student_func(case_args))
            res = np.array_equal(stud_mat, case_expected)

            if not res:
                msg = wrongAnsMsgGenerator(case_expected, case_args)
                err_dict.update(proccessTestRes(err_code, case_num, TestResult.INCORRECT, msg))

        except Exception as e:
            err_dict.update(
                proccessTestRes(err_code, case_num, TestResult.ERROR,
                                f"Student_func raised: {e} on input {case_args}"))

    return err_dict
