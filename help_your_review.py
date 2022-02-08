"""
일반적으로 검수할 때, 나타나는 이슈가 있습니다.
1. 약속해둔 class 이름과 태그 이름이 다른 경우
2. 라벨링 수행 환경이 검수 환경과 다른 경우 ex. Mac <-> Windows
3. 라벨이 없는 이미지가 존재하는 경우
4. 의도하지 않은 중복 라벨링
5. 라벨링 기준이 다른 경우
6. bbox 크기
7. ROI 외의 영역에 bbox 존재하는 경우
8. ROI 내의 영역에 bbox가 충분히 존재하지 않는 경우

해당 코드는 1~4을 해결하기 위해 짜여진 코드입니다.
해결 방법
1. -> label monitor를 통해 정해둔 class 이름과 다른 태그가 있는지 알려줍니다. 그리고 dictionary 파일을 통해 한번에 class를 수정할 수 있습니다.
2. -> encrypted와 path 내용을 Windows 기준으로 변경합니다.
3. -> 해당 이미지를 제거합니다.
4. -> 순서상 맨 앞의 라벨만 남겨둡니다.
"""

import os
import argparse
import json
from glob import glob
from os.path import join
from pprint import pprint
from tqdm import tqdm


VOTT_IMG_PATH = 'file:C:/ptits/img'
VOTT_ENCRYPTED = ['eyJjaXBoZXJ0ZXh0IjoiNjZlNDNjNjk2OTk0OTNiNmZkYzdmZTI2OWY1MGYyNTMxNzgxYzQ1ZjY4MTMzNTA3NWJiNjVlMTIzMzNkYzc3YSIsIml2IjoiYzk4NjE3YjZhN2IwYTQyOGQxZjJjOTQ5YmJlOWUyMDdhNzAyY2RkN2IzNWQ0ZmRjIn0=',
                'eyJjaXBoZXJ0ZXh0IjoiMTZkODA0NzJmZTdlMGUyY2Y2NzlhMzg1NDI5OWE2OTVlMmFkZjMxMDFhMTBkYzJlMTcyMGMyYWM1MWNhMjZkYjhiNmYwOWFmODQ3MDljOWE0MTkyYWU0NmViZjk0MDhlIiwiaXYiOiIzZjk0NmJjNzlmMjgyYjJmNjM0OTBkOWM0YTEwZGI2MzU1ZDQwMTJkNWQ0OWQ3YjIifQ==',
                'eyJjaXBoZXJ0ZXh0IjoiNDhkYTY1YTUxNDQxY2IzOGFjOWRlZWEwYWIwMjVmODEzMDJjZTk3NzlkMWMxNWNjNmZkOGIyNDEwN2M0M2JhODNhMzc5ODAyOGU1NzI1ZjhkMzEwMmMzYWIzZjc5NzdjIiwiaXYiOiJiMGFlNzAwOGE0MmMwNDQwYjJiNjQ0NDNhZTNkNTNlMWI4ZTUxMDgxYTk0ZWUxYjEifQ==']

def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')
    parser.add_argument('-i', '--input_dir', required=False, default=os.getcwd())
    parser.add_argument('-c', '--class_list', required=False, default=join(os.getcwd(), 'class_list.txt'))
    return parser.parse_args()

def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas

def save_json(json_data, save_path):
    with open(save_path, 'w') as f:
        json.dump(json_data, f, indent='\t', ensure_ascii=False)

def get_objects(json_data):
    regions = json_data["regions"]
    return [region["tags"] for region in regions]

def get_files(input_dir):
    exts = ['*.jpg', '*.json', '*.vott']
    ext_glob = lambda ext: glob(join(input_dir, '**', ext), recursive=True)
    return [ext_glob(ext) for ext in exts]

def classifier(obj, total_class):
    main_class, weather_class, light_class = total_class
    if obj in main_class:
        main_class[obj] += 1
    elif obj in weather_class:
        weather_class[obj] += 1
    elif obj in light_class:
        light_class[obj] += 1
    else:
        return False
    return True

def del_files(file_paths):
    for file_path in tqdm(file_paths):
        os.remove(file_path)

