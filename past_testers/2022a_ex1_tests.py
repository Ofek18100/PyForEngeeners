'''
Python for Engineers 2021a Ex4
'''
import contextlib
import io
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
        return {f'{err_code}{case_num}{res.value}': {wrongAnsMsgGenerator(case_expected, stud_ans)}}

    if res == TestResult.ERROR or res == TestResult.ENDLESS_LOOP:
        return {f'{err_code}{case_num}{res.value}': {msg}}

    return {}


############## EX1 Specific Testers ##############

def general_ex1_tester(expected, student_output, editDistanceThr=2):
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
    if (numRes == False) or (textRes == False and editDistance > editDistanceThr):
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

    with stdoutRedirect() as exec_output:
        # Execute the student code block and catch it's outputs
        try:
            # signal.alarm(3)
            exec(student_code, test_env)
            # signal.alarm(0)

        except Exception as e:
            return (TestResult.ERROR, f"Failed to exec student code with test env: {test_env}")

        # except TimeoutError as inf:
        #     markException(inf, f'{_testItem.get_err_code()}Inf')
        #     continue

        # Extract output
        exec_output = exec_output.getvalue()[:-1]


        #
        # if QHandler.get_qnum() == 1:
        #     # No need to check the line Diameter is :
        #     exec_output = re.compile('((D)?(d)?i(a)?meter|(C)?(c)?ircumf(e)?rence) is( )*(:)?( )*(\d)*(\.)?(\d)*').sub(
        #         '', exec_output)
        #     # No need to check new line between lines
        #     exec_output = re.compile('( )?\n(\r)?').sub('', exec_output)
        # if QHandler.get_qnum() == 2:
        #     exec_output = exec_output.rstrip()

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

            if err_code=='D':
                res = general_ex1_tester(case_expected, student_output, editDistanceThr=1)
            else: res = general_ex1_tester(case_expected, student_output)

            # if not (res == TestResult.OK):
            #     res, msg = TestResult.INCORRECT, wrongAnsMsgGenerator(case_expected, student_output)

        except Exception as e:
            msg = f"Student_func raised: {e} on input {case_vars_vals}"
            res = TestResult.ERROR


        err_dict.update(proccessTestRes(err_code, case_num, res, msg))

    return err_dict

def testQ1(student_code, err_code):
    err_dict = {}

    var_names = ['S','AB','BC','AD','DC']
    # We assign to each var based on the case
    cases = [[1, 1, 1, 1, 1],
             [42, 10, 5, 5, 18],
             [4.5, 1, 1.12345, 2, 3]]

    # Expected values list
    expected_outputs = ['Perimeter is: 4Midsegment is: 1.0Height is: 1.0',
                'Perimeter is: 38Midsegment is: 14Height is: 3',
                'Perimeter is: 7.12345Midsegment is: 2.0Height is: 2.25']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)


def testQ2(student_code, err_code):
    var_names = ['my_name']

    cases = [['alice'],
             ['AliCe'],
             ['BOB']]

    expected_outputs = ['Hello Alice!',
                        'Hello AliCe!',
                        'Hello BOB!']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

def testQ3(student_code, err_code):
    var_names = ['number']

    cases = [['7'],
             ['0'],
             ['-1'],
             ['82']]

    expected_outputs = ['I am 7 and I am divisible by 7',
                        'I am 0 and I am divisible by 7',
                        'I am -1 and I am not divisible by 7',
                        'I am 82 and I am not divisible by 7']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

def testQ4(student_code, err_code):

    var_names = ['text', 'copies']

    cases = [['tom', 3], ['ttt', 10], ['dodo', 1]]

    expected_outputs = ['tmotmotmo',
                        'tttttttttttttttttttttttttttttt',
                        'ddoo']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

def testQ5(student_code, err_code):

    var_names = ['name', 'q']

    cases = [['Python for engineers', -1],
             ['Python for engineers', 200],
             ['', 1],
             ['droLtromedloV', 0],
             ['droLtromedloV', 4]]

    expected_outputs = ['Error: illegal input!',
                        'Error: illegal input!',
                        'Error: illegal input!',
                        ' VoldemortLord',
                        'Lord Voldemort']

    return ex1ex2_simpleTester(student_code, var_names, cases, expected_outputs, err_code)

