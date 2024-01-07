'''
Python for Engineers 2019-2020 Sem A&B Ex9
'''
import re
import editdistance
from collections import namedtuple
from copy import deepcopy
import os
import signal
import inspect
from ex9_sol import *
import imageio


QuestionHandler = namedtuple('QuestionHandler', ['func_name', 'args', 'expected', 'testerFunc', 'err_code'])

INEXACT_PRINT_CODE = 'J'
INEXACT_EXP = 'L'
INCORRECT_OUTPUT_TYPE = 'T'
INFLOOP_MAXRECURISON = 'R'
UNKNOWN_EXCEP = 'X'
FORBIDDEN_EXPRESSIONS = 'Z'

EXCEPTION_MESSAGE_TOLERANCE = 25

err_dict = {}

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

def assertException(func, expType, message, errCode):
    '''
    Test Exception handling, and Exceptions messages and assign results to the relevant place in the error dict.

    :param func: Imported student function to be tested for error handling.
    :param expType: Type of exception that should be raised by student func.
    :param message: Correct message for comparision with student exception message.
    :param errCode: Error code for this specific test, this is used to add the results of the test to the dictionary.
    '''
    global err_dict
    try:
        func()

    except BaseException as e:
        #Check if exception is of the right type
        if not isinstance(e, expType):
            err_dict[errCode] = 'Wrong exception type: ' + type(e).__name__ + ':  ' + str(e)

        #If it's of the right type check if the exception message is correct.
        elif message:
            res = compareAnswer(str(e), message)
            if res is False:
                err_dict[errCode] = 'Wrong messag e: ' + str(e)
            elif res is not True:  # Must be an int then
                if res > EXCEPTION_MESSAGE_TOLERANCE:
                    err_dict[errCode] = 'Wrong message (outside tolerance):\n' + str(e)
                elif res > 3:
                    err_dict[errCode + 'J'] = 'Close message ' + str(res) + ':\n' + str(e)
                else:
                    return


    #Reeach here if no exception was thrown by the student's func
    else:
        err_dict[errCode] = 'No excepetion thrown' #

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
    signal.alarm(2)  # Make sure there are no infinite loops
    if type(args)== list or type(args) == tuple:
        stud_ans = student_func(*args)
    else:
        stud_ans = student_func(args)
    signal.alarm(0)  # Turn off the timer

    return stud_ans

def handleStudentError(e: Exception)-> str:
    if isinstance(e, TypeError):
        return INCORRECT_OUTPUT_TYPE

    elif isinstance(e, TimeoutError):
        return INFLOOP_MAXRECURISON

    else:
        return UNKNOWN_EXCEP


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

def markException(e, err_codes) -> int:
    '''
    receive exception 'e' and a list of one or more err_codes. insert err_codes to errors dictionary as keys
    and insert the exception representation as the values in the dictionary.
    the dictionary is global and it'S edited in-place
    :param e: exception that occurred outside of the function, it'S str representation will be the value of the dictionary.
    :param errCodes: a list of error codes, they will be the keys in the dictionary.
    :return:
    '''

    err_codes = err_codes.split()
    err_suffix = handleStudentError(e)

    if len(err_codes) == 1:
        err_dict[f'{err_codes[0]}{err_suffix}'] = e
        return 0

    # else - then there's more then one err_code
    for err_code in err_codes:
        err_dict[f'{err_code}{err_suffix}'] = 'Initialization for test bulk failed: ' + str(e)

    return 0

def test(err_code, func):
    '''
    Preform function 'func' handle errors by catching them and inserting them to the err_dict.
    :param errCode: error code relevant for the the specific current test.
    :param func: function to preform.
    :return: the result if an error didn't occur.
    '''
    # print errCode
    try:
        res = func()
    except BaseException as e:
        markException(e, err_code)
    else:
        if res != True:
            err_dict[err_code] = res

        return res

############## EX4 Specific Testers ##############

def test_q1a(student_module):
    global err_dict
    input_path = '/Users/d_private/PycharmProjects/PyProg1920Bex9/source/weight_input.csv'
    err_list = 'A1 A2 A3'
    true_data, true_cols, true_rows = load_training_data(input_path)

    try:
        stud_data, stud_cols, stud_rows = student_module.load_training_data(input_path)

    except BaseException as e:
        markException(e, err_list)


    else:
        test('A1', lambda: np.array_equal(true_data, stud_data))
        test('A2', lambda: np.array_equal(true_cols, stud_cols))
        test('A3', lambda: np.array_equal(true_rows, stud_rows))

    return err_dict

def test_q1BtoE(student_module, true_data, true_cols, true_rows):

    #A1b
    try:
        stud_ans = student_module.get_highest_weight_loss_trainee(true_data, true_cols, true_rows)
    except BaseException as e:
        markException(e, 'A4')
    else:
        ans = get_highest_weight_loss_trainee(true_data, true_cols, true_rows)
        test('A4', lambda: simpleObjComparision(ans, stud_ans))

    #A1c
    try:
        stud_ans = student_module.get_diff_data(true_data, true_cols, true_rows)
    except BaseException as e:
        markException(e, 'A5')

    else:
        ans = get_diff_data(true_data, true_cols, true_rows)
        test('A5', lambda: np.array_equal(ans, stud_ans))

    #A1d
    try:
        stud_ans = student_module.get_highest_loss_month(true_data, true_cols, true_rows)
    except BaseException as e:
        markException(e, 'A6')

    else:
        ans = get_highest_loss_month(true_data, true_cols, true_rows)
        test('A6', lambda: simpleObjComparision(ans, stud_ans))

    #Q1e
    try:
        stud_ans = student_module.get_relative_diff_table(true_data, true_cols, true_rows)
    except BaseException as e:
        markException(e, 'A7')

    else:
        ans = get_relative_diff_table(true_data, true_cols, true_rows)
        test('A7', lambda: np.array_equal(ans, stud_ans))

    return err_dict



