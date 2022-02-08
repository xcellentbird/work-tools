import json
import os
from glob import glob
from pprint import pprint


replace_dict = {'blacklight':'backlight', 'person':'pedestrian', 'adult':'pedestrian', 'police _back':'police_back',
                'ambuance_back':'ambulance_back'}
delete_list = ['personal_mobility', 'bicycle']


def load_json(path):
    with open(path, 'r') as f:
        datas = json.load(f)
    return datas


def main():
    input_dir = os.getcwd()

    json_list = glob(f'{input_dir}/**/*.json', recursive=True)
    print(len(json_list))

    labels = dict()
    
    for json_file in json_list:
        label_data = load_json(json_file)
        remove_idx = []
        
        for i, obj in enumerate(label_data["regions"]):
            tag = obj["tags"][0]
            
            if tag in replace_dict:
                tag = replace_dict[tag]
            elif tag in delete_list:
                remove_idx.append(i)
                continue
                
            label_data["regions"][i]["tags"] = [tag]

            if tag not in labels:
                labels[tag] = 1
            else:
                labels[tag] += 1

        for i in remove_idx:
            del label_data["regions"][i]

        with open(json_file, 'w') as f:
            json.dump(label_data, f, indent="\t")        
    
    pprint(labels)

    os.system('pause')
        

if __name__ == "__main__":
    main()
