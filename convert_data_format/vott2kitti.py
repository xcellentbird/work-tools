import argparse  
import json
import os
from os.path import join, basename, dirname
from glob import glob
from tqdm import tqdm
import PIL.Image as Image

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


def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas


def print_total_objects(total_label):
    total_str = ''
    for label_name in total_label:
        total_str += f"{label_name} is total {total_label[label_name]} \n"
    print(total_str)


def main():
    parser = argparse.ArgumentParser(description='convert setting')
    
    # input, output dirrectory setting
    parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=True)
    parser.add_argument('-o', '--output_dir', help='output ".txt" file directory.', required=True)
    
    parser.add_argument('-f', '--filtering', help='filtering(remove) label whose center y is lower than f_value.', default=None, type=float)
    parser.add_argument('-r', '--resize', help='resize image width and height.', default=None, nargs=2)
    parser.add_argument('--delete_label', help='The label do not want to transform.', default=None, nargs='*')
    parser.add_argument('--replace_labels', help='Some labels will be replaced to dictionary key. input json path. ex) {motorcycle:two-wheeler, bicycle:two-wheeler}',default=None, type=str)
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(join(output_dir,'img'), exist_ok=True)
    os.makedirs(join(output_dir,'label'), exist_ok=True)
    target_size = list(map(int,args.resize))
    if args.replace_labels is not None:
        replace_json = load_json(args.replace_labels)
    else:
        replace_json={}
    total_label = {}

    json_list = glob(f'{input_dir}/**/*.json', recursive=True)

    del_list = ['sunny', 'day', 'night', 'rainy', 'snow', 'foggy', 'snowy', 'blacklight', 'backlight']
    
    for json_file in tqdm(json_list):
        img_path = dirname(json_file).replace('json','img')
        label_data = load_json(json_file)
        img_name = label_data['asset']['name']
        label_file_name = img_name.replace('jpg','txt').replace('png','txt')
        
        # add road info for road
        line = ''
        ## img-resize
        try:
            img = Image.open(join(img_path, img_name))
            size = img.size
            img = img.resize((target_size[0], target_size[1]))
            img.save(join(output_dir, 'img', img_name).replace('png','jpg'), subsampling=-1)

            for data in label_data['regions']:
                object_class = data['tags'][0]
                if args.delete_label is not None and object_class in args.delete_label:
                    continue
                elif object_class in replace_json:
                    object_class = replace_json[object_class]

                if object_class not in total_label:
                    total_label.update({object_class:1})
                else:
                    total_label[object_class] = total_label[object_class] + 1

                # data['points'][0:4] : left top, right top, right bottom, leftbottom
                bbox = [int(data['points'][0]['x']), int(data['points'][0]['y']), int(data['points'][2]['x']), int(data['points'][2]['y'])]

                if (args.filtering is not None) and ((bbox[1] + bbox[3]) / 2) < args.filtering:
                    continue

                if object_class not in del_list:
                    line += make_KITTI_format(bbox, object_class, size, target_size)


            f = open(join(output_dir, 'label', label_file_name), 'w')
            f.write(line)
            f.close()
        except FileNotFoundError:
            print("There is No Image File : ",img_name)
    
    print_total_objects(total_label)
    
if __name__ == "__main__":
    main()
