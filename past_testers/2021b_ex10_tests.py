'''
Python for Engineers 2021b Ex10
'''
import signal

from TestResults import TestResult
import re
import inspect
import numpy as np
import pandas as pd
import past_solutions_temp.ex10_solution_2021a as sol

########## Result Checkers ###########

def search_for_forbidden_patterns(ptrn_list, student_code) -> tuple:
    '''
    Search the student'S source code and return True if it has 'pattern' in it.
    This could be used to look for imports of certain packages or for use of certain functions.
    :param pattern: to search for.
    :param student_code: Student module or func to search in.
    :return: True if 'text' exists in the source of 'student_module'
    '''
    stud_source = inspect.getsource(student_code)

    # split student code into lines, remove lines that strat with '#' or some spaces and then '#'
    comment_pattern = r'^(\s*#)'
    code_lines = [line for line in stud_source.splitlines() if not re.search(comment_pattern, line)]

    for p in ptrn_list:
        # Search all code lines for pattern p, map it to True if found
        search_res = map(lambda line: bool(re.search(p, line)), code_lines)
        # Reduce a list of booleans to result, if p was found in any of the lines, return true
        if any(search_res):
            # print(code_lines)
            # print(p)
            return True, p

    return False, None

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
    signal.signal(signal.SIGALRM, handler)
    try:
        # If case args is a tuple, such as in the case of a fucntion that recieves more than one args, then unpack it
        signal.alarm(3)  # Make sure there are no infinite loops
        stud_ans = student_func(*case_args) if (type(case_args) == tuple) else student_func(case_args)
        signal.alarm(0)  # Turn off the timer
        compare = stud_ans == case_expected
        if not compare:
            return (TestResult.INCORRECT, wrongAnsMsgGenerator(case_expected, stud_ans))

    except Exception as e:
        if (type(e) == TimeoutError):
            return (TestResult.ENDLESS_LOOP, f"Student_func took more than 3 seconds on input {case_args}")
        return (TestResult.ERROR, f"Student_func raised: {e} on input {case_args}")

    return TestResult.OK, "Passed"


def proccessTestRes(err_code, case_num, res: TestResult, msg):
    if not res == TestResult.OK:  # If res was anything but ok mark an error and return it
        if type(case_num) == list:
            return {f'{err_code}{case_num}{res.value}': {msg} for case in case_num}

        else:
            return {f'{err_code}{case_num}{res.value}': {msg}}


    return {}



############## EX10 Specific Testers ##############


def testQ1(student_module, err_code):

    err_dict = {}
    file = []
    err_dict.update(testq1a(student_module, err_code))
    err_dict.update(testq1b(student_module, err_code))
    err_dict.update(testq1d(student_module, err_code))
    err_dict.update(testq1c(student_module, err_code))
    err_dict.update(testq1e(student_module, err_code))

    return err_dict


def testq1a(student_module, err_code):

    try:
        student_func = student_module.arr_dist
    except Exception as e:
        return proccessTestRes(err_code, case_num=[1, 2, 3], res=TestResult.ERROR, msg="Failed to import function with: "+ e)


    cases = [( np.array([0]), np.array([0])),
             (np.array([35, 633, 825]), np.array([35, 633, 825])),
             (np.array([44, 532, 1094]), np.array([532, 1094, 44]))
             ]

    expected = [0, 0, 2100]

    return simpleTester(student_func, cases, expected, err_code)


