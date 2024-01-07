'''
Python for Engineers 2021a Ex4
'''
import contextlib
import io
import signal

from TestResults import TestResult
import re
import editdistance
import math
import sys

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
    return f'Wrong or Inaccurate answer, expected output: {case_expected}, got: {stud_ans}.'

#
# def proccessTestRes(test_res, err_code, output):
#     global err_dict
#     if test_res == True:
#         return
#     elif test_res == False:
#         err_dict[err_code] = f"Totally wrong output: {output}"
#
#     elif test_res == 'J':
#         markException(f"Inaccurate printout: {output}", err_code + test_res)
#
#     elif test_res == 'L':
#         markException(f"Inaccurate calulation of a number: {output}", err_code + test_res)
#
#     return 0

def proccessTestRes(err_code: str, case_num: int, res: TestResult, msg: str = None
                    ,case_expected: str = None, stud_ans: str = None):

    if res == TestResult.INCORRECT or res == TestResult.INACCURATE:   # If res was anything but ok mark an error and return it
        if msg == None:
            return {f'{err_code}{case_num}{res.value}': {wrongAnsMsgGenerator(case_expected, stud_ans)}}
        else:
            return {f'{err_code}{case_num}{res.value}': {msg}}

    if res == TestResult.ERROR or res == TestResult.ENDLESS_LOOP:
        return {f'{err_code}{case_num}{res.value}': {msg}}

    return {}


############## EX1 Specific Testers ##############

def general_ex1_tester(expected, student_output):
    numRes, textRes, editDistance = compareNumsTexts(expected, student_output)

    # In the case of a mistake only in the calculations or a small (up to extra space and 2 spelling mistakes)
    # we return INACCURATE instead of INCORRECT
    # if (not numRes and textRes) or (numRes and not textRes and editDistance < 3):
    #     return TestResult.INACCURATE

    '''
    If the calculation was wrong (up to 5 digits after decimal point, determined in compareNumsTexts) or the text is 
    inaccurate by more than two spelling mistakes return INCORRECT.
     * Not counting extra spaces in the end
     * Ignoring cap/small letters
    '''
    if (numRes == False) or (textRes == False and editDistance > 4):
        return TestResult.INCORRECT

    return TestResult.OK

def compareNumsTexts(expected, student_output):
    '''
    Extracts numbers and text from the output and expected result and checks each of them separately.
    Returns a tuple with 3 v גוalues:
    1. Result of comparing the numbers (Boolean)
    2. Boolean indicating whether the match is exact
    3. Edit distance (int) between the *lowered* versions of the expected and output string

    (If it'S only a case mismatch, the second value will be False even though the edit distance is 0)
    '''
    p = R'\d+(?:\.\d+)?'  # Number pattern
    studNums, expNums = re.findall(p, student_output), re.findall(p, expected)

    numsResults = False
    if len(studNums) == len(expNums):
        for studNum, expNum in zip(studNums, expNums):
            # Compare up to 5 decimals (can be used to avoid punishing those who rounded)
            # Accept answer difference of up to 1e-05
            res = math.fabs(round(float(studNum) - float(expNum), 5))
            if res > 1e-05:
                break
        else:
            numsResults = True

    studText, expText = re.sub(p, '', student_output), re.sub(p, '', expected)
    editDistance = int(editdistance.eval(studText.lower(), expText.lower()))
    return (numsResults, studText == expText, editDistance)

@contextlib.contextmanager
def stdoutRedirect(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def exec_student_code(student_code, test_env):
    signal.signal(signal.SIGALRM, handler)
    with stdoutRedirect() as exec_output:
        # Execute the student code block and catch it's outputs
        # try:
        # Timer
        # signal.alarm(3)
        exec(student_code, test_env)
        # signal.alarm(0)

        # except Exception as t:
        #     msg = f"**{type(t).__name__}**! Failed to exec student code with test env: {test_env}"
        #     if (type(t) == TimeoutError):
        #         raise TimeoutError(msg)
        #
        #     else:
        #         return (TestResult.ERROR, f"Failed to exec student code with test env: {test_env}")

        exec_output = exec_output.getvalue()[:-1]

    return exec_output

def ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code) -> dict:
    err_dict = {}

    for case_num, (case_vars_vals, case_expected) in enumerate(zip(cases, expected_outputs), 1):
        # Initiate result and msg
        res, msg = TestResult.OK, "Passed"

        # Zip into a dictionary the variables for this code and their values for the current test
        test_env = dict(zip(var_names, case_vars_vals))

        # Execute student code with my variable values
        try:
            student_output = exec_student_code(student_code, test_env)
            # Remove End Of Lines
            student_output = re.compile('( )?\n(\r)?').sub('', student_output)
            student_output = student_output.rstrip()
            res = general_ex1_tester(case_expected, student_output)

            if not (res == TestResult.OK):
                msg = wrongAnsMsgGenerator(case_expected, student_output)

        except Exception as e:
            msg = f"Student_func raised: {e} on input {case_vars_vals}"
            res = TestResult.ERROR


        err_dict.update(proccessTestRes(err_code, case_num, res, msg))

    return err_dict

