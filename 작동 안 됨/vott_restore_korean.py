import os
import json
import argparse
from glob import glob
from urllib.parse import unquote
import unicodedata


def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas

def write_json(path, json_data):
    with open(path, 'w') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False)

def restore_korean(target, norm=False):
    target = unquote(target)
    if norm:
        target = unicodedata.normalize('NFC', target)
    return target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=True)
    args = parser.parse_args()

    input_dir = args.input_dir

    json_files = glob(f"{input_dir}/**/*.json", recursive=True)
    
    for json_file in json_files:
        json_data = load_json(json_file)
        
        if 'Macintosh' in json_data["asset"]["path"]:
            norm_flg = True

        json_data["asset"]["name"] = restore_korean(json_data["asset"]["name"], norm_flg)
        json_data["asset"]["path"] = restore_korean(json_data["asset"]["path"], norm_flg)

        write_json(json_file, json_data)
        

if __name__ == "__main__":
    main()
