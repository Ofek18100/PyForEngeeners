import re
import ast
import sys
import io
import contextlib

# For stripping of litterl code (EX1, EX2)
import editdistance


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
        try:
            ast.literal_eval(assignmentRhs)
            isRhsLiteral = True
        except BaseException as e:
            pass  # print(e)
        if isRhsLiteral: return False

        isRhsInput = re.match('.*input.*\(.*\)', assignmentRhs)  # catching call to input()

        return not isRhsInput

    return assignmentFilter





# For handling output redirection
@contextlib.contextmanager
def stdoutRedirect(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


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

def markException_new(e, errCodes) -> int:
    pass


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

def proccessTestRes(test_res, err_code, exp, msg):
    global err_dict
    if test_res == False:
        markException(msg, err_code)

    #TODO fix to fit the msg instead of the output
    # elif test_res == 'J':
        # markException(f"Inaccurate printout: {output}", err_code + test_res)

    # TODO fix to fit the msg instead of the output
    # elif test_res == 'L':
    #     markException(f"Inaccurate calulation of a number: {output}", err_code + test_res)

    elif test_res == 'N':
        markException(msg, f'{err_code}N')

    return True

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


def handler(signum, frame):
    '''
    Register an handler for the timeout
    :param signum: SIGNAL number to handle
    :param frame:
    :return: None
    '''

    print("Infinite loop encountered!")
    raise TimeoutError("Infinite loop encountered!")