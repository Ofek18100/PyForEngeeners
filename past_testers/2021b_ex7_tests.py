'''
Python for Engineers 2021b Ex7
'''
import signal

from TestResults import TestResult
import re
import inspect


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
        print((case_args, case_expected))
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
        return {f'{err_code}{case_num}{res.value}': {msg}}
    return {}



############## EX7 Specific Testers ##############

def ex7_simple_tester(student_func, cases, expected, err_code, specific_forbidden_ptrns=None):
    err_dict = {}

    forbidden_ptrns = [r"for.*in\s.*:", r"while.*:"]
    if specific_forbidden_ptrns is not None: forbidden_ptrns += specific_forbidden_ptrns



    # Regular case vs expected test
    err_dict.update(simpleTester(student_func, cases, expected, err_code))

    # Search for ptrns that indicate non-recursive solution
    search_res, ptrn = search_for_forbidden_patterns(forbidden_ptrns, student_func)
    if search_res == True:
        err_dict.update(proccessTestRes(err_code,
                                        case_num=0,
                                        res=TestResult.FORBIDDEN,
                                        msg=f"Usage of forbidden ptrn: {ptrn} found"))

    return err_dict


def testQ1a(student_func, err_code):
    cases = [0,
             2,
             5,
             14]

    # Expected values list
    expected = [0, 2, 12, 4362]

    return simpleTester(student_func, cases, expected, err_code)

def testQ1b(student_func, err_code):
    cases = [55]
    # Expected values list
    expected = [2113625914350984]

    return simpleTester(student_func, cases, expected, err_code)

def testQ2(student_func, err_code):
    cases = [0, 10, 42]

    # Expected values list
    expected = [1, 514229, 433494437]

    return simpleTester(student_func, cases, expected, err_code)


def testQ3(student_func, err_code):
    cases = [0, 1, 2, 9]

    # Expected values list
    expected = [1, 1, 2, 4862]

    return simpleTester(student_func, cases, expected, err_code)


def testQ4(student_func, err_code):
    cases = [(0, []),
             (1, []),
             (0, [1, 2, 3]),
             (5, [3, 6, 7]),
             (20, [20, 1]),
             (133,[1,2,5,6,13,4,])
            ]

    expected = [1, 0, 1, 0, 2, 4]

    return simpleTester(student_func, cases, expected, err_code)


def testQ4b(student_func, err_code):

    cases =  [
        (143,[1,2,5,6,13,4])
    ]
    expected = [264930]

    return simpleTester(student_func, cases, expected, err_code)
