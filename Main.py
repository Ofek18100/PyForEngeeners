import glob
import pandas as pd
import sys
import importlib
import shutil
import matplotlib.pyplot as plt
from collections import namedtuple
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
import os
import regex as re

## In package imports ##
from singleStudentTester import testSingleStudentSubmissions as testSubmission

from buildProjectStructure import build_project_from_config as build_project
from checkCopiesBasic import main as check_copies
from SafeDict import SafeDict

QuestionHandler = namedtuple('QuestionHandler', ['stud_func_name', 'tester_func', 'err_code'])

configParser = ConfigParser(interpolation=ExtendedInterpolation())
config_path = '/home/guysh/PyForEngeenersTester/config.ini'
configParser.read(config_path)


OUTPUT_PATH = configParser["paths"]["out_path"]

INPUT_PATH = ''
EX_NUM = configParser["misc"]["EX_NUM"]
SEMESTER = configParser["misc"]["SEMESTER"]
VERBOSE = configParser.getboolean("flags", "IS_VERBOSE")
IS_RECHECK = configParser.getboolean("flags", "IS_RECHECK")


'''
It's possible to check only some of the students' this is relevant for checking specific anomalies or for appeals.
If the list is empty, all students will be checked. If the list has names in it of the form 'First_name Last_name'
then the output files will have 'spec' prefix.
'''
# SPECIFIC_FILES_TO_CHECK = ['Adan Ghuneim']

########### Handle submission path ####################

def set_input_path(external_input_path):
    global INPUT_PATH

    if external_input_path is not None:
        INPUT_PATH = external_input_path
    elif IS_RECHECK:
        INPUT_PATH = configParser["paths"]["fixed_files_path"]
    else:
        INPUT_PATH = configParser["paths"]["valid_files_path"]
    return 0


########### Building the grades and students dataframe ####################
# Lambda functions for bulding the students and submissions dataframe
# Extract student id and student name from the submission name which is autoformatted by the MOODLE
get_stud_id_from_filepath = lambda filepath: filepath.split('_file_')[1].split('_')[0]
get_stud_name_from_filepath = lambda filepath: os.path.basename(filepath).split('_')[0]
get_file_validty = lambda filepath: filepath.lower().endswith('.py')
get_moudle_name = lambda filepath: filepath.split(os.path.sep)[-1]
get_stud_identifier = lambda filepath: os.path.basename(filepath).split('_')[1]

def build_df_from_file_list(files_list: list)-> pd.DataFrame:
    res_df = pd.DataFrame(files_list, columns=['file_path'])
    # res_df.file_path = res_df.file_path.str.lower()
    res_df = res_df.assign(
        stud_id=res_df.file_path.apply(get_stud_id_from_filepath),  # extract student id from file name
        stud_name=res_df.file_path.apply(get_stud_name_from_filepath),  # extract student name from file name
        valid_file_flag=res_df.file_path.apply(get_file_validty),  # check it the file name ends with '.py'
        file_name=res_df.file_path.apply(get_moudle_name),  # extract relative file name for importing it later
        stud_identifier=res_df.file_path.apply(get_stud_identifier)
        # extract student identifier to later merge it with the submission times database
    )

    col_order = ['stud_id', 'stud_name', 'file_name', 'valid_file_flag', 'file_path', 'stud_identifier']
    res_df = res_df[col_order]
    res_df = res_df.set_index('stud_id', drop=True)
    return res_df

def get_file_list_from_path(path: str)->list:
    caps_files = glob.glob(path + r'/*submission_file*.PY')
    for file in caps_files:
        print(file)
        new_name = file[:-3] + '.py'
        print(new_name)
        os.rename(file, new_name)

    files_list = glob.glob(path + r'/*submission_file*.py')

    return files_list


