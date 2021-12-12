import json
import os
import sys
import argparse
import requests
from os.path import join
from glob import glob
from tqdm import tqdm


WEATHER = ("sunny", "foggy", "rainy")
LIGHT = ("day", "night", "backlight")

def convert_json(vott_json, img_path, country, dataset):
    data_format = dict()
    try:
        asset = vott_json["asset"]
        data_format["dtype"] = "labeling_data"
        data_format["img_name"] = asset["name"]
        data_format["img_path"] = join(img_path, asset["name"])
        img_size = {}
        img_size["width"], img_size["height"] = asset["size"].values()
        data_format["img_size"] = img_size

        objects = []
        weather = ""
        light = ""

        regions = vott_json["regions"]
        for obj in regions:
            obj_name = obj["tags"][0]
            if obj_name in WEATHER:
                weather = obj_name
            elif obj_name in LIGHT:
                light = obj_name
            else:
                bbox = dict()
                bbox["x_min"], bbox["y_min"] = obj["points"][0].values()
                bbox["x_max"], bbox["y_max"] = obj["points"][2].values()
                bbox_size = {"width": obj["boundingBox"]["width"],
                             "height": obj["boundingBox"]["height"]}
                objects.append({"class": obj_name,
                                "bbox": bbox,
                                "bbox_size": bbox_size})
        
        data_format["objects"] = objects
        data_format["object_cnt"] = len(objects)
        data_format["country"] = country
        data_format["dataset"] = dataset
        data_format["site"] = asset["name"][:2]
        data_format["date"] = asset["name"][10:20] + "_" + asset["name"][21:29].replace(".", "-")
        data_format["light"] = light
        data_format["weather"] = weather
        
    except:
        print("wrong format")

    return data_format

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')

    parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=True)
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--index', type=str, required=True)
    parser.add_argument('--img_path', type=str, required=True)
    parser.add_argument('--country', type=str, required=True)
    parser.add_argument('--dataset', type=str, required=True)

    return parser.parse_args()

def load_json(path):
    with open(path, 'r') as f:
        json_data = json.load(f)
    return json_data

def bulk_requests(json_datas, url, index):
    json_head = {"index": {"_index": index, "_id": ""}}
    batch_size = 1000
    batch_cnt = len(json_datas) // batch_size + 1

    data_size = sys.getsizeof(json_datas[:batch_size])
    print("batch_data size: {}".format(data_size))

    for cnt in tqdm(range(batch_cnt)):
        str_jsons = ''
        batch_data = json_datas[cnt*batch_size:(cnt+1)*batch_size]

        for json_data in batch_data:
            doc_id = json_data["img_name"]
            json_head['_id'] = doc_id
            str_json = json.dumps(json_head) + '\n' + json.dumps(json_data) + '\n'

            str_jsons += str_json

        url = "/".join([url, '_bulk'])
        headers = {"Content-Type": "application/json"}
        response = requests.post(url=url, data=str_jsons, headers=headers)
    
    return response

def put_requests(json_data, url, index):
    doc_id = json_data["img_name"]
    str_json = json.dumps(json_data)
    url = "/".join([url, index, '_doc', doc_id])

    headers = {"Content-Type": "application/json"}
    response = requests.put(url, data=str_json, headers=headers)
    
    return response

def main():
    args = get_parser()
    input_dir = args.input_dir

    vott_path = join(input_dir, "**","*.json")
    vott_paths = glob(vott_path, recursive=True)

    custom_jsons = []
    for vott in tqdm(vott_paths):
        vott_json = load_json(vott)
        json_data = convert_json(vott_json, args.img_path, args.country, args.dataset)
        #custom_jsons.append(json_data)
        response = put_requests(json_data, args.url, args.index)

    #bulk_requests(custom_jsons, args.url, args.index)
        #print(response.json())

if __name__=="__main__":
    main()
