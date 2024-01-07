'''
Python for Engineers 2022a Ex5
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


def assertException(func, expType, message, err_code, case_num, err_dict):
    '''
    Test Exception handling, and Exceptions messages and assign results to the relevant place in the error dict.

    :param func: Imported student function to be tested for error handling.
    :param expType: Type of exception that should be raised by student func.
    :param message: Correct message for comparision with student exception message.
    :param errCode: Error code for this specific test, this is used to add the results of the test to the dictionary.
    '''
    try:
        func()
        err_dict.update(proccessTestRes(err_code, case_num, TestResult.INCORRECT, "Did not catch the Exception"))

    except BaseException as e:
        # Check if exception is of the right type
        if not isinstance(e, expType):
            err_dict.update(proccessTestRes(err_code, case_num, TestResult.ERROR, "Incorrect Error Type"))

        # If it's of the right type check if the exception message is correct.
        elif message:
            res = str(e) == message
            if res is False:
                err_dict.update(proccessTestRes(err_code, case_num, TestResult.INCORRECT, "Incorrect Error message"))


def merci_compare(str1, str2):
    str1 = "".join(str1.lower().split()).strip("'").strip("\n")
    str2 = "".join(str2.lower().split()).strip("'").strip("\n")

    return str1 == str2


############## EX5 Specific Testers ##############
def testQ1(student_func, err_code):
    cases = [r"C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q1_1.txt", r"C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q1_2.txt"]
    expected = [366, 195]
    return simpleTester(student_func, cases, expected, err_code, 1)


def testQ2(student_func, err_code):
    cases = [(r'C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q2_{}_doc.txt'.format(i+1),
              r'C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q2_{}_identifiers.txt'.format(i+1)) for i in range(7)]

    Q2_1_exp = {'Hello_word9': 0, 'CoolRick11': 1, 'C-137': 2, 'c-132': 1, 'Z0Zo0': 1, 'TestMeRick123': 1}
    Q2_2_exp = {'Larry12': 1, "david94": 1, "i23schwimmer58": 0, "ric34ko71": 0, "brooklyn99": 2}
    Q2_3_exp = {'Larry12': 1, "12david94": 1, "i23schwimmer58": 1, "ric34ko71": 0, "8brooklyn99": 1}
    Q2_4_exp = {'Larry12': 0, "david94": 0, "i23schwimmer58": 0, "ric34ko71": 0, "brooklyn99": 0}
    Q2_5_exp = {'Larry12': 0, "david94": 0, "33": 5}
    Q2_6_exp = {'Hello_word9': 0, 'CoolRick11': 0, 'C-137': 1, 'c-132': 1, 'Z0Zo0': 0, 'TestMeRick123': 1}

    expected = [Q2_1_exp, Q2_2_exp, Q2_3_exp, Q2_4_exp, Q2_5_exp, Q2_6_exp]
    return simpleTester(student_func, cases, expected, err_code, 2)


def testQ3(student_func, err_code):
    # cases 1 and 2
    Q3_err_dict = {}
    Q3_1 = r'C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q3_1.txt'
    Q3_2 = r'C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q3_2.txt'
    Q3_1_exp = {'evil': 21000.0, 'good': 579.0, 'neutral': 34733.5, 'nihilist': 40988.5, 'cool': 2755.5}
    Q3_2_exp = {'cool': 2755.5, 'evil': 0.0, 'good': 505.0, 'neutral': 34733.5, 'nihilist': 40988.5}

    cases = [Q3_1, Q3_2]
    expected = [Q3_1_exp, Q3_2_exp]
    Q3_err_dict.update(simpleTester(student_func, cases, expected, err_code, 3))

    # cases 3-8
    errors = {'dup': 'Encountered duplicated Ricks',
              'digit': 'At least one of the rickounts is invalid',
              'type': 'At least one of the rick types is invalid',
              'invalid': 'Encountered invalid Rick identifier'}
    exp_msg = [errors['type'], errors['digit'], errors['digit'], errors['invalid'], errors['dup'], errors['type']]

    for i in range(6):
        assertException(lambda: student_func(r'C:\Users\Yuval\PycharmProjects\2022a_ex5\inputs\Q3_{}.txt'.format(i + 3)),
                        ValueError, exp_msg[i], err_code, i + 3, Q3_err_dict)
    return Q3_err_dict
