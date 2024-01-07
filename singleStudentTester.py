import importlib
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from configparser import ConfigParser, ExtendedInterpolation
import regex as re
import inspect
import signal
from testerFuncsArchieve import _assignmentRemover, stdoutRedirect
# skips = [1, 4, 3, 2]
skips = []

from SafeDict import SafeDict

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


def import_student_module_by_name(student_module_name: str):

    '''
    If student module takes more than 3 seconds to import then the student has probably left a code block that
    interrupts. This might interfere debugging, in this case just comment-up the timers.
    '''
    signal.alarm(3)
    student_module = importlib.import_module(student_module_name[:-3])
    signal.alarm(0)  # must turn off timer

    return student_module

''' Multi proccessing helper funcs '''

def worker2(args):
    tester_func, stud_func, err_code = args
    return tester_func(stud_func, err_code)

def stop_process_pool(executor):
    for pid, process in executor._processes.items():
        process.terminate()
    executor.shutdown()

def testSubs1or2(student_module,  student_module_name, qhandler_list, VERBOSE, EX_NUM):

    configParser = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = '/Users/d_private/_git/PyProg-tester/past_configs/2022b_ex1_config.ini'
    configParser.read(config_path)

    DELIM = '# Question'
    VARS_LIST = []

    for qnum, var_names_for_question in configParser["ex1ex2_var_names"].items():
        var_names_for_question = var_names_for_question.split(',')
        VARS_LIST.append(var_names_for_question)

    #General test pattern, try to activate the function, if it doesn't work -> exception
    with open(student_module.__file__, errors='ignore') as submission: # 'ignore' solves encoding problems
        contents = submission.read()
        # Split the student code into different questions using DELIM variable
        question_codes_unfiltered = contents.split(DELIM)[1:]

        if len(question_codes_unfiltered) < len(qhandler_list):
            msg = f"Failed to import module, name: {student_module_name[:-3]}. only: {len(question_codes_unfiltered)}" \
                  f" were found in the module instead of {len(qhandler_list)}, skipping student."
            if (VERBOSE):
                print(msg)
            return {'Imp': msg}

        # Strip the built in characters from each question, leaving only the student code
        # question_codes_unfiltered = list(map(lambda question: re.split('(#+\n)', question)[2], question_codes_unfiltered))

        #define a lambda function for stripping the student code from assignment
        stripAssignments = lambda var_list, question_code : '\n'.join(filter(remove_assignments_from_codeBlock(var_list),
                                                                         question_code.splitlines()[1:])
                                                                   )



    for qnum, _qhandler in enumerate(qhandler_list, 1):
        if (qnum in skips): continue
        stud_func_name, tester_func, err_code = _qhandler.stud_func_name, _qhandler.tester_func, _qhandler.err_code
        # Remove variables assignment for each question
        q_code_filtered = stripAssignments(VARS_LIST[qnum-1], question_codes_unfiltered[qnum-1])


        try:
            signal.alarm(3)  # For debugging purposes
            err_dict.update(tester_func(student_code=q_code_filtered, err_code=err_code))
            signal.alarm(0)  # must turn off timer
        except Exception as t:
            msg = f"**{type(t).__name__}**! to initiate test block for Q{qnum} with err: {t}"
            if (type(t) == TimeoutError):
                err_dict.update({f"{err_code}Inf": msg})
            else:
                err_dict.update({f"{err_code}Imp": msg})
            if VERBOSE:
                print(f"{msg}, Skipping to next question")
            continue

        if VERBOSE:
            print('Finished testing Question:', qnum)


    return err_dict