def relocate_bad_files(bad_files_df: pd.DataFrame) -> str:
    bad_files_df.to_csv(OUTPUT_PATH + f'/ex{EX_NUM}_import_error.csv')

    bad_files_path = Path(configParser["paths"]["failed_to_test_path"])

    if (VERBOSE):
        print(f"Bad files df head: {bad_files_df.head}")
        print(f"Copying bad files to new path: {bad_files_path}")

    # Copy all files
    for file_path in bad_files_df.file_path:
        if (VERBOSE):
            print(f"Copying file: {file_path}")
        relative_name = get_moudle_name(file_path)
        shutil.copy(file_path, f'{bad_files_path}/{relative_name}')

    return bad_files_df


########### Testing the student code functions. These are here as an archive, should be copied to the tester file ########

def run_copy_analysis(students_df: pd.DataFrame):
    mask = students_df.err_codes == 'Imp'
    valid_files = students_df[~mask]
    copies_df = check_copies(list(valid_files.file_path))
    copies_df.to_csv(OUTPUT_PATH + f'/ex{EX_NUM}_copy_analysis.csv')

    if VERBOSE:
        print(copies_df.describe())


def get_err_count(err_codes_str: str)-> float:
    '''
    THIS FUNCTION IS USED AGAIN TO REFACTOR GRADES AT THE FINAL NOTEBOOK, ITS HERE FOR PURPOSE OF CONSERVATION
    Get a string representing all error codes that a student has.
    Count the different types of errors and return the weighted total of errors.
    :param err_codes_str: string representation of error codes, format is a  a comma seprated string representation of
    a list, such assuch as 'A1, D*2, C3' etc.
    :return: float representing the total weighted errors.
    '''
    if(err_codes_str == 'OK'): return 0

    regular_errs_sum = 0
    for err_code in ['A', 'B', 'C', 'D', 'E']:
        # Count err codes for each question, if more than 3 errors in the same question, it becomes a following error
        regular_errs_sum += min(len(re.findall(err_code, err_codes_str)), 3)

    imp_flag = len(re.findall('Imp', err_codes_str))
    RECHECK_flag = len(re.findall('RE', err_codes_str))
    err_count =  imp_flag * 10 + regular_errs_sum * 1  + RECHECK_flag * 3
    return err_count



def get_final_grade(err_count: float) -> int:
    '''
    THIS FUNCTION IS USED AGAIN TO REFACTOR GRADES AT THE FINAL NOTEBOOK, ITS HERE FOR PURPOSE OF CONSERVATION
    Return a grade according to number of grades
    :param err_count: a float representing number of errors (e.g 15.5)
    :return: an integer representing the final grade according to the grading rules.
    '''
    if err_count <= 2.0:
        return 100
    elif err_count <= 5.0:
        return 90
    elif err_count <= 10.0:
        return 80
    elif err_count <= 25.0:
        return 60
    else:
        return 0

def integrate_errors(students_df: pd.DataFrame, err_dict: dict)-> pd.DataFrame:
    err_df = pd.DataFrame.from_dict(err_dict, orient='index')
    err_df = err_df.reset_index()
    err_df.rename(columns={'index': 'stud_id'}, inplace=True)
    students_df = students_df.reset_index()
    students_df.rename(columns={'index': 'stud_id'}, inplace=True)
    students_df = pd.merge(students_df, err_df, on='stud_id')

    return students_df

def enrich_student_df_with_errs(students_df: pd.DataFrame, err_df_extended: pd.DataFrame):
    cols = list(err_df_extended.columns)
    cols.remove('stud_id')
    cols.remove('stud_name')
    err_df_longform = err_df_extended.melt(id_vars='stud_id', value_vars=cols, var_name='err_code').dropna()
    err_codes = err_df_longform.groupby('stud_id').err_code.apply(lambda x: ", ".join(x))
    students_df = students_df.merge(err_codes, on = 'stud_id', how ='outer').rename({'err_code':'err_codes'}, axis=1)
    return students_df

