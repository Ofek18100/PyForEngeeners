''' Exercise #9. Python for Engineers.'''

import numpy as np
import imageio
import matplotlib.pyplot as plt


#########################################
# Question 2 - do not delete this comment
#########################################

def load_training_data(filename):
    with open(filename, 'r') as f:
        data = []
        row_names = []
        for line in f:
            data_to_add = line.strip().split(',')
            data.append(data_to_add[1:])
            row_names.append(data_to_add[0])
    column_names = np.array(data[0])
    data = np.array(data[1:]).astype('float')
    row_names = np.array(row_names[1:])
    return {"data": data, "column_names": column_names, "row_names": row_names}


def get_highest_weight_loss_trainee(data_dict):
    row_names = data_dict["row_names"]
    data = data_dict["data"]
    return row_names[np.argmax((data[:, 0] - data[:, -1]))]


def get_diff_data(data_dict):
    data = data_dict["data"]
    return np.diff(data)


def get_highest_loss_month(data_dict):
    column_names = data_dict["column_names"]
    return column_names[np.argmax(np.sum(get_diff_data(data_dict), axis=0)*(-1.0)) + 1]


def get_relative_diff_table(data_dict):
    data = data_dict["data"]
    return get_diff_data(data_dict)/data[:, :-1]


#########################################
# Question 3 - do not delete this comment
#########################################

def compute_entropy(img):
    image_pixels = imageio.imread(img).flatten()
    bin_prob = np.bincount(image_pixels)/(image_pixels.shape[0])
    prob_values = (-1.0)*bin_prob
    bin_prob[bin_prob==0]=1.0
    return (prob_values*np.log2(bin_prob)).sum()


def nearest_enlarge(img, a):
    img = imageio.imread(img)
    big_y, big_x = img.shape[0]*a, img.shape[1]*a
    big_image = np.zeros((big_y, big_x), dtype='int')
    a_fac = 1/a
    for i in range(big_image.shape[0]):
        for j in range(big_image.shape[1]):
            big_image[i,j] = img[np.floor(i*a_fac).astype(int), np.floor(j*a_fac).astype(int)]
    return big_image

#########################################
# Question 1 - do not delete this comment
#########################################

class Roman():
    def __init__(self, input_value):
        if isinstance(input_value, int):
            self.is_neg = input_value < 0
            self.int_value = input_value
            self.roman_value = self.get_roman_from_int()
        else:
            self.is_neg = '-' in input_value
            self.roman_value = input_value.upper()
            self.int_value = self.get_int_from_roman()       
        
        
    def get_int_from_roman(self):
        rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        roman_string = self.roman_value.strip('-')
        int_val = 0
        for counter in range(len(roman_string)):
            if counter > 0 and rom_val[roman_string[counter]] > rom_val[roman_string[counter - 1]]:
                int_val += rom_val[roman_string[counter]] - 2 * rom_val[roman_string[counter - 1]]
            else:
                int_val += rom_val[roman_string[counter]]
        int_val = -int_val if self.is_neg else int_val
        return int_val
    
    def get_roman_from_int(self):
        num = self.int_value if not self.is_neg else -self.int_value
        roman_num = '' if not self.is_neg else '-'
        counter = 0
        
        roman_char = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        int_vals = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        
        while num > 0:
            for _ in range(num // int_vals[counter]):
                roman_num += roman_char[counter]
                num -= int_vals[counter]
            counter += 1
        return roman_num
    
    
    def __str__(self):
        return "The integer value is {} and the Roman Numeral is denoted by \'{}\'".format(str(self.int_value), self.roman_value)
    
    def __repr__(self):
        return self.roman_value
    
    def __add__(self, other):
        if not isinstance(other, Roman):
            other = Roman(other)
        int_value = self.int_value + other.int_value
        if int_value == 0:
            raise ValueError("unsupported addition result")

        return Roman(int_value)
    
    def __lt__(self, other):
        if not isinstance(other, Roman):
            other = Roman(other)
        return self.int_value < other.int_value
    
    def __gt__(self, other):
        if not isinstance(other, Roman):
            other = Roman(other)
        return self.int_value > other.int_value
    
    def __neg__(self):
        return Roman(-self.int_value)
        
    def __floordiv__(self, other):
        if not isinstance(other, Roman):
            other = Roman(other)
        floor_division = self.int_value // other.int_value
        if floor_division == 0:
            raise ValueError("unsupported division result")
        return Roman(self.int_value // other.int_value)
    
if __name__ == '__main__':
    print(Roman(2))
    print(repr(Roman(2)))
    print(-Roman("IV"))
    r = Roman(2) + 3
    print(repr(r))
