'''
Python for Engineers 2021b Ex9
'''
import past_solutions_temp.ex9_solution_2021b
from TestResults import TestResult
import re
import inspect
import past_solutions_temp.ex9_solution_2021b as sol
import imageio
import numpy as np

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
        print((case_args, case_expected))
        res, msg = testSingleCase(student_func, case_args, case_expected)
        err_dict.update(proccessTestRes(err_code, case_num, res, msg))

    return err_dict

def simpleObjComparision(expected, studentOut):
    # The output is a simple integer in this question, nothing fancy
    return studentOut == expected

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



############## EX6 Specific Testers ##############
## TODO check what about the recusion
# TODO check if cases args should be packed in a list as well

class DimensionsMismatchError(Exception):
    pass

def areNumericArraysEqual(arr1, arr2, th=1e-6):
    if arr2 is None:
        raise TypeError('None value encountered')
    if arr1.shape != arr2.shape:
        raise DimensionsMismatchError('Arrays with different shapes compared')
    return np.max(abs(arr1-arr2.astype('float'))) < th


def areFloatEqual(a,b,th=1e-6):
    return abs(a-b) < th


def areObjEqual(obj1, obj2, student_module):
    if not isinstance(obj2, student_module.Roman):
       raise TypeError("Did not return Roman")
    return obj1.__dict__.items() <= obj2.__dict__.items()

def areRomanPartiallyEqual(obj1, obj2, student_module):
    if not isinstance(obj2, student_module.Roman):
       raise TypeError("Did not return Roman")
    return len(obj2.__dict__.items() - obj1.__dict__.items()) <= 1

def testQ1(student_module, err_code):
    err_dict = {}
    # A1
    input = 'XV'
    true_obj1 = sol.Roman(input)
    try:
        stud_obj1 = student_module.Roman(input)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))
    else:
        res = TestResult.OK if areObjEqual(true_obj1, stud_obj1, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Input: {input}"))


    # A2
    input = -4
    true_obj2 = sol.Roman(input)
    try:
        stud_obj2 = student_module.Roman(input)

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))

    else:
        res = TestResult.OK if areObjEqual(true_obj2, stud_obj2, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 2, res, msg=f"Input: {input}"))

    # A3
    try:
        true_ans = true_obj1.__repr__()
        stud_ans = stud_obj1.__repr__()
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Input: {input}"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

    # A4
    try:

        true_ans = sol.Roman(8).__repr__()
        stud_ans = student_module.Roman(8).__repr__()
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Input: {input}"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))

    # A5
    try:
        true_ans = true_obj2 + (-11) + sol.Roman(2)
        stud_ans = stud_obj2 + (-11) + student_module.Roman(2)
        res = TestResult.OK if areRomanPartiallyEqual(true_ans, stud_ans, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 5, res, msg=f"Input: {input}"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 5, TestResult.ERROR, e))

    # A6
    try:
        true_ans = sol.Roman(-3) < sol.Roman(-2) and sol.Roman(5) > 3
        stud_ans = student_module.Roman(-3) < student_module.Roman(-2) and student_module.Roman(5) > 3
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 6, res, msg=f"Input: {input}"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 6, TestResult.ERROR, e))

    # A7
    try:
        true_ans = sol.Roman(13) // sol.Roman('-V')
        stud_ans = student_module.Roman(13) // student_module.Roman('-V')
        res = TestResult.OK if areRomanPartiallyEqual(true_ans, stud_ans, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 7, res, msg=f"Input: {input}"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 7, TestResult.ERROR, e))

    # A8
    try:
        student_module.Roman(-13) // student_module.Roman('-XV')
    except BaseException as e:
        if not isinstance(e, ValueError):
            msg = 'Wrong exception type: ' + type(e).__name__ + ':  ' + str(e)
            err_dict.update(proccessTestRes(err_code, 8, res, msg))

    else:
        err_dict.update(proccessTestRes(err_code, 8, res, msg=f"Input: {input}"))

    return err_dict