def summarize_main(students_df: pd.DataFrame, err_df_extended: pd.DataFrame)-> pd.DataFrame:
    # Merge the error codes to the general df
    students_df = enrich_student_df_with_errs(students_df, err_df_extended)
    students_df = students_df.assign(err_count = students_df.err_codes.apply(lambda  err_list: get_err_count(err_list)))
    students_df = students_df.assign(final_grade=students_df.err_count.apply(lambda err_num: get_final_grade(err_num)))

    return students_df


def plotResults(students_df_summary: pd.DataFrame) -> None:

    dist = students_df_summary.final_grade.value_counts(normalize=True, sort=False)
    dist.plot(kind='bar', figsize=(12, 8), rot = 45)
    plt.xlabel('Grades')
    plt.ylabel('Frequency')
    plt.title(f'Python for Engineers, {SEMESTER}, Ex{EX_NUM} - Grades distribution')
    dist_norm = students_df_summary.final_grade.value_counts(normalize=True, sort=False)
    dist_quant = students_df_summary.final_grade.value_counts(normalize=False, sort=False)
    temp = pd.DataFrame(dist_norm)
    temp = temp.assign(num_of_students=dist_quant)
    temp.rename({'final_grade': 'percent_of_total'}, inplace=True, axis=1)
    temp.percent_of_total = temp.percent_of_total.apply(lambda per: round(per, 3))
    temp = temp[['num_of_students', 'percent_of_total']]
    temp = temp.sort_index(ascending = False)
    temp.index.name = 'Grade'
    plt.show()

    num_of_imports = students_df_summary.err_codes.apply(lambda err_codes: bool(re.search(r'\bImp', err_codes))).sum()
    print(f"*******\n"
          f"Final Ex{EX_NUM} data:\n"
          f"Number of corrupted (Failed to test) submissions: {num_of_imports}\n"
          f"Median num of errors is: {round(students_df_summary.err_count.median(), 0)}\n"
          f"Avg num of errors is: {round(students_df_summary.err_count.mean(), 0)}\n"
          f"Grade distribution is:\n\n{str(temp)}\n"
          f"*******\n")


def create_extended_error_df(err_dict_extended: dict, students_df: pd.DataFrame) -> pd.DataFrame:
    # TODO document
    # IF debug flag is on, print a dataframe containing for each student what failed in what test
    # In the dataframe, if a cell is empty the student has no error, if it is False then he had a value mistake.
    # If the test raised an error it will be printed under that cell in the dataframe

    err_df_extended = pd.DataFrame.from_dict(err_dict_extended, orient='index')
    cols = sorted(list(err_df_extended.columns))
    err_df_extended = err_df_extended[cols]
    err_df_extended = err_df_extended.reset_index().rename({'index': 'stud_id'}, axis=1)

    err_df_extended = pd.merge(err_df_extended, students_df[['stud_id', 'stud_name']], on='stud_id', how='right')
    cols = ['stud_id', 'stud_name'] + cols
    return err_df_extended[cols]


def createQuestionHandlersList():

    stud_func_names_list = []
    test_funcs_list = []
    err_codes_list = []
    # I
    for qnum, stud_func_name in configParser["stud_func_names"].items():
        stud_func_names_list.append(stud_func_name)

    # Import the tester module for the whole excercise
    tester_module = importlib.import_module(configParser.get("misc", "tester_file_path"))

    # Read the tester func names from the config list and import each tester func from the tester module
    for qnum, item in configParser["test_funcs"].items():
        test_func_name, err_code = item.split(', ')
        test_funcs_list.append(tester_module.__dict__[test_func_name])
        err_codes_list.append(err_code)

    # Create pairs (QuestionHandlers named tuples of student func names and it's actual tester func)
    # Note that the tester func is actually the import function from the tester file while the student func is only the name
    return [QuestionHandler(s, t, e) for s, t, e in zip(stud_func_names_list, test_funcs_list, err_codes_list)]


