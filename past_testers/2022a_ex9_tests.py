'''
Python for Engineers 2022a Ex9
'''
import os

import past_solutions_temp.ex9_solution_2022a
from TestResults import TestResult
import re
import inspect
import past_solutions_temp.ex9_solution_2022a as sol
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
        err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Wrong answer"))


    # A2
    input = -4
    true_obj2 = sol.Roman(input)
    try:
        stud_obj2 = student_module.Roman(input)

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))

    else:
        res = TestResult.OK if areObjEqual(true_obj2, stud_obj2, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 2, res, msg=f"Wrong answer"))

    # A3
    try:
        input = 'XV'
        true_obj3 = sol.Roman(input)
        stud_obj3 = student_module.Roman(input)
        true_ans = true_obj3.__repr__()
        stud_ans = stud_obj3.__repr__()
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Wrong answer"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

    # A4
    try:
        input = 8
        true_ans = sol.Roman(8).__repr__()
        stud_ans = student_module.Roman(8).__repr__()
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Wrong answer"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))

    # A5
    try:
        input = -4
        true_obj5 = sol.Roman(input)
        stud_obj5 = student_module.Roman(input)
        true_ans = true_obj5 + (-11) + sol.Roman(2)
        stud_ans = stud_obj5 + (-11) + student_module.Roman(2)
        res = TestResult.OK if areRomanPartiallyEqual(true_ans, stud_ans, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 5, res, msg=f"Wrong answer"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 5, TestResult.ERROR, e))

    # A6
    try:
        input1 = -3
        input2 = -2
        input3 = 5
        true_ans = sol.Roman(input1) < sol.Roman(input2) and sol.Roman(input3) > 3
        stud_ans = student_module.Roman(input1) < student_module.Roman(input2) and student_module.Roman(input3) > 3
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 6, res, msg=f"Wrong answer"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 6, TestResult.ERROR, e))

    # A7
    try:
        input1 = 13
        input2 = "-V"
        true_ans = sol.Roman(input1) // sol.Roman(input2)
        stud_ans = student_module.Roman(input1) // student_module.Roman(input2)
        res = TestResult.OK if areRomanPartiallyEqual(true_ans, stud_ans, student_module) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 7, res, msg=f"Wrong answer"))

    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 7, TestResult.ERROR, e))

    # A8
    try:
        input1 = -13
        input2 = "-XV"
        student_module.Roman(input1) // student_module.Roman(input2)
    except BaseException as e:
        if not isinstance(e, ValueError):
            msg = 'Wrong exception type: ' + type(e).__name__ + ':  ' + str(e)
            err_dict.update(proccessTestRes(err_code, 8, res, msg))

    else:
        err_dict.update(proccessTestRes(err_code, 8, res, msg=f"Wrong answer"))

    return err_dict

def testQ2(student_module, err_code):
    err_dict = {}

    input_path = r'/Users/amitc/Projects/PythonTesting/2022a/ex9/sources/'
    weights_path = os.path.join(input_path, "weights.csv")
    heights_path = os.path.join(input_path, "heights.csv")
    weights_dict, heights_dict = sol.load_training_data(weights_path, heights_path)
    err_dict.update(test_q2a(student_module, weights_dict, heights_dict))

    if ('B2' in err_dict and 'B3' in err_dict) or ('B2X' in err_dict and 'B3X' in err_dict):
        try:
            checked_weights_dict, checked_heights_dict = student_module.load_training_data(weights_path, heights_path)
        except:
            checked_weights_dict, checked_heights_dict = weights_dict.copy(), heights_dict.copy()
    else:
        checked_weights_dict, checked_heights_dict = weights_dict.copy(), heights_dict.copy()

    err_dict.update(test_q2BtoE(student_module,weights_dict, heights_dict, checked_weights_dict, checked_heights_dict))

    return err_dict