def testQ2(student_module, err_code):
    err_dict = {}

    input_path = r'/Users/d_private/Documents/PyProgs/2021b/ex9/sources/weight_input.csv'

    true_dict = sol.load_training_data(input_path)
    err_dict.update(test_q2a(student_module,true_dict))

    if ('B2' in err_dict and 'B3' in err_dict) or ('B2X' in err_dict and 'B3X' in err_dict):
        try:
            checked_dict = student_module.load_training_data(input_path)
        except:
            checked_dict = true_dict.copy()
    else:
        checked_dict = true_dict.copy()

    err_dict.update(test_q2BtoE(student_module,true_dict,checked_dict))

    return err_dict


def test_q2a(student_module, true_dict):
    err_code = 'B'
    err_dict = {}
    input_path = r'/Users/d_private/Documents/PyProgs/2021b/ex9/sources/weight_input.csv'
    true_data = true_dict["data"]
    true_cols = true_dict["column_names"]
    true_rows = true_dict["row_names"]

    try:
        stud_dict = student_module.load_training_data(input_path)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))
        err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

    else:
        try:
            stud_data = stud_dict["data"]
            res = TestResult.OK if areNumericArraysEqual(true_data, stud_data) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))

        try:
            stud_cols = stud_dict["column_names"]
            res = TestResult.OK if np.array_equal(true_cols, stud_cols) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 2, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))
        try:
            stud_rows = stud_dict["row_names"]
            res = TestResult.OK if np.array_equal(true_rows, stud_rows) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

    return err_dict




def test_q2BtoE(student_module, true_dict, checked_dict):
    err_dict = {}
    err_code = 'B'

    #B4
    try:
        stud_ans = student_module.get_highest_weight_loss_trainee(checked_dict)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))
    else:
        true_ans = sol.get_highest_weight_loss_trainee(true_dict)
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Wrong answer"))

    #B5
    try:
        stud_ans = student_module.get_diff_data(checked_dict)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 5, TestResult.ERROR, e))

    else:
       true_ans = sol.get_diff_data(true_dict)
       res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
       err_dict.update(proccessTestRes(err_code, 5, res, msg=f"Wrong answer"))

    #B6
    try:
        stud_ans = student_module.get_highest_loss_month(checked_dict)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 6, TestResult.ERROR, e))

    else:
       true_ans= sol.get_highest_loss_month(true_dict)
       res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
       err_dict.update(proccessTestRes(err_code, 6, res, msg=f"Wrong answer"))

    #B7
    try:
        stud_ans = student_module.get_relative_diff_table(checked_dict)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 7, TestResult.ERROR, e))

    else:
       true_ans = sol.get_relative_diff_table(true_dict)
       res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
       err_dict.update(proccessTestRes(err_code, 7, res, msg=f"Wrong answer"))
    return err_dict



def testQ3(student_module, err_code):
    err_dict = {}

    err_dict.update(test_q3a(student_module))
    err_dict.update(test_q3b(student_module))

    return err_dict


def test_q3a(student_module):
    err_dict = {}
    err_code = 'C'
    input_path = r'/Users/d_private/Documents/PyProgs/2021b/ex9/sources/cameraman.tif'

    try:
        stud_ans = student_module.compute_entropy(input_path)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))

    else:
        true_ans = sol.compute_entropy(input_path)
        if isinstance(stud_ans, float):
            res = TestResult.OK if areFloatEqual(true_ans, stud_ans) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Wrong answer"))
        else:
            res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Wrong answer"))

    return err_dict


def test_q3b(student_module):
    err_dict = {}
    err_code = 'C'
    input_path = r'/Users/d_private/Documents/PyProgs/2021b/ex9/sources/cameraman.tif'
    #
    # # C2
    # try:
    #     stud_ans = student_module.nearest_enlarge(input_path, 1)
    # except BaseException as e:
    #     err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))
    #
    # else:
    #     true_ans = sol.nearest_enlarge(input_path, 1)
    #     res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
    #     err_dict.update(proccessTestRes(err_code, 2, res, msg=f"Wrong answer"))

    # C3
    try:
        stud_ans = student_module.nearest_enlarge(input_path, 2)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

    else:
        true_ans = sol.nearest_enlarge(input_path, 2)
        res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Wrong answer"))

    # C4
    try:
        stud_ans = student_module.nearest_enlarge(input_path, 3)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))

    else:
        true_ans = sol.nearest_enlarge(input_path, 3)
        res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Wrong answer"))


    return err_dict