def main(external_input_path: str = None, external_output_path_path: str = None, should_write=True):

    err_dict_extended = SafeDict()
    # Build project paths from config file
    build_project(configParser)
    # Set paths for files
    set_input_path(external_input_path)
    # Import the tests file where all tester functions are

    try:
        qhandler_list = createQuestionHandlersList()

    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Failed to import tester file module, check path and config file for mistakes, error: {e}")

    # Specific files path
    # INPUT_PATH = configParser["paths"]["specific_files_path"]

    sys.path.append(INPUT_PATH)
    files_list = get_file_list_from_path(INPUT_PATH)
    students_df = build_df_from_file_list(files_list)


    # mark all students with bad file names
    mask = students_df.valid_file_flag == False
    bad_file_df = students_df[mask].reset_index()
    relocate_bad_files(bad_file_df)


    # remove bad files from students df according to their valid_file_flag.
    # If the same student has more than one file, and one of the files is not valid, all other files will also be removed \
    # So in that case it is better to move the old files to a new location.
    students_df = students_df[~students_df.isin(bad_file_df)].dropna()
    students_df = students_df.reset_index().rename({'index': 'stud_id'}, axis=1)

    for index, entry in students_df.iterrows():
        stud_id = entry.stud_id
        err_dict_extended[stud_id] = {}

        test_res = testSubmission(entry.file_name, qhandler_list, VERBOSE, EX_NUM)

        err_dict_extended[stud_id].update(test_res)

        # If the recheck flag is on then mark all exercises with RE mark for grading.
        if (IS_RECHECK):
            # err_dict[stud_id].append('RE')
            err_dict_extended[stud_id].update({'RE': 'recheck flag'})

    # Merge errors dict, summarize the results, count errors
    err_df_extended = create_extended_error_df(err_dict_extended, students_df)

    ''' Consider moving this part and on to summarize'''
    students_df = summarize_main(students_df, err_df_extended)

    # Write extended errors df to file for debugging

    if should_write:
        if INPUT_PATH == configParser["paths"]["specific_files_path"]:
            filename = f"ex{EX_NUM}_specific_err_df_extended.csv"
        elif (IS_RECHECK):
            filename = f"ex{EX_NUM}_recheck_err_df_extended.csv"
        else:
            filename = f"ex{EX_NUM}_err_df_extended.csv"
        err_df_extended.to_csv(f'{OUTPUT_PATH}/{filename}')

    # Create a 'cleaner' version of the dataframe for plotting
    cols = ['stud_id', 'stud_name', 'valid_file_flag', 'err_codes', 'err_count', 'final_grade']
    students_df_summary = students_df[cols]


    # Write results out, and plot a graph describing the results + summary statistics
    if INPUT_PATH == configParser["paths"]["specific_files_path"]:
        filename = f"ex{EX_NUM}_specific_students_df.csv"
    elif (IS_RECHECK):
        filename = f"ex{EX_NUM}_recheck_students_df.csv"
    else:
        filename = f"ex{EX_NUM}_students_df.csv"

    if should_write:
        students_df_summary.to_csv(f'{OUTPUT_PATH}/{filename}')
        # plotResults(students_df_summary)


    if not IS_RECHECK:
        mask = students_df.err_codes == 'Imp'
        bad_files_df = students_df[mask]
        imp_df = relocate_bad_files(bad_files_df)
        print(imp_df.stud_name)
        print(bad_file_df.stud_name)

    if configParser.getboolean("flags", "CHECK_COPY"):
        run_copy_analysis(students_df)
    print(f"the input path is: {INPUT_PATH}")
    print(f"Finished writing outputs to  {OUTPUT_PATH}")
    print(f"Finished grading Ex{EX_NUM} successfully.")

    return students_df_summary

if __name__ == '__main__':
    main("/home/guysh/worksToCheck/fuckers")