''' main tester func '''
def testSingleStudentSubmissions(student_module_name, qhandler_list, VERBOSE, EX_NUM):

    global err_dict

    err_dict = SafeDict()
    signal.signal(signal.SIGALRM, handler)

    if(VERBOSE):
        print(f"Starting to test student: {student_module_name.split('_')[0]}")

    try:
        if (VERBOSE):
            print(f"Now importing student module: {student_module_name[:-3]}")
        student_module = import_student_module_by_name(student_module_name)

    except Exception as e:
        msg = f"**{type(e).__name__}**! Failed to import module, name: {student_module_name[:-3]}. skipping\n with error: {type(e).__name__}"
        if (VERBOSE):
            print(msg)
        return {'Imp': msg}


    if (VERBOSE):
        print(f"Import succeeded, Starting to test")

    if(EX_NUM in ['1', '2']):
        err_dict.update(testSubs1or2(student_module, student_module_name, qhandler_list, VERBOSE, EX_NUM))
        if err_dict == {}:
            err_dict = {'OK': 'Passed all tests'}
        return err_dict



    for qnum, _qhandler in enumerate(qhandler_list, 1):

        if VERBOSE:
            print('Testing Question:', qnum)

        stud_func_name, tester_func, err_code = _qhandler.stud_func_name, _qhandler.tester_func, _qhandler.err_code
        stud_func = None


        try:
            stud_func = student_module.__dict__[stud_func_name]
        except Exception as e:
            if not EX_NUM in ['8', '9', '10']:

                msg = f"**{type(e).__name__}**! Failed to import func: {stud_func_name} from student module."
                err_dict.update({f"{err_code}Imp": msg})
                if VERBOSE:
                    print(f"{msg}, Skipping to next question")
                continue

        args = (tester_func, stud_func, err_code)
        if EX_NUM in ['8', '9', '10']:
            args = (tester_func, student_module, err_code)

        with ProcessPoolExecutor(1) as executor:
        # Pool executor returns a list of results, one result per one process therefore we take the results @ [0]
        # The timeout param is handling infinite loops
        # args must be packed as a tuple that contains the varibales for the worker function that calls the tester
        # and then it must be packed in a list because the executor launches one instance for each item in the iterable list
            try:

                # signal.alarm(4) # For debugging purposes
                # test_res = list(executor.map(worker2, [args], timeout=3))[0]
                test_res = list(executor.map(worker2, [args]))[0]

                # test_res = worker2(args)
                # signal.alarm(0)  # must turn off timer
                err_dict.update(test_res)
            # Handle test errors, espcially timeout error
            except Exception as t:
                msg = f"**{type(t).__name__}**! to initiate test block for Q{qnum} with err: {t}"
                if(type(t) == TimeoutError):
                    err_dict.update({f"{err_code}Inf": msg})
                else:
                    err_dict.update({f"{err_code}Imp": msg})
                if VERBOSE:
                    print(f"{msg}, Skipping to next question")
                stop_process_pool(executor)
                continue



        if VERBOSE:
            print('Finished testing Question:', qnum)

    if err_dict == {}:
        err_dict = {'OK': 'Passed all tests'}
    if VERBOSE:
        print(f"Finished testing student: {student_module_name.split('_')[0]}\n")

    return err_dict



def handler(signum, frame):
    '''
    Register an handler for the timeout
    :param signum: SIGNAL number to handle
    :param frame:
    :return: None
    '''

    print("Alarm Raised")
    raise TimeoutError("Timeout reached!")



############### ARCHIVE ########################


def remove_assignments_from_codeBlock(vars_list):
    '''
    Create a mapping function that returns true for if a line has assignment for a variables in vars+list
    :param qnum: a list of string representations of the variables that the mapping functions needs to remove from the
    code
    :return: a mapping fucntion - assignmentFilter
    '''

    varsToRemove = vars_list
    alreadyRemoved = {}

    def assignmentFilter(line):
        '''

        :param line: a text line, a fragment of code
        :return: True if the line isn't an assignment line, or if the variable in the line was already removed
        '''

        # Find lines with variable assignments.
        # this regex divides an assignment lines into two groups separated by the '=' operator
        assignedVarMatch = re.search('\s*(\w+).*=(.*)', line)
        # If there was no match -> there was no assignment, return True
        if not assignedVarMatch: return True

        # Extract the variable name itself (comes before the '=')
        assignedVar = assignedVarMatch.group(1)

        # If the extracted variable is not in varsToRemove - return true
        if assignedVar not in varsToRemove: return True

        # Always remove first time var is found
        if assignedVar not in alreadyRemoved:
            alreadyRemoved[assignedVar] = 1
            return False

        # Here check if assignment is done to a literal or to input() call
        assignmentRhs = assignedVarMatch.group(2).lstrip()
        #TODO check if this can help
        # isRhsLiteral = False
        # try:
        #     ast.literal_eval(assignmentRhs)
        #     isRhsLiteral = True
        # except BaseException as e:
        #     pass  # print(e)
        # if isRhsLiteral: return False

        isRhsInput = re.match('.*input.*\(.*\)', assignmentRhs)  # catching call to input()

        return not isRhsInput

    return assignmentFilter