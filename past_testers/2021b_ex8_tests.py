'''
Python for Engineers 2021a Ex5
'''
from copy import deepcopy
import numpy as np
from TestResults import TestResult
import os


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


## added Q_num here so it will know which testSingleCase to call
def simpleTester(student_func, cases, expected_outputs, err_code, Q_num) -> dict:
    err_dict = {}

    for case_num, (case_args, case_expected) in enumerate(zip(cases, expected_outputs), 1):
        if (Q_num == 1):
            res, msg = testSingleCase(student_func, case_args, case_expected)
        if (Q_num == 2):
            res, msg = testSingleCaseForQ2(student_func, case_args, case_expected)
        if (Q_num == 3):
            res, msg = testSingleCaseForQ3(student_func, case_args, case_expected)
        if (Q_num == 4):
            res, msg = testSingleCaseForQ4(student_func, case_args, case_expected)

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


def merci_compare(str1, str2):
    str1 = "".join(str1.lower().split()).strip("'").strip("\n")
    str2 = "".join(str2.lower().split()).strip("'").strip("\n")

    return str1 == str2


############## EX8 Specific Testers ##############

def testQ1(student_module, err_code):
    err_dict = {}

    drinks1 = {'coke': 12, 'rum': 25}
    snacks1 = {'m&m': 10, 'cake': 30}

    # Create Instance
    mini = None
    try:
        mini = student_module.Minibar(drinks1, snacks1)
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, "", TestResult.IMPORT, "Could not initiate new Minibar"))
        return err_dict

    # eat a snack
    try:
        mini.eat_a_snack("cake")
        expected = "The minibar contains the drinks: ['coke', 'rum']\nAnd the snacks: ['m&m']\nThe bill for the " \
                   "minibar is: 30.0"
        compare = merci_compare(repr(mini), expected)
        if not compare:
            err_dict.update(proccessTestRes(err_code, 1, TestResult.INCORRECT, "Incorrect repr for minibar after "
                                                                               "eating cake"))
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, 1, TestResult.ERROR, "Could not eat a snack"))
    drinks1 = {'coke': 12, 'rum': 25}
    snacks1 = {'m&m': 10, 'cake': 30}
    mini = student_module.Minibar(drinks1, snacks1)
        # drink a drink
    try:
        mini.drink_a_drink("rum")
        expected = "The minibar contains the drinks: ['coke']\nAnd the snacks: ['m&m', 'cake']\nThe bill for the " \
                   "minibar is: 25.0"
        compare = merci_compare(repr(mini), expected)
        if not compare:
            err_dict.update(proccessTestRes(err_code, 2, TestResult.INCORRECT, "Incorrect repr for minibar after "
                                                                               "eating cake and drinking a rum"))
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, 2, TestResult.ERROR, "Could not drink a drink"))


        # try to drink water
    try:
        mini.drink_a_drink("water")
    except ValueError as ve:
        expected = "The drink is not in the minibar"
        compare = merci_compare(str(ve), expected)
        if not compare:
            err_dict.update(proccessTestRes(err_code, 3, TestResult.INCORRECT, "Incorrect Error message"))
    except Exception as e:
        err_dict.update(proccessTestRes(err_code, 3, TestResult.ERROR, "Incorrect Error Type"))


    return err_dict

    # cases = [r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q1_input1.txt"]
    # # Expected values list
    # expected = [366]
    #
    # return simpleTester(student_func, cases, expected, err_code, 1)


def testQ2(student_func, err_code):
    stud_op_file_PATH = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\tmp.txt"
    cases = [(r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_input1.txt", stud_op_file_PATH, "larry"),
             (r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_input2.txt", stud_op_file_PATH, "hello"),
             (r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_input3.txt", stud_op_file_PATH, "person"),
             (r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_input3.txt", stud_op_file_PATH, "larry"),
             (r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_aaaa.txt", stud_op_file_PATH, "a")]
    # Expected values list
    expected = [r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_output_empty.txt",
                r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_output2_hello.txt",
                r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_output3_person.txt",
                r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q2_output_empty.txt",
                None]

    return simpleTester(student_func, cases, expected, err_code, 2)


def testQ3(student_func, err_code):
    stud_op_file_PATH = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\tmp.txt"
    cases = [(-2, stud_op_file_PATH), (5, r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\ggg\Q3_30.txt"),
             (1, stud_op_file_PATH), (30, stud_op_file_PATH)]
    # Expected values list
    thirty_res_path = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q3_30.txt"
    one_res_path = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q3_1.txt"
    expected = ["num<=0", "bad_path", one_res_path, thirty_res_path]

    return simpleTester(student_func, cases, expected, err_code, 3)


def testQ4(student_func, err_code):
    empty_file = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q4_input1.txt"
    two_bands = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q4_input2.txt"
    reguler = r"C:\Users\Yuval\PycharmProjects\2021b_ex5\inputs\Q4_input3.txt"
    cases = [empty_file, two_bands, reguler]
    # Expected values list
    expected = ["valErr1", "valErr2", {'Radiohead': 4, 'ABBA': 2, 'The Beatles': 7}]

    return simpleTester(student_func, cases, expected, err_code, 4)
