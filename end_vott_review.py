import os
import argparse
import paramiko
import json
import requests
from time import strptime
from os.path import join, split
from zipfile import ZipFile
from glob import glob
from tqdm import tqdm
from datetime import date
from datetime import datetime


CLASS_FILE_NAME = 'class_list.txt'
CONFIG_FILE_NAME = 'end_vott_review_config.txt'

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')
    parser.add_argument('-i', '--input_dir', help='input parents file directory.', required=False, default=os.getcwd())
    return parser.parse_args()

class NAS_client:
    '''
    사용법 \n
    get이나 put에는 데이터와 경로를 함께 넣어야합니다. \n
    NAS의 home 경로는 ssh 접속 기준 /volume1/입니다. \n
    경로 구분은 '/'입니다. \n
    ex) 'Nota-its/its/data/traffic/daejeon/video/<video_name>.mp4'
    ex) 'C:/ptits/img/<image_name>.jpg'
    '''
    def __init__(self, hostname, username, password, port):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password, port=self.port)
        print('ssh connected')
        self.sftp = self.ssh.open_sftp()
        print('sftp connected')

    def __enter__(self):
        return self.sftp

    def __exit__(self, type, value, traceback):
        self.sftp.close()
        print('sftp closed')
        self.ssh.close()
        print('ssh closed')

def load_json(json_path):
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    return json_data

def save_json(json_data, save_path):
    with open(save_path, 'w') as f:
        json.dump(json_data, f, indent='\t', ensure_ascii=False)
    return save_path

def get_config():
    cfg_path = join(os.getcwd(), CONFIG_FILE_NAME)
    cfg = load_json(cfg_path)
    return cfg

def get_class_list():
    list_dir = join(os.getcwd(), CLASS_FILE_NAME)
    class_list = load_json(list_dir)
    return class_list

def post_requests(json_data, url, index):
    doc_id = json_data["img_name"]
    str_json = json.dumps(json_data)
    url = "/".join([url, index, '_doc', doc_id])

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=str_json, headers=headers)
    
    return response

def get_bbox(obj):
    bbox = dict()
    bbox["x_min"], bbox["y_min"] = obj["points"][0].values()
    bbox["x_max"], bbox["y_max"] = obj["points"][2].values()
    bbox_size = {"width": obj["boundingBox"]["width"],
                 "height": obj["boundingBox"]["height"]}
    return bbox, bbox_size

def parsing_objects(regions):
    objects = []
    weather = ""
    light = ""
    class_cnts = dict()

    class_list = get_class_list()
    main_class = class_list["main"]
    weather_class = class_list["weather"]
    light_class = class_list["light"]

    for obj in regions:
        obj_name = obj["tags"][0]

        if obj_name in weather_class:
            weather = obj_name
        elif obj_name in light_class:
            light = obj_name
        elif obj_name in main_class:
            if obj_name not in class_cnts:
                class_cnts[obj_name] = 0
            class_cnts[obj_name] += 1

            bbox, bbox_size = get_bbox(obj)
            objects.append({"class": obj_name,
                            "bbox": bbox,
                            "bbox_size": bbox_size})
        else:
            print(obj_name, 'is wrong class')
    
    return objects, weather, light, class_cnts

def convert_vott(vott_json, labeled_date, change_name=lambda x: x):
    data_format = dict()
    asset = vott_json["asset"]
    new_img_name = change_name(asset["name"])
    country, dataset, site, date, _ = new_img_name.split('_')

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

def date_check(date):
    try:
        if len(date) == 8 and date.isdigit():
            return date
        elif datetime.strptime(date, '%Y%m%dT%H%M%S%z'):
            return date
    except:
        return False

def convert_json(vott_paths, input_dir):
    print('converting vott to json and save josn files')
    today = str(date.today())
    local_path_json = join(input_dir, today, 'json')
    os.makedirs(local_path_json, exist_ok=True)

    json_files = []
    json_datas = []
    for vott_file in tqdm(vott_paths):
        vott_json = load_json(vott_file)
        labeled_date = vott_file.split(os.path.sep)[-3][-10:].replace('-', '')
        if not date_check(labeled_date):
            print('wrong date format')
            break
        json_data = convert_vott(vott_json, labeled_date)
        json_datas.append(json_data)
        json_file = save_json(json_data, join(local_path_json, json_data["img_name"]+'.json'))
        json_files.append(json_file)
        
    return json_files, json_datas