def testQ1(student_code, err_code):
    err_dict = {}
    var_names = ['lst', 'a']
    # We assign to each var based on the case

    cases = [[[1, 2, 3, 4, 5], 3],
             [[1, 2, 3, 4, 5], 8],
             [[2, 4, 8, 16], 16],
             [[], 3],
             [[3], 3]]



    # Expected values list
    expected_outputs = ['2', '-1', '3', '-1', '0']
    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)


def testQ2(student_code, err_code):
    var_names = ['lst2']

    cases = [[["hello", 'world', "course", "python", "day"]],
             [["hello"]],
             [["hello", 'world']],
             [["hello", 'world', "course"]],
             [["aaaaaa", 'aaaaaa', "aaaaaa", "aaaaaa", "a"]]]

    expected_outputs = ['The number of strings longer than the average is: 2',
                        'The number of strings longer than the average is: 0',
                        'The number of strings longer than the average is: 0',
                        'The number of strings longer than the average is: 1',
                        'The number of strings longer than the average is: 4']

    err_dict = {}

    for case_num, (case_vars_vals, case_expected) in enumerate(zip(cases, expected_outputs), 1):
        # Initiate result and msg
        res, msg = TestResult.OK, "Passed"

        # Zip into a dictionary the variables for this code and their values for the current test
        test_env = dict(zip(var_names, case_vars_vals))

        # Execute student code with my variable values
        try:
            student_output = exec_student_code(student_code, test_env)
            '''
            Specifically in EX2q2 the student prints the output twice. This might cause double errors so we split
            the output to avoid and check only the first print. Later in the function we make sure the student indeed 
            used a while loop
            '''
            student_output = student_output.split('\n')[0]
            student_output = student_output.rstrip()
            res = general_ex1_tester(case_expected, student_output)

            # if not (res == TestResult.OK):
            #     res, msg = TestResult.INCORRECT, wrongAnsMsgGenerator(case_expected, student_output)

        except Exception as e:
            msg = f"**{type(e).__name__}**! Failed to exec student code on input {case_vars_vals}"
            if (type(e) == TimeoutError):
                res = TestResult.ENDLESS_LOOP

            else:
                res = TestResult.ERROR


        err_dict.update(proccessTestRes(err_code, case_num, res, msg))

    ptrn = re.compile('^while\s*\(*.*\)*\s*:\s*$', re.MULTILINE)
    if len(re.findall(ptrn, student_code)) < 1:
        err_dict[f'{err_code}{len(cases)+1}{TestResult.INCORRECT.value}'] = f'Did not find use of while loop in student code'

    return err_dict

def testQ3(student_code, err_code):
    var_names = ['lst3']

    cases = [[[0, 1, 2, 3, 4]],
             [[]],
             [[2]],
             [[9, 6, 0, 3]],
             [[3, 3, 3, 3]]]

    expected_outputs = ['20', '0', '2', '54', '27']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

def testQ4(student_code, err_code):

    var_names = ['lst4']

    cases = [[[1, 2, 4, 5, 5, 8]],
             [[1, 2, 4, 8]],
             [[1, 3, 0]],
             [[2, 1]],
             [[9, 8, 6, 3, 2]]]

    expected_outputs = ['[1, 2, 4, 8]',
                        '[1, 2, 4, 8]',
                        '[1, 3, 0]',
                        '[2, 1]',
                        '[9, 8, 6, 3]']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

def testQ5(student_code, err_code):

    var_names = ['my_string', 'k']

    cases = [["abaadddefggg",1],
             ["ab4t3bbb34bbb345bbbb35bbbbbmmmmmm",6],
             ["abcccccd", 2],
             ["abcCcCcd", 2],
             ["abaadddefggg", 9],
             ["", 2]]

    expected_outputs = ['For length 1, found the substring a!',
                        'For length 6, found the substring mmmmmm!',
                        'For length 2, found the substring cc!',
                        "Didn't find a substring of length 2",
                        "Didn't find a substring of length 9",
                        "Didn't find a substring of length 2"]

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