def test_q1(student_module):
    global err_dict
    err_dict = {}
    input_path = '/Users/d_private/PycharmProjects/PyProg1920Bex9/source/weight_input.csv'

    true_data, true_cols, true_rows = load_training_data(input_path)

    err_dict.update(test_q1a(student_module))
    err_dict.update(test_q1BtoE(student_module, true_data, true_cols, true_rows))

    return err_dict



def test_q2(student_module):
    global err_dict

    input_path = '/Users/d_private/PycharmProjects/PyProg1920Bex9/source/missions_test.csv'
    failure_flag = False
    #General test pattern, try to activate the function, if it doesn't work -> exception
    #If it works

    err_list = 'B1 B2 B3 B4 B5'

    try:
        student_func = student_module.read_missions_file
    except BaseException as e:
        markException(e, err_list)

    else:
        true_df = read_missions_file(input_path)

    # Test Q2.a - read_missions_file(file_name)
    '''
    Test IO Error in case of a bad file name
    Test that a panda DataFrame is indeed returned
    Check number of columns in 3, Bounty, Expenses, Duration
    The index should be the kingdoms names
    '''
    #check that the student function doesnt fail totally
    try:
        stud_df = student_func(input_path)
    except BaseException as e:
        markException(e, 'B1 B2 B3')
        failure_flag = True


    #We only enter here if the function did not fail completly, then we can preform the tests on the return value
    else:
        test('B1', lambda: type(stud_df) == type(true_df))
        assertException(lambda: student_module.read_missions_file("empty"), IOError, 'An IO error occurred', 'B3')
        test('B2', lambda: stud_df.equals(true_df))

    #Test Q2.b
    '''
    input is a pandas dataframe
    no loops
    calculate the missions value stuff
    '''

    true_ans = true_df.Bounty.sum() - true_df.Expenses.sum()
    try:
        if(failure_flag == False): #Q1A returned a dataframe so we continue to use it
            stud_ans = student_module.sum_rewards(stud_df)
        else:
            # Use the true df to test the student answer to avoid following mistake
            stud_ans = student_module.sum_rewards(true_df)
    except BaseException as e:
        markException(e, 'B4')

    try:
        test('B4', lambda: stud_ans == true_ans)

    except BaseException as e:
        markException(e, 'B4')

    #Test Q2.c
    '''
    input is a pandas dataframe from Q1a output
    find_best_kingdom(bounties)
    '''
    eff = true_df.apply(lambda row: (row.Bounty - row.Expenses) / row.Duration, axis=1)
    mask = eff.values == eff.max()
    true_ans = eff.where(mask).dropna().index[0]

    try:
        if (failure_flag == False):  # Q1A returned a dataframe so we continue to use it
            stud_ans = student_module.find_best_kingdom(stud_df)
        else:
            # Use the true df to test the student answer to avoid following mistake
            stud_ans = student_module.find_best_kingdom(true_df)

    except BaseException as e:
        markException(e, 'B5')

    try:
        test('B5', lambda: stud_ans == true_ans)
    except BaseException as e:
        markException(e, 'B5')


    return err_dict


def test_q3(student_module):
    global err_dict

    err_dict.update(test_q3a(student_module))
    err_dict.update(test_q3b(student_module))

    return err_dict

def test_q3a(student_module):
    global err_dict
    input_path = '/Users/d_private/PycharmProjects/PyProg1920Bex9/source/cameraman.tif'

    try:
        stud_func = student_module.compute_entropy
    except BaseException as e:
        markException(e, 'C1')
        failure_flag = True

    try:
        ans = compute_entropy(input_path)
        stud_ans = stud_func(input_path)

    except BaseException as e:
        markException(e, 'C1')

    else:
        test('C1', lambda: simpleObjComparision(stud_ans, ans))

    return err_dict


def test_q3b(student_module):
    global err_dict
    input_path = '/Users/d_private/PycharmProjects/PyProg1920Bex9/source/cameraman.tif'
    # input_path = '/Users/d_private/PycharmProjects/PyProg1920Bex9/doncic.jpeg'
    try:
        stud_func = student_module.nearest_enlarge
    except BaseException as e:
        markException(e, 'C2 C3')
        failure_flag = True

    try:
        ans = nearest_enlarge(input_path, 2)
        stud_ans = stud_func(input_path, 2)

    except BaseException as e:
        markException(e, 'C2')

    else:
        test('C2', lambda: np.array_equal(stud_ans, ans))

    try:
        ans = nearest_enlarge(input_path, 3)
        stud_ans = stud_func(input_path, 3)

    except BaseException as e:
        markException(e, 'C3')

    else:
        test('C3', lambda: np.array_equal(stud_ans, ans))

    return err_dict







############## EX4 Specific variables ##############


NUM_OF_QUESTIONS = 5
# Q1a_handler = QuestionHandler('',
#                              # args
#                              None,
#                              # exp
#                              None,
#                  simpleTester, 'A')


# QHandler_lst = [Q1a_handler, Q1b_handler, Q2_handler, Q3_handler, Q4a_handler, Q4b_handler]
QHandler_lst = [test_q1, test_q2, test_q3]

