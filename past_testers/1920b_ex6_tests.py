'''
Python for Engineers 2019-2020 Sem A&B Ex6
'''
import re
import editdistance
from collections import namedtuple
from copy import deepcopy
import os
import signal
import inspect

QuestionHandler = namedtuple('QuestionHandler', ['func_name', 'args', 'expected', 'testerFunc', 'err_code'])

INEXACT_PRINT_CODE = 'J'
INEXACT_EXP = 'L'
INCORRECT_OUTPUT_TYPE = 'T'
INFLOOP_MAXRECURISON = 'R'
UNKNOWN_EXP = 'X'
FORBIDDEN_EXPRESSIONS = 'Z'

class TypeDiffError(TypeError):
    pass


def handler(signum, frame):
    '''
    Register an handler for the timeout
    :param signum: SIGNAL number to handle
    :param frame:
    :return: None
    '''

    print("Infinite loop encountered!")
    raise TimeoutError("Infinite loop encountered!")

signal.signal(signal.SIGALRM, handler)

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

# def assertException(func, expType, message, errCode):
#     '''
#     Test Exception handling, and Exceptions messages and assign results to the relevant place in the error dict.
#
#     :param func: Imported student function to be tested for error handling.
#     :param expType: Type of exception that should be raised by student func.
#     :param message: Correct message for comparision with student exception message.
#     :param errCode: Error code for this specific test, this is used to add the results of the test to the dictionary.
#     '''
#     try:
#         func()
#
#     except BaseException as e:
#         #Check if exception is of the right type
#         if not isinstance(e, expType):
#             errors[errCode] = 'Wrong exception type: ' + type(e).__name__ + ':  ' + str(e)
#
#         #If it's of the right type check if the exception message is correct.
#         elif message:
#             res = compareAnswer(str(e), message)
#             if res is False:
#                 errors[errCode] = 'Wrong message: ' + str(e)
#             elif res is not True: # Must be an int then
#                 if res > EXCEPTION_MESSAGE_TOLERANCE:
#                     errors[errCode] = 'Wrong message (outside tolerance):\n' + str(e)
#                 else:
#                     errors[errCode+'J'] = 'Close message ' + str(res) + ':\n' + str(e)
#
#     #Reeach here if no exception was thrown by the student's func
#     else:
#         errors[errCode] = 'No excepetion thrown' #

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

def simpleTester_old(student_func, case_args, case_expected):

    case_args = deepcopy(case_args)

    if not (type(case_args) == list or type(case_args) == tuple):
        stud_ans = student_func(case_args)

    elif len(case_args) == 1:
        stud_ans = student_func(case_args[0])
    else:
        stud_ans = student_func(case_args[0], case_args[1])

    CheckOutputType(stud_ans, [type(case_expected)])

    res = simpleObjComparision(case_expected, stud_ans)

    # print(stud_ans, case_expected)
    return \
        (True, stud_ans) if res \
        else \
            (False, wrongAnsMsgGenerator(case_expected, stud_ans))

def simpleObjComparision(expected, studentOut):
    # The output is a simple integer in this question, nothing fancy
    return studentOut == expected


def simpleRunStudFunc(student_func, args):
    # Try running the student's function the case's args
    signal.alarm(3)  # Make sure there are no infinite loops
    stud_ans = student_func(*args)
    signal.alarm(0)  # Turn off the timer

    return stud_ans

def handleStudentError(e: Exception, case_err_code, stud_ans, case_args, case_exp)-> tuple:
    if isinstance(e, TypeDiffError):
        return (case_err_code+INCORRECT_OUTPUT_TYPE, f"Output type is {type(stud_ans)} instead of {type(case_exp)}")

    elif isinstance(e, TimeoutError):
        return (case_err_code + INFLOOP_MAXRECURISON, f"Infinite loop encountered or max recursion depth reached!" \
                                                             f"input: {str(*case_args)}.")
    else:
        return (case_err_code + UNKNOWN_EXP, f"Function raised an exception, input: {str(*case_args)}.")


