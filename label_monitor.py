import argparse
import json
import os
from os.path import join
from glob import glob
from pprint import pprint


multi_label_flg = True
catch_labels = ['blacklight']


def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas


def main():
    input_dir = os.getcwd()
    #input_dir = input_dir.replace('\\', '/')

    json_list = glob(f'{input_dir}/**/*.json', recursive=True)
    print(len(json_list))
    json_list.sort()

    labels = dict()
    multi_labels = []
    catch = []
    
    for json_file in json_list:
        label_data = load_json(json_file)

        for obj in label_data["regions"]:
            tags = obj["tags"]
            if multi_label_flg and len(tags) > 1:
                multi_labels.append([json_file.split('\\')[-3], label_data["asset"]["name"], tags])
            else:
                if tags[0] not in labels:
                    labels[tags[0]] = 1
                else:
                    labels[tags[0]] += 1

            if set(catch_labels) & set(tags):
                catch.append([json_file.split('\\')[-3], label_data["asset"]["name"], tags])
                
        
        """
        flg = False
        lines = []
        with open(json_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if '"night",' in line:
                    flg = True
                    del lines[i+1]
                    lines[i] = lines[i].replace('"night",', '"night"')
                if '"sunny",' in line:
                    flg = True
                    del lines[i+1]
                    lines[i] = lines[i].replace('"sunny",', '"sunny"')
                    
                    

        if flg:
            with open(json_file, 'w') as f:
                f.writelines(lines)
        """

    
    multi_labels.sort()
    catch.sort()

    print('multi label list')
    pprint(multi_labels)

    print('catch label list')
    pprint(catch)
    print(labels) 
        
    

if __name__ == "__main__":
    main()