def compress_vott(input_dir, vott_prj_files):
    print('compressing vott files(img/json) with zip format')
    zip_files = []
    for vott_set in tqdm(vott_prj_files):
        vott_prj = load_json(vott_set)
        img_name = list(vott_prj["assets"].values())[0]["name"]
        _,dataset,_,_,_ = img_name.split('_')

        for _ in range(2):
            vott_set = split(vott_set)[0]
        set_name = split(vott_set)[1]
        
        zip_dir = join(input_dir, str(date.today()), 'zip')
        os.makedirs(zip_dir, exist_ok=True)
        zip_file = join(zip_dir, f'{set_name}.zip')
        zip_files.append([zip_file, dataset])
        with ZipFile(zip_file, 'w') as zfile:
            for path, _, files in os.walk(vott_set):
                for file in files:
                    zip_contents = join(path, file)
                    folder = split(path)[1]
                    zfile.write(zip_contents, join(folder, file))

    return zip_files

def img_to_NAS(input_dir, nas):
    print('send image files to NAS')
    img_path_format = join(input_dir, 'reviewed', '**', '*.jpg')
    img_paths = glob(img_path_format, recursive=True)
    for img_path in tqdm(img_paths):
        f_name = split(img_path)[1]
        _, dataset, _, _, _ = f_name.split('_')
        nas_img_path = f'Nota-its/data/traffic/{dataset}/image'
        nas_img_name = '/'.join([nas_img_path, f_name])
        nas.put(img_path, nas_img_name)

def json_to_NAS(json_files, nas):
    print('send json files to NAS')
    for json_file in tqdm(json_files):
        f_name = split(json_file)[1]
        _, dataset, _, _, _ = f_name.split('_')
        nas_json_path = f'Nota-its/data/traffic/{dataset}/label'
        nas_json_name = '/'.join([nas_json_path, f_name])
        nas.put(json_file, nas_json_name)

def zip_to_NAS(zip_files, nas):
    print('send zip files to NAS')
    for vott_zip, dataset in tqdm(zip_files):
        _, zip_name = split(vott_zip)
        labeled_date = zip_name[-14:-4]
        nas_vott_path = f'/Labeling-Task/data/traffic/{dataset}/reviewed/{labeled_date}'
        if labeled_date not in nas.listdir(split(nas_vott_path)[0]):
            nas.mkdir(nas_vott_path)
        nas_zip = '/'.join([nas_vott_path, zip_name])
        nas.put(vott_zip, nas_zip)

def json_to_ES(json_datas, es_url, es_index):
    print("uploading json_data to ES")
    for json_data in tqdm(json_datas):
        post_requests(json_data, es_url, es_index)

def main():
    args = get_parser()
    input_dir = args.input_dir
    cfg = get_config()
    es_url = cfg["ES_URL"]
    es_index = cfg["ES_INDEX"]
    nas_ip = cfg["NAS_IP"]
    nas_username = cfg["NAS_USERNAME"]
    nas_password = cfg["NAS_PASSWORD"]
    nas_ssh_port = cfg["NAS_SSH_PORT"]

    vott_format = join(input_dir, "reviewed", "**", "*.json")
    vott_files = glob(vott_format, recursive=True)
    vott_prj_format = join(input_dir, "reviewed", "**", "*.vott")
    vott_prj_files = glob(vott_prj_format, recursive=True)
    
    # compress vott to zip
    zip_files = compress_vott(input_dir, vott_prj_files)

    # convert its-json & save
    json_files, json_datas = convert_json(vott_files, input_dir)

    # upload json to ES
    json_to_ES(json_datas, es_url, es_index)
    
    with NAS_client(nas_ip, nas_username, nas_password, nas_ssh_port) as nas:
        # send img to data folder
        img_to_NAS(input_dir, nas)
        
        # send its-json to NAS
        json_to_NAS(json_files, nas)
        
        # send vott(label, img) to labeling-task
        zip_to_NAS(zip_files, nas)
        

if __name__=="__main__":
    main()
    