def test_q2a(student_module, weights_dict, heights_dict):
    err_code = 'B'
    err_dict = {}
    input_path = r'/Users/amitc/Projects/PythonTesting/2022a/ex9/sources/'
    weights_path = os.path.join(input_path, "weights.csv")
    heights_path = os.path.join(input_path, "heights.csv")
    true_weights_data = weights_dict["data"]
    true_weights_cols = weights_dict["column_names"]
    true_weights_rows = weights_dict["row_names"]
    true_heights_dict = heights_dict

    try:
        stud_weights_dict, stud_heights_dict = student_module.load_training_data(weights_path, heights_path)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))
        err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))
        err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))

    else:
        try:
            stud_weights_data = stud_weights_dict["data"]
            res = TestResult.OK if areNumericArraysEqual(true_weights_data, stud_weights_data) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))

        try:
            stud_weights_cols = stud_weights_dict["column_names"]
            res = TestResult.OK if np.array_equiv(true_weights_cols, stud_weights_cols) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 2, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))
        try:
            stud_weights_rows = stud_weights_dict["row_names"]
            res = TestResult.OK if np.array_equiv(true_weights_rows, stud_weights_rows) else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

        try:
            res = TestResult.OK if true_heights_dict == stud_heights_dict else TestResult.INCORRECT
            err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Wrong answer"))
        except BaseException as e:
            err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))

    return err_dict




def test_q2BtoE(student_module, true_weights_dict, true_heights_dict, checked_weights_dict, checked_heights_dict):
    err_dict = {}
    err_code = 'B'

    #B5
    try:
        stud_ans = student_module.get_highest_weight_loss(checked_weights_dict)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 5, TestResult.ERROR, e))
    else:
        true_ans = sol.get_highest_weight_loss(true_weights_dict)
        res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 5, res, msg=f"Wrong answer"))

    #B6
    try:
        stud_ans = student_module.get_highest_bmi_loss_month(checked_weights_dict, checked_heights_dict)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 6, TestResult.ERROR, e))

    else:
       true_ans= sol.get_highest_bmi_loss_month(true_weights_dict, true_heights_dict)
       res = TestResult.OK if simpleObjComparision(true_ans, stud_ans) else TestResult.INCORRECT
       err_dict.update(proccessTestRes(err_code, 6, res, msg=f"Wrong answer"))

    # #B7
    # try:
    #     stud_ans = student_module.get_bmi_diff(checked_weights_dict, checked_heights_dict)
    # except BaseException as e:
    #     err_dict.update(proccessTestRes(err_code, 7, TestResult.ERROR, e))
    #
    # else:
    #    true_ans = sol.get_bmi_diff(true_weights_dict, true_heights_dict)
    #    res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
    #    err_dict.update(proccessTestRes(err_code, 7, res, msg=f"Wrong answer"))

    return err_dict


def testQ3(student_module, err_code):
    err_dict = {}
    err_code = 'C'
    img_path = r'/Users/amitc/Projects/PythonTesting/2022a/ex9/sources/image.png'
    img_pixels = (np.random.rand(100, 100) * 255).astype(np.uint8)
    imageio.imwrite(img_path, img_pixels)

    # Test image loading
    try:
        stud_ans = student_module.load_image_as_matrix(img_path)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, e))

    else:
        true_ans = sol.load_image_as_matrix(img_path)
        res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 1, res, msg=f"Wrong answer"))

    # Test matrix binarization
    image_matrix = sol.load_image_as_matrix(img_path)
    binarized_image = sol.binarize_matrix(image_matrix)
    try:
        stud_ans = student_module.binarize_matrix(image_matrix)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, e))

    else:
        res = TestResult.OK if areNumericArraysEqual(binarized_image, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 2, res, msg=f"Wrong answer"))


    true_compressed_img, sol_shape = sol.compress_flatten_rle(binarized_image)

    # C3
    try:
        stud_compressed_img, stud_shape = student_module.compress_flatten_rle(binarized_image)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, e))

    else:
        res = TestResult.OK if stud_compressed_img.shape == true_compressed_img.shape and areNumericArraysEqual(stud_compressed_img, true_compressed_img) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 3, res, msg=f"Wrong answer"))

    # C4
    try:
        stud_ans = student_module.decompress_flatten_rle(true_compressed_img, sol_shape)
    except BaseException as e:
        err_dict.update(proccessTestRes(err_code, 4, TestResult.ERROR, e))

    else:
        true_ans = sol.decompress_flatten_rle(true_compressed_img, sol_shape)
        res = TestResult.OK if areNumericArraysEqual(true_ans, stud_ans) else TestResult.INCORRECT
        err_dict.update(proccessTestRes(err_code, 4, res, msg=f"Wrong answer"))

    return err_dict
