from os.path import join
import argparse
import json


def load_json(json_path):
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    return json_data

def save_json(json_data, save_path, no_name=False):
    if no_name:
        file_name = json_data["img_name"]
        save_path = join(save_path, file_name+'.json')
    with open(save_path, 'w') as f:
        json.dump(json_data, f, indent='\t', ensure_ascii=False)
    return save_path

def input_check(input_str):
    yesall_flg = False
    ans = input('{input_str} is right input? [Y/YA/N]')
    if ans.upper() == 'YA':
        yesall_flg = True
    elif ans.upper() == 'N':
        input_str = None
    return input_str, yesall_flg

def get_parser(parsing_contents):
    parser = argparse.ArgumentParser(description='convert setting')
    parser.add_argument('-s', '--gwf', )

    parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=True)
    parser.add_argument('-o', '--output', required=False)
    parser.add_argument('--img_path', required=False)

    return parser.parse_args()