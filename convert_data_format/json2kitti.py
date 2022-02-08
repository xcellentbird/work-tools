import os
import argparse
import json
from os.path import join
from glob import glob
from tqdm import tqdm


TARGET_SIZE = (960, 544)

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')

    parser.add_argument('-i', '--input_dir', required=True)
    parser.add_argument('-o', '--output_dir', required=True)

    return parser.parse_args()

def load_json(path):
    with open(path, 'r') as f:
        json_data = json.load(f)
    return json_data

def write_kitti(data, path):
    with open(path, 'w') as f:
        f.writelines(data)

def make_KITTI_format(bbox, object_class, size, t_size):
    # useless values
    truncated = 0
    occlusion = 3
    alpha = -1
    dimension_3d = [-1, -1, -1]
    location_3d = [-1, -1, -1]
    rotation_y = -1
    
    # make KITTI format
    bbox_format = f"{bbox[0]*t_size[0]//size[0]} {bbox[1]*t_size[1]//size[1]} {bbox[2]*t_size[0]//size[0]} {bbox[3]*t_size[1]//size[1]}"
    dimension_3d_format = f"{dimension_3d[0]} {dimension_3d[1]} {dimension_3d[2]}"
    location_3d_format = f"{location_3d[0]} {location_3d[1]} {location_3d[2]}"

    kitti_label = f"{object_class} {truncated} {occlusion} {alpha} {bbox_format} {dimension_3d_format} {location_3d_format} {rotation_y}\n"

    return kitti_label

def edit_ext(file, ext):
    name, _ = os.path.splitext(file)
    if '.' not in ext:
        ext = '.' + ext
    return name + ext

def convert_to_kitti(json_data):
    objects = json_data["objects"]
    img_size = json_data["img_size"].values()
    file_name = json_data["img_name"]
    file_name = edit_ext(file_name, 'txt')
    
    kitti_data = []
    for obj in objects:
        object_class = obj["class"]
        bbox = [int(ax) for ax in obj["bbox"].values()]

        line = make_KITTI_format(bbox, object_class, list(img_size), TARGET_SIZE)
        kitti_data.append(line)
        
    return kitti_data, file_name

def main():
    args = get_parser()
    input_dir = args.input_dir
    output_dir = args.output_dir

    json_path_format = join(input_dir, '**', '*.json')
    json_paths = glob(json_path_format, recursive=True)

    for json_path in tqdm(json_paths):
        json_data = load_json(json_path)

        kitti_data, file_name = convert_to_kitti(json_data)
        save_path = join(output_dir, file_name)
        write_kitti(kitti_data, save_path)

if __name__=='__main__':
    main()