def simpleTester(student_func, _QHandler):
    err_dict = {}
    args = deepcopy(_QHandler.args)
    exps = deepcopy(_QHandler.expected)
    err_code = _QHandler.err_code
    stud_ans = ''

    for num, (case_args, case_exp) in enumerate(zip(args, exps), 1):
        case_err_code = err_code+str(num)
        try:
            stud_ans = simpleRunStudFunc(student_func, case_args)
            CheckOutputType(stud_ans, [type(case_exp)])

        except Exception as e:
            case_err_code, msg = handleStudentError(e, case_err_code, stud_ans, case_args, case_exp)
            print(f'{case_err_code}: {msg}')
            err_dict[case_err_code] = msg
            continue

        res = simpleObjComparision(stud_ans, case_exp)

        if res == False:
            msg = wrongAnsMsgGenerator(case_exp, stud_ans)
            err_dict[case_err_code] = msg

    return err_dict

def search_student_code_for_text(patterns, student_source) -> bool:
    '''
    Search the student'S source code and return True if it has 'pattern' in it.
    This could be used to look for imports of certain packages or for use of certain functions.
    :param pattern: to search for.
    :param student_source: Student module to search in.
    :return: True if 'text' exists in the source of 'student_module'
    '''
    for ptrn in patterns:
        if len(re.findall(ptrn, student_source)) > 0:
            return True

    return False

############## EX4 Specific Testers ##############


def general_tester_EX6(student_func, _QHandler):
    err_dict = {}
    err_code = _QHandler.err_code
    forbidden_expressions = ['for ', 'while ']

    if err_code == 'A': # errcode is a proxy to the question number and therefore the case
        forbidden_expressions.append('str\.')
    elif err_code == 'B':
        forbidden_expressions += [' max\(', '\(max\(']
    elif err_code == 'C':
        forbidden_expressions.append('str\.')

    student_source = inspect.getsource(student_func)

    if search_student_code_for_text(forbidden_expressions, student_source):
        err_dict[err_code+'1'+FORBIDDEN_EXPRESSIONS] = 'True'
        err_dict[err_code+'2'+FORBIDDEN_EXPRESSIONS] = 'True'
        return err_dict

    # If stucent didn't use forbidden expressions in his code, test the code
    err_dict.update(simpleTester(student_func, _QHandler))

    return err_dict


############## EX4 Specific variables ##############


NUM_OF_QUESTIONS = 5

Q1_handler = QuestionHandler('reverse_string',
                             # args
                             [['abs'], ['a'], ['dg4#tgg!'], ['RevRERSE'], ['bob'], ['']],
                             # exp
                             ['sba', 'a', '!ggt#4gd', 'ESRERveR', 'bob', ''],
                 general_tester_EX6, 'A')

Q2_handler = QuestionHandler('find_maximum',
                             # args
                             [[[1, 2, 3, 4]], [[]], [[0]], [[100, 10, 100]], [[100, 100]], [[5, 7.5]]],
                             # exp
                             [4, -1, 0, 100, 100, 7.5],
                 general_tester_EX6, 'B')
Q3_handler = QuestionHandler('is_palindrome',
                             # argsRevRERSE
                             [['bob'], ['boB'], ['bob '], ['Rat Snake'], ['Rat SnakeekanS taR'], ['DooD']],
                             # exp
                             [True, False, False, False, True, True],
                 general_tester_EX6, 'C')

Q4_handler = QuestionHandler('climb_combinations',
                             # args
                             [[3], [17], [15], [1], [2]],
                             # exp
                             [3, 2584, 987, 1, 2],
                 general_tester_EX6, 'D')


Q5_handler = QuestionHandler('is_valid_paren',
                             # args
                                 [['p(()r((0)))'], ['(.(a)'], ['()'], [')('], ['))(()()((())'], ['']],
                             # exp
                             [True, False, True, False, False, True],
                 general_tester_EX6, 'E')


QHandler_lst = [Q1_handler, Q2_handler, Q3_handler, Q4_handler, Q5_handler]
