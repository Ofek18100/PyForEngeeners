''' Exercise #9. Python for Engineers.'''

import numpy as np
import imageio
import matplotlib.pyplot as plt


#########################################
# Question 2 - do not delete this comment
#########################################

def load_training_data(weights_file, heights_file):
    with open(weights_file, 'r') as f:
        data = []
        row_names = []
        for line in f:
            data_to_add = line.strip().split(',')
            data.append(data_to_add[1:])
            row_names.append(data_to_add[0])
    column_names = np.array(data[0])
    data = np.array(data[1:]).astype('float')
    row_names = np.array(row_names[1:])
    weights_data={"data": data, "column_names": column_names, "row_names": row_names}
    with open(heights_file, 'r') as f:
        heights_data ={}
        for i, line in enumerate(f):
            if i==0: continue
            data_to_add= line.strip().split(',')
            heights_data[data_to_add[0]]=float(data_to_add[1])
    return weights_data, heights_data


def get_highest_weight_loss(data_dict):
    row_names = data_dict["row_names"]
    data = data_dict["data"]
    return row_names[np.argmax((data[:, 0] - data[:, -1]))]


def get_bmi(weights_data, heights_data):
    n_rows = weights_data["row_names"].shape[0]
    n_cols = weights_data["column_names"].shape[0]
    xx, yy = np.meshgrid(np.arange(n_rows), np.arange(n_cols))
    return np.apply_along_axis(
        lambda a: round(weights_data["data"][a[0], a[1]] / (heights_data[weights_data["row_names"][a[0]]] / 100) ** 2, 2),
        1,
        np.dstack((xx.flatten(), yy.flatten()))[0]
    ).reshape((n_cols, n_rows)).T


def get_bmi_diff(weights_data, heights_data):
    return np.diff(get_bmi(weights_data, heights_data))


def get_highest_bmi_loss_month(weights_data, heights_data):
    column_names = weights_data["column_names"]
    return column_names[np.argmax(np.sum(get_bmi_diff(weights_data, heights_data), axis=0) * (-1.0)) + 1]


#########################################
# Question 3 - do not delete this comment
#########################################

def load_image_as_matrix(img_path):
    print(f'mat.shape of {img_path}: {imageio.imread(img_path).shape}')
    return imageio.imread(img_path)


def binarize_matrix(mat):
    dup_mat = np.zeros(mat.shape)
    dup_mat[mat >= 128] = 1
    return dup_mat


def compress_flatten_rle(mat):
    pixels = mat.flatten()
    pixels = np.concatenate([[0], pixels, [9]])
    runs = np.where(pixels[1:] != pixels[:-1])[0]
    runs[1:] -= runs[:-1]
    runs = (runs if runs.size != 0 else np.array([mat.size]))
    return runs, mat.shape


def decompress_flatten_rle(mat_rle_compressed, shape):
    is_one = False
    pos = 0
    mat_rle_decompressed = np.zeros(shape[0] * shape[1])
    for count in mat_rle_compressed:
        if is_one:
            mat_rle_decompressed[pos:pos + count] = 1
        pos = pos + count
        is_one = not is_one
    return mat_rle_decompressed.reshape(shape)


def calc_compression_ratio(mat_rle_compressed, mat):
    return round(mat_rle_compressed.size / mat.size, 2)

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
