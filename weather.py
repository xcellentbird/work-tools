import os
import argparse
from os.path import join
from glob import glob
from tqdm import tqdm
from collections import Counter
from help_your_review import load_json, save_json



FILTER = {"labeled_date": "2021_12_28"}

def data_parsing():
    pass

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')
    parser.add_argument('-i', '--json', required=False)
    parser.add_argument('-v', '--vott', required=False)
    return parser.parse_args()

def parsing_objects(regions):
    objects = []
    class_cnts = dict()

    for obj in regions:
        obj_name = obj["tags"][0]
        obj_name = obj_name

        if obj_name not in class_cnts:
            class_cnts[obj_name] = 0
        class_cnts[obj_name] += 1

        bbox = dict()
        bbox["x_min"], bbox["y_min"] = obj["points"][0].values()
        bbox["x_max"], bbox["y_max"] = obj["points"][2].values()
        bbox_size = {"width": obj["boundingBox"]["width"],
                        "height": obj["boundingBox"]["height"]}
        objects.append({"class": obj_name,
                        "bbox": bbox,
                        "bbox_size": bbox_size})
    
    return objects, Counter(class_cnts)

def main():
    args = get_parser()
    json_path = args.json
    json_format = join(json_path, '**', '*.json')
    json_files = glob(json_format, recursive=True)

    vott_path = args.vott
    vott_format = join(vott_path, '**', '*.json')
    vott_files = glob(vott_format, recursive=True)

    edit_contents = dict()
    for vott_file in tqdm(vott_files):
        json_data = load_json(vott_file)

        labeled_date = '2021_12_29'
        if '2021_12_30' in vott_file:
            labeled_date = '2021_12_30'

        img_name = json_data["asset"]["name"]
        
        objects, class_cnts = parsing_objects(json_data["regions"])

        edit_contents[img_name] = [objects, class_cnts, labeled_date]
    
    for json_file in tqdm(json_files):
        json_data = load_json(json_file)

        img_name = json_data["img_name"]
        if  img_name in edit_contents:
            json_data["objects"] += edit_contents[img_name][0]
            class_cnts = Counter(json_data["class_cnts"]) + edit_contents[img_name][1]
            json_data["class_cnts"] = dict(class_cnts)
            json_data["labeled_date"] = edit_contents[img_name][2]
            json_data["object_cnt"] = sum(class_cnts.values())

            path = list(os.path.split(json_file))
            path.insert(1, 'pt2')
            save_json(json_data, '\\'.join(path))        

if __name__=="__main__":
    main()