import argparse
from PIL import Image
from os.path import join, split
from tqdm import tqdm
from glob import glob

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')

    parser.add_argument('-i', '--input_dir', required=True)
    parser.add_argument('-o', '--output_dir', required=True)
    parser.add_argument('-t', '--target_size', default=(960, 544))

    return parser.parse_args()

def img_resizer(img, t_size):
    img = img.resize((t_size[0], t_size[1]))
    return img

def main():
    args = get_parser()
    input_dir = args.input_dir
    output_dir = args.output_dir
    t_size = args.target_size

    img_path_format = join(input_dir, '**', '*.jpg')
    img_paths = glob(img_path_format, recursive=True)

    for img_path in tqdm(img_paths):
        img = Image.open(img_path)
        img = img_resizer(img, t_size)

        img_name = split(img_path)[1]
        img.save(join(output_dir, img_name))

if __name__=="__main__":
    main()