import argparse
import requests
import json
import base64


def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')

    parser.add_argument('-i', '--input_img', help='input image file', required=True)
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--index', type=str, required=True)
    parser.add_argument('--dataset', type=str, required=True)
    parser.add_argument('--site', type=str, required=True)

    return parser.parse_args()

def imread(path):
    with open(path, 'rb') as img_file:
        encoded_str = base64.b64encode(img_file.read())
    return encoded_str.decode('utf-8')

def init_json(str_img, dataset, site):
    ret_json = {"dtype": "info"}
    ret_json["example_img"] = str_img
    ret_json["dataset"] = dataset
    ret_json["site"] = site
    return ret_json

def post_requests(json_data, url, index):
    str_json = json.dumps(json_data)
    url = "/".join([url, index, '_doc'])

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=str_json, headers=headers)

def main():
    args = get_parser()
    
    str_img = imread(args.input_img)
    json_data = init_json(str_img, args.dataset, args.site)
    response = post_requests(json_data, args.url, args.index)

if __name__=="__main__":
    main()