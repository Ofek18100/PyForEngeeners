import os
import glob


def extract(path):
    folders_list = os.listdir(path)
    for folder in folders_list:
        f = glob.glob(os.path.join(path, folder, "*.*"))[0]
        os.rename(f, os.path.join(path, folder + ".py"))
        os.rmdir(os.path.join(path, folder))


extract(r"C:\Users\Yuval\Desktop\aaa")
