''' Exercise #4. Python for Engineers.'''


#########################################
# Question 1 - do not delete this comment
#########################################
from copy import deepcopy


def least_popular_character(my_string):
    """Returns the second's most common letter in a string"""
    alphaDict = { char:(my_string.count(char)) for char in my_string }
    common_val = min(alphaDict.values())
    mult_common_letters = []
    for char, val in alphaDict.items():
        if val==common_val:
            mult_common_letters.append(char)
    mult_common_letters.sort()
    return(' '.join(mult_common_letters))



#########################################
# Question 2 - do not delete this comment
#########################################
def mult_sparse_matrices(lst):
    result_keys = lst[0].keys()
    
    # get only repeating keys, others will be nullified
    for mat in lst:
        result_keys &= mat.keys()
    
    # multiply
    result = {key: 1 for key in result_keys}
    for mat in lst:
        for tup in result_keys:
            result[tup] *= mat[tup]


    result = {key: value for (key, value) in result.items() if value != 0  }

    return result



#########################################
# Question 3 - do not delete this comment
#########################################
def fill_substring_dict(s, d, k):
    for i in range(len(s)):
        for j in range(k):
            key = s[i:i+j+1]
            if key in d.keys():
                d[key].append(i)

    return d

                

#########################################
# Question 4 - do not delete this comment
#########################################
def courses_per_student(tuples_lst):
    courses_per_student_dict = {}
    for tup in tuples_lst:
        stud_name = tup[0].lower()
        course = tup[1].lower()
        if not (stud_name in courses_per_student_dict):
            courses_per_student_dict[stud_name] = [course]
        else:
            courses_per_student_dict[stud_name].append(course)
    return(courses_per_student_dict)    


def num_courses_per_student(stud_dict):
    for key in stud_dict.keys():
        stud_dict[key] = len(stud_dict[key])


#########################
# main code - do not delete this comment
# Tests have been added for your convenience.
# You can add more tests below.
#########################

# Q1
print(least_popular_character('aabbAA') == 'A a b')

cases = ['z', 'CCbccccbbb', 'CCaaZZ']
for case in cases:
    print(case)
    print(least_popular_character(case))


# Q2
print(mult_sparse_matrices([{(1, 3): 2, (2, 7): 1}, {(1, 3): 6}]) == {(1, 3): 12})
# Sparse Matrcies
M1 = {(1, 1): 1}
M2 = {}
M3 = {(1, 1): 2, (5, 5): -5, (5, 4): 2}
M4 = {(1, 1): -1, (2, 2): 1}
M5 = {(5, 5): -1, (5, 4): 2}

cases = [[deepcopy(M1), deepcopy(M1)],
         [deepcopy(M1), deepcopy(M2), deepcopy(M1)],
         [deepcopy(M4), deepcopy(M3)],
         [deepcopy(M2), deepcopy(M2)],
         [deepcopy(M1), deepcopy(M2), deepcopy(M5), deepcopy(M1)]]

for case in cases:
    print(case)
    print(mult_sparse_matrices(case))


# Q3
# print(find_substring_locations('TTAATTAGGGGCGC', 2) == {'TT': [0, 4], 'TA': [1, 5], 'AA': [2], 'AT': [3], 'AG': [6], 'GG': [7, 8, 9], 'GC': [10, 12], 'CG': [11]})

cases = [('wholoveswholegrain', {'who': [], 'Love': []}, 3),
         ('wholoveswholegrain', {'who': [], 'Love': []}, 2),
         ('bbbbbbb', {'b': []}, 4),
         ('TTAATTAGGCGCTA', {'TA': [], 'G': [], 'K': [], 'TTAA': [], 'tat': [], 'TTA': []}, 3),
         ]

for case in cases:
    print(case)
    print(fill_substring_dict(*case))

# ============================== END OF FILE =================================