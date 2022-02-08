import argparse
import json
import os
from os.path import join
from glob import glob
from pprint import pprint


weather = ['sunny', 'rainy', 'snow', 'snowy', 'foggy']
light = ['day', 'night', 'backlight']

multi_label_flg = True


def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas


def main():
    input_dir = os.getcwd()

    json_list = glob(f'{input_dir}/**/*.json', recursive=True)
    print(len(json_list))

    labels = {'vehicle':{}, 'weather':{k:0 for k in weather}, 'light':{k:0 for k in light}}
    multi_labels = []
    no_labels = []
    
    for json_file in json_list:
        label_data = load_json(json_file)

        label_cnt = 0
        print(list(label_data.keys()))
        for obj in label_data["regions"]:
            tag = obj["tags"][0]
            if tag in weather + light:
                continue
            label_cnt += 1

        if not label_cnt:
            no_labels.append([json_file.split('\\')[-3], label_data["asset"]["name"]])

        for obj in label_data["regions"]:
            tags = obj["tags"]
            if multi_label_flg and len(tags) > 1:
                multi_labels.append([json_file.split('\\')[-3], label_data["asset"]["name"], tags])
            else:
                tag = tags[0]
                if tag in weather:
                    labels['weather'][tag] += 1
                elif tag in light:
                    labels['light'][tag] += 1
                else:
                    if tag not in labels['vehicle']:
                        labels['vehicle'][tag] = 0
                    labels['vehicle'][tag] += 1
                
    
    multi_labels.sort()

    print('no label list')
    no_labels.sort()
    pprint(no_labels)

    print('multi label list')
    pprint(multi_labels)

    pprint(labels)
    print('total vehicle')
    print(sum(labels['vehicle'].values()))

    os.system('pause')
    

if __name__ == "__main__":
    main()
