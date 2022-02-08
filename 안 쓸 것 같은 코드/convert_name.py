import os
from os.path import join
from pprint import pprint


cwd = os.getcwd()
file_list = os.listdir(cwd)
print("now:", cwd)

pprint(file_list)
for f in file_list:
    if f[-2:] != 'py':
        date, _ = f.split('_')
        yyyy, mm, dd, hh, minute, sec = date[0:4], date[4:6], date[6:8], date[8:10], date[10:12], '00'
        day = '_'.join([yyyy, mm, dd])
        time = '_'.join([hh, minute, sec])
        new_name = '-'.join(['korea','daejeon', 'YS_OC', day, time+'.avi'])
        os.rename(join(cwd, f), join(new_name))
