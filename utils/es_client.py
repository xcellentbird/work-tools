import json
import requests
import sys
from tqdm import tqdm


ES_URL = 'http://34.64.93.57:9200'

def bulk_requests(json_datas:list, url, index)-> str:
    json_head = {"index": {"_index": index, "_id": ""}}
    batch_size = 100
    batch_cnt = len(json_datas) // batch_size + 1

    data_size = sys.getsizeof(json_datas[:batch_size])
    print("batch_data size: {}".format(data_size))

    for cnt in tqdm(range(batch_cnt)):
        str_jsons = ''
        batch_data = json_datas[cnt*batch_size:(cnt+1)*batch_size]

        for json_data in batch_data:
            doc_id = json_data["img_name"]
            json_head['_id'] = doc_id
            str_json = json.dumps(json_head) + '\n' + json.dumps(json_data) + '\n'

            str_jsons += str_json

        url = "/".join([url, '_bulk'])
        headers = {"Content-Type": "application/json"}
        response = requests.post(url=url, data=str_jsons, headers=headers)
    
    return response

def put_requests(json_data, url, index):
    doc_id = json_data["img_name"]
    str_json = json.dumps(json_data)
    url = "/".join([url, index, '_doc', doc_id])

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=str_json, headers=headers)
    
    return response

def load_json(path):
    with open(path, 'r') as f:
        json_data = json.load(f)
    return json_data

def json_request(json_paths, url, index):
    for json_file in tqdm(json_paths):
        json_data = load_json(json_file)
        response = put_requests(json_data, url, index)
    
    print(f'response: {response}')