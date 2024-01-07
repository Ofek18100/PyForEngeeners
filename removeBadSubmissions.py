import importlib
import signal
from glob import glob
import os
import importlib.util as util
import sys
import multiprocessing
import time
import shutil
from enum import Enum
from pathlib import Path

main_comment = '# You can add more tests below.'

class Test_Result(Enum):
    GOOD = 1
    ENDLESS_LOOP = 2
    FAIL = 3

def check_correct_and_failed_submissions(submissions_dir, output_dir_correct, output_dir_failed):
    endless_loops_list = []
    error_while_loading_list = []
    good_files = 0
    # first iteration:
    for single_file in glob(os.path.join(submissions_dir, "*.py")):
        base_name = os.path.basename(single_file)
        print(base_name)
        test_res = check_single_file(single_file)
        if test_res == Test_Result.ENDLESS_LOOP:
            endless_loops_list.append(base_name)
            shutil.copy(single_file, os.path.join(output_dir_failed, base_name))
            print(f"\tendless loop in {single_file}")
        elif test_res == Test_Result.FAIL:
            error_while_loading_list.append(base_name)
            shutil.copy(single_file, os.path.join(output_dir_failed, base_name))
            print(f"\tfailed loading in {single_file}")
        else:
            shutil.copy(single_file, os.path.join(output_dir_correct, base_name))
            good_files += 1

    print(f"endless loops: {len(endless_loops_list)}")
    print(f"errors while loading loops: {len(error_while_loading_list)}")
    print(f"good files: {good_files}")
    return endless_loops_list + error_while_loading_list



def check_single_file(single_file, print_error=False):

    process = multiprocessing.Process(target=try_loading, args=(single_file,))
    process.start()
    time.sleep(1.5)
    if process.is_alive():
        process.terminate()  # stuck in a loop
        if print_error:
            print("Endless loop")
        return Test_Result.ENDLESS_LOOP
    else:
        if not try_loading(single_file, print_error): # error while loading the file
            return Test_Result.FAIL
    return Test_Result.GOOD

def try_loading(single_file, print_error = False):
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    error = None
    try:
        try:
            base_name = os.path.basename(single_file).split(".py")[0]
            spec = util.spec_from_file_location(base_name, os.path.join(submissions_dir, single_file))
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except Exception as exp :
            error = f"\tException: {exp}"
            return False
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout
        if print_error and error is not None:
            print(error)


def comment_out_code_after_main_comment(in_file, main_comment, output_dir):
    new_lines = []
    with open(in_file, 'r') as f_in:
        comment_out = False
        for line in f_in.readlines():
            if main_comment in line:
                comment_out = True
            if comment_out:
                new_lines.append(f"# {line}")
            else:
                new_lines.append(line)
    base_name = os.path.basename(in_file)
    fixed_file = os.path.join(output_dir, base_name[:-3]+'_fixed.py')
    with open(fixed_file, "w") as f_out:
        f_out.writelines(new_lines)
    return fixed_file

def fix(failed_sumissions_dir, output_dir):

    fixed_files_list = []
    for single_file in glob(os.path.join(failed_sumissions_dir, "*.py")):
        base_name = os.path.basename(single_file)
        print(f"fixing {base_name}")
        #gentle fix
        fixed_file = comment_out_code_after_main_comment(single_file, main_comment, output_dir)
        test_result = check_single_file(fixed_file, print_error=True)
        if test_result == Test_Result.GOOD:
            # Remove old file from failed submissions dir to clean it up
            os.remove(single_file)
            fixed_files_list.append(base_name)
            print("\tSuccessfully loaded !")
        else:
            # Remove failed to fix file from output dir
            filepath = os.path.join(output_dir, fixed_file)
            os.remove(filepath)

        print("---------")

    return fixed_files_list

if __name__ == "__main__":
    from configparser import ConfigParser, ExtendedInterpolation
    configParser = ConfigParser(interpolation=ExtendedInterpolation())
    configParser.read("./config.ini")

    # main_path = configParser["paths"]["resource_path"]
    out_path = configParser["paths"]["out_path"]
    # Read from here
    global submissions_dir
    submissions_dir = configParser["paths"]["main_path"]

    # Move valid files here
    valid_files_path = configParser["paths"]["valid_files_path"]
    os.makedirs(valid_files_path, exist_ok=True)
    # Move invalid files here
    bad_files_path = configParser["paths"]["failed_to_fix_path"]
    os.makedirs(bad_files_path, exist_ok=True)

    # After you have "good" and bad submissions you can comment out this line
    # Get a list of the failed files
    # failed_files = check_correct_and_failed_submissions(submissions_dir, valid_files_path, bad_files_path)

    # Move files fixed by the script here
    fixed_files_path = configParser["paths"]["fixed_files_path"]
    os.makedirs(fixed_files_path, exist_ok=True)

    main_comment = '# You can add more tests below.'
    os.makedirs(fixed_files_path, exist_ok=True)

    fixed_files = fix(bad_files_path, fixed_files_path)


    # final_failures = [file for file in failed_files if file not in fixed_files]

    print("Writing fixed files names to file")

    # Write a report
    with open(Path(out_path, "fixed_files_report.txt"), "w") as file:
        file.writelines(''.join(i) + '\n' for i in fixed_files)
