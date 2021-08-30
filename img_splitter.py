import sys
import subprocess
import os
import shutil
from datetime import datetime


# pip가 없으면 pip를 설치한다.
try:
    import pip
except ImportError:
    print("Install pip for python3")
    subprocess.call(['sudo', 'apt-get', 'install', 'python3-pip'])


# cv가 없으면 cv를 설치한다.
try:
    import cv2
except ModuleNotFoundError:
    print("Install opencv in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'opencv-python'])
finally:
    import cv2


# argparse가 없으면 argparse를 설치한다.
try:
    import argparse
except ModuleNotFoundError:
    print("Install argparse in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'argparse'])
finally:
    import argparse

# numpy가 없으면 numpy를 설치한다.
try:
    import numpy
except ModuleNotFoundError:
    print("Install numpy in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'numpy'])
finally:
    import numpy as np

dir_del = None
clicked_points = []
clone = None


def GetArgument():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_path", required=True, help="image input dir path")
    ap.add_argument("-o", "--output_path", required=True, help="image output dir path")
    args = vars(ap.parse_args())
    
    return args['input_path'], args['output_path']

def main():
    global clone, clicked_points
    
    print("\n")
    print("1. 입력한 파라미터인 이미지 경로(--path)에서 이미지들을 차례대로 읽어옵니다.")
    print("2. 키보드에서 'n'을 누르면(next 약자) 다음 이미지로 넘어갑니다.")
    print("3. 키보드에서 'b'를 누르면(back 약자) 이전 이미지로 넘어갑니다.")
    print("4. 키보드에서 'spacebar'를 누르면 저장할 이미지를 선택/해제 합니다.")
    print("5. 이미지 경로에 존재하는 모든 이미지에 작업을 마친 경우 또는 'q'를 누르면(quit 약자) 프로그램이 종료됩니다.")
    print("\n")

    # 이미지 디렉토리 경로를 입력 받는다.
    input_path, output_path = GetArgument()
    # path의 이미지명을 받는다.
    image_names = os.listdir(input_path)

    # path를 구분하는 delimiter를 구한다.
    if len(input_path.split('\\')) > 1:
        dir_del = '\\'
    else :
        dir_del = '/'

    # path에 입력된 마지막 폴더 명을 구한다.    
    folder_name = input_path.split(dir_del)[-1]


    # 새 윈도우 창을 만들고 그 윈도우 창에 click_and_crop 함수를 세팅해 줍니다.
    cv2.namedWindow("image")
    # cv2.setMouseCallback("image", MouseLeftClick)

    check_list = [False for _ in range(len(image_names))]

    idx = 0
    while True:
    
        # if (idx % sampling != 0):
        #     continue
        
        image_name = image_names[idx]

        image_path = input_path + dir_del + image_name
        image = cv2.imread(image_path)

        clone = image.copy()
        
        flag = False

        while True:
            if check_list[idx] :
                image[:40,:,0] = 255
            cv2.imshow("image", image)

            key = cv2.waitKey(0)

            if key == ord('n'):
                if idx < len(image_names) - 1:
                    idx += 1
                # # 텍스트 파일을 출력 하기 위한 stream을 open 합니다.
                # # 중간에 프로그램이 꺼졌을 경우 작업한 것을 저장하기 위해 쓸 때 마다 파일을 연다.
                # file_write = open('./' + now_str + '_' + folder_name + '.txt', 'a+')

                # text_output = image_name
                # text_output += "," + str(len(clicked_points))
                # for points in clicked_points:
                #     text_output += "," + str(points[0]) + "," + str(points[1])
                # text_output += '\n'
                # file_write.write(text_output)
                
                # # 클릭한 점 초기화
                # clicked_points = []

                # # 파일 쓰기를 종료한다.
                # file_write.close()

                break

            if key == ord(' '):
                check_list[idx] = not check_list[idx]
                break

            if key == ord('b'):
                if idx >= 1:
                    idx -= 1
                break

            if key == ord('q'):
                # 프로그램 종료
                flag = True
                break
                
        # 현재 체크한 이미지 개수와 진행 상황을 print합니다.
        print("Select Count: {}\tnow: {}/{}".format(sum(check_list), idx+1, len(check_list)), end="\r")
        if flag:
            break

    image_path = input_path + dir_del
    # save file
    for idx, image_name in enumerate(image_names):
        if check_list[idx] :
            shutil.move(image_path + image_name, os.path.join(output_path, image_name))

    # 모든 window를 종료합니다.
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()
