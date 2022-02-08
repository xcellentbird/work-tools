import argparse
import json
import os
import ray
from glob import glob
from tqdm import tqdm
from os.path import join


def check_obj_name(obj_name):
    if obj_name not in PROMISED_CLASS + WEATHER + LIGHT + tuple(RENAME):
        print(f'{obj_name} is not our class')
        rename = input(f'input name to replace {obj_name}')
        RENAME.append(rename)
        return rename
    else:
        return obj_name

def parsing_objects(regions):
    objects = []
    weather = ""
    light = ""
    class_cnts = dict()

    for obj in regions:
        obj_name = obj["tags"][0]
        obj_name = check_obj_name(obj_name)

        if obj_name in WEATHER:
            weather = obj_name
        elif obj_name in LIGHT:
            light = obj_name
        else:
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
    
    return objects, weather, light, class_cnts

def convert_vott(vott_json, labeled_date, change_name=lambda x: x):
    data_format = dict()
    asset = vott_json["asset"]
    new_img_name = change_name(asset["name"])
    country, dataset, site, day, time, _ = new_img_name.split('-')

    date = day + "-" + time
    regions = vott_json["regions"]
    objects, weather, light, class_cnts = parsing_objects(regions)
    img_width, img_height = asset["size"].values()

    data_format["dtype"] = "label"
    data_format["img_name"] = new_img_name
    data_format["img_size"] = {"width": img_width, "height": img_height}
    data_format["objects"] = objects
    data_format["object_cnt"] = len(objects)
    data_format["class_cnts"] = class_cnts
    data_format["country"] = country
    data_format["dataset"] = dataset
    data_format["site"] = site
    data_format["date"] = date
    data_format["light"] = light
    data_format["weather"] = weather
    data_format["labeled_date"] = labeled_date

    return data_format

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')
    parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=True)
    parser.add_argument('-o', '--output', required=True)

    return parser.parse_args()

def load_json(json_path):
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    return json_data

def save_json(json_data, save_path):
    file_name = json_data["img_name"]
    with open(join(save_path, file_name+'.json'), 'w') as f:
        json.dump(json_data, f, indent='\t', ensure_ascii=False)

def main():
    args = get_parser()
    input_dir = args.input_dir
    save_path = args.output

    vott_path = join(input_dir, "**","*.json")
    vott_paths = glob(vott_path, recursive=True)

    for vott_file in tqdm(vott_paths):
        vott_json = load_json(vott_file)
        labeled_date = vott_file.split(os.path.sep)[-3][4:].replace('-', '_')
        json_data = convert_vott(vott_json, labeled_date)
        save_json(json_data, save_path)

if __name__=="__main__":
    main()