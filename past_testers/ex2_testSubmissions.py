import pandas as pd
import regex as re
import inspect
import sys
import io
import contextlib
import signal
import copy


from specific_tests.ex2_specific_tester_variables import QHandler_lst, NUM_OF_QUESTIONS
from specific_tests.pythonExConfig import TESTS, NUM_QUESTIONS #, CASE_INSENSITIVE_QUESTIONS


class SafeDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            dict.__setitem__(self, key, value)
        else:
            raise KeyError("Key already exists - check for duplicate error code: " + key)

err_dict = SafeDict()  # define such a dictionary to document errors
EXCEPTION_MESSAGE_TOLERANCE = 25

VERBOSE = True
DELIM = '# Question'



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


def markException(e, errCodes) -> int:
    '''
    receive exception 'e' and a list of one or more err_codes. insert err_codes to errors dictionary as keys
    and insert the exception representation as the values in the dictionary.
    the dictionary is global and it'S edited in-place
    :param e: exception that occurred outside of the function, it'S str representation will be the value of the dictionary.
    :param errCodes: a list of error codes, they will be the keys in the dictionary.
    :return:
    '''
    errCodes = errCodes.split()
    for errCode in errCodes:
        err_dict[errCode] = ('Initialization for test bulk failed: ' if len(errCodes) > 1 else '') + str(e)

    return 0

def proccessTestRes(test_res, err_code, exp, output):
    global err_dict
    if test_res == False:
        markException(f"Wrong output: {output}\n, expected: {exp}!", err_code)

    elif test_res == 'J':
        markException(f"Inaccurate printout: {output}", err_code + test_res)

    elif test_res == 'L':
        markException(f"Inaccurate calulation of a number: {output}", err_code + test_res)

    return True

def search_student_code_for_text(pattern, student_module) -> bool:
    '''
    Search the student'S source code and return True if it has 'pattern' in it.
    This could be used to look for imports of certain packages or for use of certain functions.
    :param pattern: to search for.
    :param student_module: Student module to search in.
    :return: True if 'text' exists in the source of 'student_module'
    '''
    stud_source = inspect.getsource(student_module)
    return len(re.findall(pattern, stud_source)) > 0



def testSubmission(student_module):
    global err_dict
    err_dict = SafeDict()
    signal.signal(signal.SIGALRM, handler)


    if(VERBOSE):
        print(f"Submission name: {student_module.__name__}")

    #General test pattern, try to activate the function, if it doesn't work -> exception
    with open(student_module.__file__, errors='ignore') as submission: # 'ignore' solves encoding problems
        contents = submission.read()
        # Split the student code into different questions using DELIM variable
        question_codes_unfiltered = contents.split(DELIM)[1:]
        if len(question_codes_unfiltered) < NUM_OF_QUESTIONS:
            raise ValueError("Imp")

        # Strip the built in characters from each question, leaving only the student code
        question_codes_unfiltered = list(map(lambda question: re.split('(#+\n)', question)[2], question_codes_unfiltered))

        #define a lambda function for stripping the student code from assignment
        getQuestionCode = lambda rawQuestion, test: '\n'.join(filter(_assignmentRemover(test.vars),
                                                                     rawQuestion.splitlines()[1:]))

        tests = copy.deepcopy(TESTS)
        err_codes = ['A', 'B', 'C', 'D', 'E']
        for qNum, (q, test) in enumerate(zip(question_codes_unfiltered, tests), 1):
            # Remove variables assignment for each question
            q_code_filtered = getQuestionCode(q, test)
            testQuestion(qNum, q_code_filtered, test, err_codes[qNum-1])

    return err_dict

def testQuestion(qNum, code, test, err_code):
    '''
    Returns a tuple containing:
    1. the error string (returned to student)
    2. list of outputs for error cases
    '''


    if VERBOSE:
        print('Testing Question:', qNum)

    if qNum == 2:
        if not ("while" in code and "for" in code):
            curr_err_code = f'{err_code}6'
            markException("Did not implement while loop and for loop both", curr_err_code)

    for i, case in enumerate(test.cases):
        curr_err_code = f'{err_code}{i+1}'
        if VERBOSE:
            print(f"Performing test {curr_err_code}")


        # Zip into a dictionary the variables for this code and their values for the current test
        # print(_testItem.get_var_vals_list())
        testEnv = dict(zip(test.vars, case[0]))

        # Execure student code and redirect output to catch student code printouts

        with stdoutRedirect() as execOutput:
            try:
                signal.alarm(3)
                exec(code, testEnv)
                signal.alarm(0)

            except TimeoutError as inf:
                markException(inf, curr_err_code+'Inf')
                continue

            except BaseException as e:
                #Mark exception and err code
                markException(e, curr_err_code)
                continue

        prints = execOutput.getvalue()[:-1]
        expectedOutput = case[1]

        #Test the student's answer and proccess the result

        test_res = test.checker(expectedOutput, prints)
        print(test_res)
        proccessTestRes(test_res, curr_err_code, expectedOutput, prints)

    if VERBOSE:
        print('Finished testing Question:', qNum)
    return

@contextlib.contextmanager
def stdoutRedirect(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def handler(signum, frame):
    '''
    Register an handler for the timeout
    :param signum: SIGNAL number to handle
    :param frame:
    :return: None
    '''

    print("Infinite loop encountered!")
    raise TimeoutError("Infinite loop encountered!")


def _assignmentRemover(vars):
    '''
    Idea for making it better:
    Use ast.literal_eval _inside a try to see if an assignment is done to literal
    '''
    varsToRemove = list(vars)
    alreadyRemoved = {}

    def assignmentFilter(line):
        # print line
        assignedVarMatch = re.search('\s*(\w+).*=(.*)', line)
        if not assignedVarMatch: return True

        assignedVar = assignedVarMatch.group(1)
        # print 'found', assignedVar
        if assignedVar not in varsToRemove: return True

        # Always remove first time var is found
        if assignedVar not in alreadyRemoved:
            alreadyRemoved[assignedVar] = 1
            return False

        # Here check if assignment is done to a literal or to input() call
        assignmentRhs = assignedVarMatch.group(2).lstrip()
        isRhsLiteral = False
        """
        try:
            ast.literal_eval(assignmentRhs)
            isRhsLiteral = True
        except BaseException as e:
            pass  # print(e)
        """
        if isRhsLiteral: return False

        isRhsInput = re.match('.*input.*\(.*\)', assignmentRhs)  # catching call to input()

        return not isRhsInput

    return assignmentFilter






