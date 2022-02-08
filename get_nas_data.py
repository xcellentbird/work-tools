import os
import sys
import subprocess
from os.path import split, join
from pprint import pprint

# pip가 없으면 pip를 설치한다.
try:
    import pip
except ImportError:
    print("Install pip for python3")
    subprocess.call(['sudo', 'apt-get', 'install', 'python3-pip'])

# argparse가 없으면 argparse를 설치한다.
try:
    import argparse
except ModuleNotFoundError:
    print("Install argparse in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'argparse'])
finally:
    import argparse

try:
    import paramiko
except ModuleNotFoundError:
    print("Install paramiko in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'paramiko'])
finally:
    import paramiko

try:
    import pandas as pd
except ModuleNotFoundError:
    print("Install pandas in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'pandas'])
finally:
    import pandas as pd

try:
    import PIL.Image as Image
except ModuleNotFoundError:
    print("Install pillow in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'pillow'])
finally:
    import PIL.Image as Image

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("Install tqdm in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'tqdm'])
finally:
    from tqdm import tqdm

ADDRESS = '14.63.1.76'
USERNAME = 'Nota-its'
PASSWORD = "Nota180928!!"
PORT = 5052

TARGET_SIZE = (960, 544)

NUM_SHOW_FAILED = 100


def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')

    parser.add_argument('-i', '--input_csv', help='input parents file directory.', required=True)
    parser.add_argument('-o', '--output_dir', required=True)

    return parser.parse_args()

def set_sftp_connect(username, address, port, password):
    global USERNAME, ADDRESS, PORT, PASSWORD
    USERNAME = username
    ADDRESS = address
    PORT = port
    PASSWORD = password

def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        data_paths = f.readlines()
    return data_paths[1:]

def show_get_result(get_failed, num_show):
    if not get_failed:
        print('all success!!')
    else:
        num_failed = len(get_failed)

        print(f'{num_failed} failed... ')
        pprint(get_failed[:num_show])
        if num_failed > num_show:
            print('...more')

def sftp_get(file_paths: list, output_dir: str)->list:
    '''
    - 설정된 SFTP 서버에서 file_paths 파일들을 output_dir로 다운로드합니다.\n
    - 실패한 file_paths를 반환합니다.\n
    - ex) file_path: ["Nota-its/dataset3/file1_name.ext", "Nota-its/dataset1/file4_name.ext"]
    - ex) output_dir: "D:/Users/folder/"
    '''
    get_failed = []
    successed = []
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(ADDRESS, username=USERNAME, password=PASSWORD, port=PORT)
        print('ssh connected')
    
        with ssh.open_sftp() as sftp:
            print('sftp connected')
    
            for file_path in tqdm(file_paths):
                file_name = split(file_path)[1]
                try:
                    sftp.get(file_path, join(output_dir, file_name))
                    successed.append(join(output_dir, file_name))
                except:
                    get_failed.append(file_path)
    return successed, get_failed

def inner_nas_path(img_name):
    country, dataset, site, date, index_with_ext = img_name.split('_')

    return f'/Nota-its/data/traffic/{dataset}/image/{img_name}'

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

def series_to_list(series):
    return series.replace(',', '').split(' ')

def edit_ext(file, ext):
    name, _ = os.path.splitext(file)
    if '.' not in ext:
        ext = '.' + ext
    return name + ext

def write_kitti(data, path):
    with open(path, 'w') as f:
        f.writelines(data)

def df_to_kitti(df, output_dir):
    for i in range(len(df)):
        img_name = df["img_name"][i]
        img_width = int(df["img_size.width"][i].replace(',', ''))
        img_height = int(df["img_size.height"][i].replace(',', ''))
        size = [img_width, img_height]
        objects_class = series_to_list(df["objects.class"][i])
        xmins = series_to_list(df["objects.bbox.x_min"][i])
        ymins = series_to_list(df["objects.bbox.y_min"][i])
        xmaxs = series_to_list(df["objects.bbox.x_max"][i])
        ymaxs = series_to_list(df["objects.bbox.y_max"][i])

        kitti_data = []
        for object_class, xmin, ymin, xmax, ymax in zip(objects_class, xmins, ymins, xmaxs, ymaxs):
            try:
                bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]
            except:
                print(objects_class, xmin, ymin, xmax, ymax)
                break
            line = make_KITTI_format(bbox, object_class, size, TARGET_SIZE)
            kitti_data.append(line)

        file_name = edit_ext(img_name, 'txt')
        save_path = join(output_dir, file_name)
        write_kitti(kitti_data, save_path)

def main():
    args = get_parser()
    input_csv = args.input_csv
    output_dir = args.output_dir

    img_outpath = join(output_dir, 'img')
    label_outpath = join(output_dir, 'label')
    os.makedirs(img_outpath, exist_ok=True)
    os.makedirs(label_outpath, exist_ok=True)

    df = pd.read_csv(input_csv)
    df_to_kitti(df, label_outpath)
    
    img_paths = list(df["img_name"].map(inner_nas_path))
    success, failed = sftp_get(img_paths, img_outpath)

    for img_path in tqdm(success):
        img = Image.open(img_path)
        img = img.resize((TARGET_SIZE[0], TARGET_SIZE[1]))
        img.save(img_path, subsampling=-1)
    show_get_result(failed, NUM_SHOW_FAILED)
    

if __name__=="__main__":
    main()