def edit_vott(vott_files, replace_dict, total_class):
    for vott_file in vott_files:
        vott = load_json(vott_file)

        vott["sourceConnection"]["providerOptions"]["encrypted"] = VOTT_ENCRYPTED[0]
        vott["targetConnection"]["providerOptions"]["encrypted"] = VOTT_ENCRYPTED[1]
        vott["exportFormat"]["providerOptions"]["encrypted"] = VOTT_ENCRYPTED[2]

        for asset_id, v_dict in vott["assets"].items():
            new_path = '/'.join([VOTT_IMG_PATH, v_dict["name"]])
            vott["assets"][asset_id]["path"] = new_path
        
        all_tag = set()
        del_tag = []
        for i, tag in enumerate(vott["tags"]):
            tag_name = tag["name"]
            if tag_name in all_tag:
                del_tag.append(i)
                continue  
            all_tag.add(tag_name)

            vott["tags"][i]["name"] = replace_dict.get(tag_name, tag_name)

            for total_dict in total_class:
                if tag_name in total_dict:
                    vott["tags"][i]["color"] = total_dict[tag_name]
                    break

        for i in del_tag[::-1]:
            del vott["tags"][i]

        save_json(vott, vott_file)

def edit_json(edited_list):
    if edited_list:
        print('edit json')
        for json_file, json_data in tqdm(edited_list.items()):
            save_json(json_data, json_file)

def del_imgs(img_to_del):
    if img_to_del:
        print('no label in these imgs: ')
        pprint(img_to_del)
        answer = input(f'delete {len(img_to_del)} imgs? [Y/N] ')
        if answer.upper() == 'Y':
            del_files(img_to_del)

def review_json(json_files, total_class):
    labeled_imgs = []
    edited_dict = dict() # 해당 json_file이 value값으로 수정되었음을 알려주는
    to_edit = []

    print('review json file')
    for json_file in tqdm(json_files):
        json_data = load_json(json_file)

        labeled_imgs.append(json_data["asset"]["name"])
        objects = get_objects(json_data)

        for i, obj_list in enumerate(objects):
            obj = obj_list[0]

            # mulit-labeled check
            if len(obj_list) > 1:
                json_data["regions"][i]["tags"] = [obj]
                edited_dict[json_file] = json_data
            
            # 의도하지 않은 class 이름 check
            if not classifier(obj, total_class):
                to_edit.append([json_file, json_data, i, obj])

        # 파일 경로 수정
        asset_path = json_data["asset"]["path"]
        if asset_path[:len(VOTT_IMG_PATH)] != VOTT_IMG_PATH:
            asset_name = json_data["asset"]["name"]
            json_data["asset"]["path"] = '/'.join([VOTT_IMG_PATH, asset_name])
            edited_dict[json_file] = json_data
    
    return labeled_imgs, edited_dict, to_edit

def img_check(img_files, labeled_imgs):
    print('review img file')
    img_to_del = []
    for img_file in tqdm(img_files):
        _, file_name = os.path.split(img_file)
        if file_name not in labeled_imgs:
            img_to_del.append(img_file)
    return img_to_del

def replace_class(total_class, edited_dict, to_edit):
    replace_dict = dict()
    not_our_cls = {cls for _, _, _, cls in to_edit}

    if not_our_cls:
        print('wrong class name:')
        print(not_our_cls)
        answer = input('input replace dictionary file(with path): ')
        if answer:
            replace_dict = load_json(answer)
        
            for json_file, json_data, i, obj in to_edit:
                new_obj = replace_dict.get(obj, obj)
                json_data["regions"][i]["tags"] = [new_obj]
                classifier(new_obj, total_class)
                edited_dict[json_file] = json_data
    
    return replace_dict

def init_class_cnt(class_list):
    main_class = {c:0 for c in class_list["main"]}
    weather_class = {c:0 for c in class_list["weather"]}
    light_class = {c:0 for c in class_list["light"]}
    total_class = [main_class, weather_class, light_class]
    return total_class

def main():
    args = get_parser()
    input_dir = args.input_dir
    class_list = load_json(args.class_list)

    total_class = init_class_cnt(class_list)
    img_files, json_files, vott_files = get_files(input_dir)

    review_result = review_json(json_files, total_class)
    labeled_imgs, edited_dict, to_edit = review_result

    img_to_del = img_check(img_files, labeled_imgs)
    del_imgs(img_to_del)

    replace_dict = replace_class(total_class, edited_dict, to_edit)
    edit_json(edited_dict)
    edit_vott(vott_files, replace_dict, total_class)

    print('----------------------------------')
    print(f'total labeled imgs: {len(labeled_imgs)}')
    print(f'total tags: {sum(total_class[0].values())}')
    pprint(total_class[0])
    pprint(total_class[1])
    pprint(total_class[2])

if __name__=="__main__":
    main()
    os.system('pause')