import argparse
from os import listdir
from os.path import join

parser = argparse.ArgumentParser(description='convert setting')
    
parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=True)
parser.add_argument('-o', '--output_dir', help='output ".txt" file directory.', required=True)
        
args = parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir

kitti_list = listdir(input_dir)

del_list = ['sunny', 'day', 'night', 'rainy', 'snow', 'foggy', 'snowy', 'blacklight', 'backlight', 'personal_mobility', 'hdv', 'hdv_back', 'bicycle']

for kitti in kitti_list:
    kitti_path = join(input_dir, kitti)

    lines = []
    with open(kitti_path, 'r') as f:
        for l in f.readlines():
            for dl in del_list:
                if dl in l:
                    break
            else:
                lines.append(l)

    output_path = join(output_dir, kitti)
    with open(output_path, 'w') as f:
        f.writelines(lines)
    
