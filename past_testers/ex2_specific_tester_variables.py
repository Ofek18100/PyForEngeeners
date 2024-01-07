'''
Python for Engineers 2020-2021 Sem A Ex2
'''
import re
import editdistance

INEXACT_PRINT_CODE = 'J'
INEXACT_CALCULATION_CODE = 'L'

########## Result Checkers ###########
'''
Here you can define custom checker functions that check the result of a single test case.
The checker function should receive the expected result and actual output (as two arguments).
After performing the check, it should return the following:
Return True if the check passes
Return False if fails
Otherwise, can also return a list of special codes (strings) for special comments/failures.
'''

def checkResultQ1(expected, studentOut):
    if expected in studentOut:
        return True

    return False

def checkResultQ2(expected, studentOut):
    p = R'\d+(?:\.\d+)?'
    stud_ans_num = re.findall(p, studentOut)
    if not expected in stud_ans_num:
        return False
    if not "number of strings" in studentOut:
        return False
    return True

def checkResultQ2_old(expected, studentOut):
    expected = "The number of strings longer than the average is: " + expected
    numRes, textRes, editDistance = compareNumsTexts(expected, studentOut)

    if not numRes:
        return False
    if editDistance > 1:
        return INEXACT_PRINT_CODE
    return True

def checkResultQ3(expected, studentOut):
    if not expected in studentOut:
        return False
    return True

def checkResultQ4(expected, studentOut):
    if not expected in studentOut.replace(' ',''):
        return False
    return True

def checkResultQ5(expected, studentOut):
    if not expected[0] in studentOut:
        return False
    if not expected[1] in studentOut:
        return False
    return True

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


class testItem():

    def __init__(self, var_vals_list: list, expected_out, err_code):
        self.var_vals_list = var_vals_list
        self.expected_out = expected_out
        self.err_code = err_code

    def get_err_code(self) -> str:
        return self.err_code

    def get_var_vals_list(self) -> list:
        return self.var_vals_list

    def get_expected(self) -> str:
        return self.expected_out


class QuestionHandler():
    def __init__(self, qnum: int, vars_list: list, test_lists: list, testerFunc) -> None:
        self.qnum = qnum
        self.vars = vars_list
        self.test_list = test_lists
        self.testerFunc = testerFunc

    def get_all_err_codes(self):
        res = ""
        for test_item in self.test_list:
            res += f"{test_item.get_err_code()} "

        return res

    def get_vars(self):
        return self.vars

    def get_qnum(self):
        return self.qnum

    def get_test_list(self):
        return self.test_list

    def get_testerFunc(self):
        return self.testerFunc


############## EX1 Specific variables ##############

NUM_OF_QUESTIONS = 5

# Question 1
Q1a = testItem([[1,2,3,4,5], 3], '2', 'A1')
Q1b = testItem([[1,2,3,4,5], 8], '-1', 'A2')
Q1c = testItem([[2,4,8,16], 16], '3', 'A3')
Q1d = testItem([[],3], '-1', 'A4')
Q1e = testItem([[3],3], '0', 'A5')


Q1_handler = QuestionHandler(1, ['A', 'a'], [Q1a, Q1b, Q1c, Q1d, Q1e], checkResultQ1)

# Question 2
Q2a = testItem([["hello",'world',"course","python","day"]], '2', 'B1')
Q2b = testItem([["hello"]], '0', 'B2')
Q2c = testItem([["hello",'world']], '0', 'B3')
Q2d = testItem([["hello",'world',"course"]], '1', 'B4')
Q2e = testItem([["aaaaaa",'aaaaaa',"aaaaaa","aaaaaa","a"]], '4', 'B5')

Q2_handler = QuestionHandler(2, ['B'], [Q2a, Q2b, Q2c, Q2d, Q2e], checkResultQ2)

# Question 3
Q3a = testItem([[0,1,2,3,4]], '20', 'C1')
Q3b = testItem([[]], '0', 'C2')
Q3c = testItem([[2]], '2', 'C3')
Q3d = testItem([[9,6,0,3]], '54', 'C4')
Q3e = testItem([[3,3,3,3]], '27', 'C5')

Q3_handler = QuestionHandler(3, ['C'], [Q3a, Q3b, Q3c, Q3c, Q3e], checkResultQ3)

# Question 4
Q4a = testItem([[1, 2, 4, 5, 6, 8]], '[1,2,4,8]', 'D1')
Q4b = testItem([[1, 2, 4, 8]], '[1,2,4,8]', 'D2')
Q4c = testItem([[1,3,0]], '[1,3,0]', 'D3')
Q4d = testItem([[2,1]], '[2,1]', 'D4')
Q4e = testItem([[9,8,6,3,2]], '[9,8,6,3]', 'D5')

Q4_handler = QuestionHandler(4, ['D'], [Q4a, Q4b, Q4c, Q4d, Q4e], checkResultQ4)

# Question 5

Q5a = testItem(["abaadddefggg",1], ['1', 'a'], 'E1')
Q5b = testItem(["ab4t3bbb34bbb345bbbb35bbbbbmmmmmm",6], ['6', 'mmmmmm'], 'E2')
Q5c = testItem(["abaadddefggg",3], ['3', 'ddd'], 'E3')
Q5d = testItem(["abcccccd",2], ['2', 'cc'], 'E4')
Q5e = testItem(["abaadddefggg",9], ['9', 'idn'], 'E5')

Q5_handler = QuestionHandler(5, ['my_string', 'k'], [Q5a, Q5b, Q5c, Q5d, Q5e], checkResultQ5)

VARS_list = [['A', 'a'], ['B'], ['C'], ['D'], ['my_string', 'k']]

QHandler_lst = [Q1_handler, Q2_handler, Q3_handler, Q4_handler, Q5_handler]
