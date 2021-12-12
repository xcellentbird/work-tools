#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zipfile import ZipFile
from glob import glob
from tqdm import tqdm
from os import path


d = "D:\다운로드\monitoring\yangsan_traffic\송채연05"
print(path.split(d))

input_dir = "D:\다운로드\monitoring\yangsan_traffic"
output_dir = "D:\다운로드\monitoring\yangsan_"

zip_list = glob(path.join(input_dir, '**','*.zip'))
print(len(zip_list))

for z in tqdm(zip_list):
    output_path = path.split(z)[0]
    ZipFile(z).extractall(output_path)