def testq1b(student_module, err_code):
    try:
        student_func = student_module.find_best_place
    except Exception as e:
        return proccessTestRes(err_code, case_num=4, res=TestResult.ERROR, msg="Failed to import function with: "+ e)

    cases = [
        (np.array([[0, 0, 0, 0, 0], [0, 0, 84, 105, 102], [1, 3, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]),
             np.array([87, 101, 108]))
    ]
    expected = [(1, 2)]

    res, msg = testSingleCase(student_func, cases[0], expected[0])
    return proccessTestRes(err_code, 4, res, msg)


def testq1c(student_module, err_code):

    try:
        student_func = student_module.create_image_with_msg
    except Exception as e:
        return proccessTestRes(err_code, case_num=5, res=TestResult.ERROR, msg="Failed to import function with: " + e)


    cases = [
        (np.array([[0,0,0,0,0], [0,0,84,105,102], [1,3,0,0,0], [0,0,0,0,0], [0,0,0,0,0]]), (1,2), np.array([87, 101, 108]))
    ]

    expected = [np.array([[1,2,3,0,0], [0,0,87,101,108], [1,3,0,0,0], [0,0,0,0,0], [0,0,0,0,0]])]

    try:
        signal.alarm(3)  # Make sure there are no infinite loops
        stud_ans = student_func(*cases[0])
        signal.alarm(0)  # Turn off the timer

        true_ans = expected[0]
        res = TestResult.OK if np.array_equal(true_ans, stud_ans) else TestResult.INCORRECT
        return (proccessTestRes(err_code, 5, res, msg=f"Input: {input}"))

    except Exception as e:
        return  proccessTestRes(err_code, 5, TestResult.ERROR, f"Student_func raised: {e} on input {cases[0]}")




def testq1d(student_module, err_code):
    try:
        student_func = student_module.get_message
    except Exception as e:
        return proccessTestRes(err_code, case_num=6, res=TestResult.ERROR, msg="Failed to import function with: " + e)

    cases = [
        np.array([[1, 2, 3, 0, 0], [0, 0, 87, 101, 108], [1, 3, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
    ]

    expected = ['Wel']

    res, msg = testSingleCase(student_func, cases[0], expected[0])
    return proccessTestRes(err_code, 6, res, msg)

def testq1e(student_module, err_code):
    try:
        student_func = student_module.put_message
    except Exception as e:
        return proccessTestRes(err_code, case_num=7, res=TestResult.ERROR, msg="Failed to import function with: " + e)

    cases = [
                (np.array([[0, 0, 0, 0, 0], [0, 0, 84, 105, 102], [1, 3, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]), 'Wel')
             ]
    expected = [
        np.array([[1, 2, 3, 0, 0], [0, 0, 87, 101, 108], [1, 3, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
            ]

    try:
        signal.alarm(3)  # Make sure there are no infinite loops
        stud_ans = student_func(*cases[0])
        signal.alarm(0)  # Turn off the timer

        true_ans = expected[0]
        res = TestResult.OK if np.array_equal(true_ans, stud_ans) else TestResult.INCORRECT
        return (proccessTestRes(err_code, 7, res, msg=f"Input: {input}"))

    except Exception as e:
        return proccessTestRes(err_code, 7, TestResult.ERROR, f"Student_func raised: {e} on input {cases[0]}")


def testQ2(student_module, err_code):

    err_dict = {}
    input_file = '/Users/d_private/Documents/PyProgs/2021b/ex10/sources/missions.csv'
    true_df = sol.read_missions_file(input_file)


    # Test Q2.a - read_missions_file(file_name)
    '''
    Test IO Error in case of a bad file name
    Test that a panda DataFrame is indeed returned
    Check number of columns in 3, Bounty, Expenses, Duration
    The index should be the kingdoms names
    '''
    try:
        stud_func = student_module.read_missions_file
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, case_num=1, res=TestResult.ERROR,
                                   msg="Failed to import function with: " + e))

    # Function import succeeded
    # Case 1
    try:
        stud_df = stud_func(input_file)
        if type(stud_df) != type(true_df): raise TypeError

        res = TestResult.OK if stud_df.equals(true_df) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Input: {input}"))

    except Exception as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, f"Student_func raised: {e}"))


    # Case 2 - non existing file should throw IO Error
    try:
        stud_df = stud_func("Non existing path")
    except Exception as e:
        if not e.__class__ == IOError:
            err_dict.update(proccessTestRes(err_code, 2, TestResult.INCORRECT,
                                            f"Student func raised wrong exception on empty input: {e}"))




    # Q2.b - Case 3 - Test add_daily_gain_col

    # Function should edit inplace
    q2b_df = true_df.copy()
    sol.add_daily_gain_col(true_df)

    # Make a copy for the student as well
    stud_df = true_df.copy()
    try:
        stud_func = student_module.add_daily_gain_col
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, case_num=3, res=TestResult.ERROR,
                                   msg="Failed to import function with: " + e))

    # Import succeeded
    try:
        stud_func(stud_df)

        res = TestResult.OK if stud_df.equals(true_df) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Input: {input}"))

    except Exception as e:
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, f"Student_func raised: {e}"))

    # Q2.c - Case 4 - sum_rewards
    q2c_df = true_df.copy()
    # Make a copy for the student as well
    try:
        stud_func = student_module.sum_rewards
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, case_num=4, res=TestResult.ERROR,
                                        msg="Failed to import function with: " + e))

    # Import succeeded
    try:
        true_ans = sol.sum_rewards(true_df)
        stud_ans = stud_func(q2c_df)


        res = TestResult.OK if stud_ans ==  true_ans else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Input: {input}"))

    except Exception as e:
        err_dict.update(proccessTestRes(err_code, case_num=4, res=TestResult.ERROR,
                                        msg="Failed to import function with: " + e))

    # Q2.d - Case 4 - find_best_kingdom
    q2d_df = true_df.copy()

    try:
        stud_func = student_module.find_best_kingdom
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, case_num=4, res=TestResult.ERROR,
                                        msg="Failed to import function with: " + e))

    # Import succeeded
    try:
        true_ans = sol.find_best_kingdom(true_df)
        stud_ans = stud_func(stud_df)

        res = TestResult.OK if stud_ans == true_ans else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 5, res, msg=f"Input: {input}"))

    except Exception as e:
        err_dict.update(proccessTestRes(err_code, case_num=5, res=TestResult.ERROR,
                                        msg="Failed to import function with: " + e))




    return err_dict