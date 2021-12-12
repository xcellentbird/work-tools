import os
from os.path import join


cwd = os.getcwd()
print(cwd)
file_list = os.listdir()


add_str = input()
for file_name in file_list:
    if os.path.splitext(file_name)[1] != '.py':
        new_name = add_str + file_name
        os.rename(join(cwd, file_name), join(cwd, new_name))
