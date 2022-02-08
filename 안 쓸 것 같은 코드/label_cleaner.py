import json
import os
from glob import glob
from pprint import pprint


replace_dict = {'blacklight':'backlight', 'person':'pedestrian', 'adult':'pedestrian', 'police _back':'police_back',
                'ambuance_back':'ambulance_back', 'child':'pedestrian'}
delete_list = [] #['personal_mobility', 'bicycle']
weather = ['sunny', 'rainy', 'snow', 'snowy', 'foggy']
light = ['day', 'night', 'backlight']


def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas


def main():
    input_dir = os.getcwd()

    json_list = glob(f'{input_dir}/**/*.json', recursive=True)
    print(len(json_list))

    labels = dict()
    keep_json_list = []
    
    for json_file in json_list:
        label_data = load_json(json_file)
        remove_idx = []
        label_cnt = 0
        
        for i, obj in enumerate(label_data["regions"]):
            tag = obj["tags"][0]

            if tag not in weather+light:
                label_cnt += 1
            
            if tag in replace_dict:
                tag = replace_dict[tag]
            elif tag in delete_list:
                remove_idx.append(i)
                continue
                
            label_data["regions"][i]["tags"] = [tag]

            if tag not in labels:
                labels[tag] = 0
            labels[tag] += 1
            
        for i in remove_idx:
            pprint(label_data["regions"])
            print(i)
            del label_data["regions"][i]

        if not label_cnt:
            os.remove(json_file)
            continue
        else:
            keep_json_list.append(label_data["asset"]["name"])

        with open(json_file, 'w') as f:
            json.dump(label_data, f, indent="\t")
            
            
    img_list = os.listdir(f'{input_dir}/img/')
    only_img = set(img_list) - set(keep_json_list)
    print('delete_list:')
    pprint(only_img)
    for img in only_img:
        # img 파일 삭제
        os.remove(f'{input_dir}/img/'+img)
    
    pprint(labels)

    os.system('pause')
        

if __name__ == "__main__":
    main()
