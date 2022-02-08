import argparse
import json
import os
from os.path import join
from glob import glob
from pprint import pprint


def load_txt(path):
    with open(path, 'r') as f:
        datas = f.readlines()
    return datas


def main():
    input_dir = os.getcwd()

    kitti_list = glob(f'{input_dir}/**/*.txt', recursive=True)
    print(len(kitti_list))

    object_cnt = dict()
    
    for kitti_file in kitti_list:
        label_data = load_txt(kitti_file)

        for label in label_data:
            obj = label.split()[0]

            if obj not in object_cnt:
                object_cnt[obj] = 0
            object_cnt[obj] += 1
    
    print(object_cnt)
    print("total_object :", sum(object_cnt.values()))
    

if __name__ == "__main__":
    main()
