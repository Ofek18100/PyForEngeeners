# How to use the PyProg-tester
## General
The repo is conssisted of modules that are relativley fixed and some modules that has to be created/changed every  submission.
The Main module start the whole operation, using modules the _singleStudentTester, summarizeTesterResults,  and optionally - checkCopiesBasic, buildProjectStructure_ and _removeBadSubmissions._  
In order to adjust the tester a new excercise, one must do the following (generally speaking):
* Update the config.ini for relevant paths and symbols
* Create a specific tester: (e.g _2021a_ex5_tests_) where each function tests a question in the exercise, debug it and put it's path in the _tester_file_path_ in the _config.ini_ file
* Run the Main module to generate grades
* Run the _summary_scripts_ on jupyter to generate final plots and grades

## Some tips
### Specific tester file
* Before your first run make sure you install the requierments described in the _requirements.txt_ by using:
    * $ pip install -r requirements.txt
* Tester functions should return a dictionary of the form {'err_code':'err_message'}.
    * The err_code is set by the config file but it's not mandatory to use the codes in there and you can ignore/add different err codes inside the function as long as you return them in the dict as described.
    * The messages are omitted in the downstream of the program flow. The messages aren't being used or displayed to the students later but they can later allow to check specific mistakes a specific student had if you're not sure. 
*  Some useful functions are kept for archieving in the testerFuncsArchieve file, you can look for useful functions in there.
    * Such useful function is the simpleTester func which is handy if all you want is to run the student function on certain input and then compare the output to some result.
    * You can either import the functions to your specific tester or copy them into it and edit them to your needs.
  

## Module info
* _buildProjectStructure.py_ - A small script that builds the path structure, run this first hand and then put your files in the the relevant folders
* _checkCopiesBasic.py_ - Analyse for copying oddes pair-wise based on kmers.
* _config.ini_ - A configuration file that contains most of the variables for the testing such as 
* _summary_scripts.ipynb_ - A jupyter notebook for analysing the results of the test allowing to produce the final grades, error abundance etc.
* _Main.py_ - The main module that runs the whole operation using the singleStudentTester, checkCopies etc. This is also the module that reads the config file.
* _removeBadSubmissions.py_ - A contirbution by Lena dankin, for fixing some of the submissions that fail to run commenting out lines in the free code section (where the students add there own tests) 
* _SafeDict.py_ - A locally implemented extention of the dictionary class that *does not* allow duplicated keys in order to avoid double student id's etc.
* _singleStudentTester.py_ - along with the Main module this is the most significant module, this module tests the submission for a single student by importing the student function that is being tests and passing it to the specific testing module (e.g __2021a_ex5_tests__)
* _Student late days database.ipynb_ - A notebook for analysing the late submission dates for students.
* _summarizeTesterResults.py_ - Contining some fuctions that proccess the tester results in the Main module to create the finalized students dataframe.
* _testerFuncsArchieve.py_  - A module that stores functions that were previously used in specific testers such as the useful _simpleTester_ func.
* _TestResults.py_ - An enum class that describes possible results for a test of the student module. It's mainly used by the _singleStudentTester_ and should be used by the speicfic tests file per the excercise (e.g _2021a_ex5_tests_)