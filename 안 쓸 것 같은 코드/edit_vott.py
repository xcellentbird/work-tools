#!/usr/bin/env python
# coding: utf-8


import os

folder_path = 'C:/ptits/json/'
file_name = 'ptits.vott'
file_path = os.path.join(folder_path, file_name)
file_path


# 2. __수정 내용__
# * 보안망에 걸리지 않도록 vott 프로젝트 파일을 수정해야합니다.
# 
# 
# * "encrypted"의 value는 모두 _"eyJjaXBoZXJ0ZXh0IjoiNjZlNDNjNjk2OTk0OTNiNmZkYzdmZTI2OWY1MGYyNTMxNzgxYzQ1ZjY4MTMzNTA3NWJiNjVlMTIzMzNkYzc3YSIsIml2IjoiYzk4NjE3YjZhN2IwYTQyOGQxZjJjOTQ5YmJlOWUyMDdhNzAyY2RkN2IzNWQ0ZmRjIn0="_ 와 같이 수정합니다.
# 
# 
# * _"C:/ptits/..."_ 와 같이 이미지 경로를 수정합니다.
# 
# > ex)  
# > 변경 전: __"path": "file:/Volumes/Macintosh%20HD%20-%20%E1%84%83%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%90%E1%85%A5%201/img/cam1_21-08-08_00-02-26-33.jpg"__  
# > 변경 후: __"path": "file:C:/ptits/img/cam1_21-08-08_00-02-26-33.jpg"__


# 수정할 key와 그 내용
k = '"encrypted"'
v = ['', '', '']
v[0] = '"eyJjaXBoZXJ0ZXh0IjoiNjZlNDNjNjk2OTk0OTNiNmZkYzdmZTI2OWY1MGYyNTMxNzgxYzQ1ZjY4MTMzNTA3NWJiNjVlMTIzMzNkYzc3YSIsIml2IjoiYzk4NjE3YjZhN2IwYTQyOGQxZjJjOTQ5YmJlOWUyMDdhNzAyY2RkN2IzNWQ0ZmRjIn0="'
v[1] = '"eyJjaXBoZXJ0ZXh0IjoiMTZkODA0NzJmZTdlMGUyY2Y2NzlhMzg1NDI5OWE2OTVlMmFkZjMxMDFhMTBkYzJlMTcyMGMyYWM1MWNhMjZkYjhiNmYwOWFmODQ3MDljOWE0MTkyYWU0NmViZjk0MDhlIiwiaXYiOiIzZjk0NmJjNzlmMjgyYjJmNjM0OTBkOWM0YTEwZGI2MzU1ZDQwMTJkNWQ0OWQ3YjIifQ=="'
v[2] = '"eyJjaXBoZXJ0ZXh0IjoiNDhkYTY1YTUxNDQxY2IzOGFjOWRlZWEwYWIwMjVmODEzMDJjZTk3NzlkMWMxNWNjNmZkOGIyNDEwN2M0M2JhODNhMzc5ODAyOGU1NzI1ZjhkMzEwMmMzYWIzZjc5NzdjIiwiaXYiOiJiMGFlNzAwOGE0MmMwNDQwYjJiNjQ0NDNhZTNkNTNlMWI4ZTUxMDgxYTk0ZWUxYjEifQ=="'

# 수정할 path key
p_k = '"path"'
to_edit = []

# 파일을 읽어와 to_edit에 내용을 담습니다.
with open(file_path, 'r') as f:
    to_edit = f.readlines()

# 내용을 한 줄씩 읽으면서
ecpt_cnt = 0
for i, line in enumerate(to_edit):
    # 'encrypted'가 line에 있으면,
    if k in line:
        idx = line.index(k) + len(k) + 2
        to_edit[i] = line[:idx] + v[ecpt_cnt] + '\n'
        ecpt_cnt += 1
    
    # 'path'가 line에 있으면,
    if p_k in line:
        spt = line.split(':')
        spt2 = spt[-1].split('/')
        to_edit[i] = ':'.join(spt[:2] + ['C:/ptits/' + '/'.join(spt2[spt2.index('img'):])])

# 파일을 수정된 내용으로 덮어씌웁니다.
with open(file_path, 'w') as f:
    f.writelines(to_edit)


# __결과:__
# * sourceConnection, targetConnection, exportFormat의 providerOptions - encrypted의 value가 모두 "ey...In0="로 바뀝니다.
# * 모든 path의 value 형식이 "file:C:/ptits/img/<파일 이름>" 으로 바뀝니다.


# 3. json파일 내의 'path' 경로를 바꿉니다.
for file in os.listdir(folder_path):
    if file[-5:] == '.json':
        to_edit = []

        # 파일을 읽어와 to_edit에 내용을 담습니다.
        with open(os.path.join(folder_path, file), 'r') as f:
            to_edit = f.readlines()

        # 내용을 한 줄씩 읽으면서
        cnt = 0
        for i, line in enumerate(to_edit):
            # 'path'가 line에 있으면,
            if p_k in line:
                spt = line.split(':')
                spt2 = spt[-1].split('/')
                to_edit[i] = ':'.join(spt[:2] + ['C:/ptits/' + '/'.join(spt2[spt2.index('img'):])])

        # 파일을 수정된 내용으로 덮어씌웁니다.
        with open(os.path.join(folder_path, file), 'w') as f:
            f.writelines(to_edit)




