import pandas as pd

import matplotlib.pyplot as plt
import imageio
import numpy as np
#Q1
#-----------------------------------------------------------------------------
def arr_dist(a1, a2):
    return abs(np.int_(a1) - np.int_(a2)).sum()

#-----------------------------------------------------------------------------
def np_array_to_ascii(darr):
    return ''.join([chr(item) for item in darr])

#-----------------------------------------------------------------------------
def ascii_to_np_array(s):
    return np.frombuffer(s.encode(), dtype=np.uint8)

#-----------------------------------------------------------------------------
def put_message(im, msg):
    np_msg = ascii_to_np_array(msg)
    img_idx = find_best_place(im, np_msg)
    im1 = create_image_with_msg(im, img_idx, np_msg)
    return im1

#-----------------------------------------------------------------------------
def find_best_place(im, np_msg):
    r, c = im.shape
    min_idx = 0
    min_dist = 100000
    m = min(r,256)
    n = min(c - len(np_msg) + 1, 256)
    for i in range(m):
        for j in range(n):
            if i == 0 and j < 3:
                #Preserve 3 bytes for the meta-data
                continue
            curr_dist = arr_dist(im[i:i+1, j:j+len(np_msg)][0], np_msg)
            if min_dist >= curr_dist:
                min_dist = curr_dist
                min_idx = (i,j)
    return min_idx

#-----------------------------------------------------------------------------
def create_image_with_msg(im, img_idx, np_msg):
    im1 = im.copy()
    im1[img_idx[0]:img_idx[0]+1, img_idx[1]:img_idx[1]+len(np_msg)] = np_msg
    im1[0][0] = img_idx[0]
    im1[0][1] = img_idx[1]
    im1[0][2] = len(np_msg)
    return im1

#-----------------------------------------------------------------------------
def get_message(im):
    l = im[0][2]
    r = im[0][0]
    c = im[0][1]
    np_msg = im[r:r+1, c:c+l]
    msg = np_array_to_ascii(np_msg[0])
    return msg
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

#Q2
def read_missions_file(file_name):
    try:
        bounties = pd.read_csv(file_name, index_col="Kingdom")
    except IOError:
        raise IOError("An IO error occurred")
    return bounties
#-----------------------------------------------------------------------------
def add_daily_gain_col(bounties):
    bounties["daily gain"] = bounties.apply(lambda row: (row["Bounty"] - row["Expenses"])/row["Duration"], axis = 1)
#-----------------------------------------------------------------------------
def sum_rewards(bounties):
    return (bounties["Bounty"] - bounties["Expenses"]).sum()
#-----------------------------------------------------------------------------

def find_best_kingdom(bounties):
    add_daily_gain_col(bounties)
    return bounties["daily gain"].idxmax()
#-----------------------------------------------------------------------------
def find_best_duration(bounties):
    add_daily_gain_col(bounties)
    bestlength = bounties.groupby(["Duration"])["daily gain"].mean().idxmax()
    return bestlength

df = read_missions_file('/Users/d_private/Documents/PyProgs/2021b/ex10/245sources/missions.csv')
df = read_missions_file('/Users/d_private/Documents/PyProgs/2021b/ex10/sources/missions.csv')
print(df)
add_daily_gain_col(df)
print(df)

print(sum_rewards(df))
print(find_best_kingdom(df))