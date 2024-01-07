from configparser import ConfigParser, ExtendedInterpolation
import os


'''
This module builds the folder structure of the project, for inputs, outputs etc.
It read for the path variables from the config.ini file and then creates the directories in the paths.
If directories exist it skips them.
'''


def build_project_from_config(configParser):
    # configParser = ConfigParser(interpolation=ExtendedInterpolation())
    # config_path = '/Users/d_private/_git/PyProg-tester/past_configs/2022b_ex6_config.ini'
    # configParser.read(config_path)

    for key, path in configParser["paths"].items():
        os.makedirs(path, exist_ok=True)
        # Make sure no resource directories are comitted to git by accident
        with open(f"{path}/.gitignore", 'w') as file:
            file.write('*\n/*')


    # Make sure there's no FileNotFound err when trying to read outputs/fixed_files_report.txt
    filename = configParser["paths"]["out_path"]+'/fixed_files_report.txt'
    if not os.path.exists(filename):
        with open(filename, 'w'): pass

    return 0


if __name__ == '__main__':
    config_parser = ConfigParser(interpolation=ExtendedInterpolation())
    config_parser.read("config.ini")
    build_project_from_config(config_parser)
'''
    from configparser import ConfigParser, ExtendedInterpolation
    config_parser = ConfigParser(interpolation=ExtendedInterpolation())
    config_parser.read("config.ini")
'''
