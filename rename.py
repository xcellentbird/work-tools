import os
import argparse
from glob import glob
from os.path import join, split


def get_parser():
    parser = argparse.ArgumentParser(description='convert setting')
    parser.add_argument('-i', '--input_dir', required=False, default=os.getcwd())
    parser.add_argument('-s', '--save_dir', required=False)
    parser.add_argument('-e', '--ext', default='jpg')
    return parser.parse_args()

DAEJEON_SITE = {'원골네거리_도안고등학교방면_03': 'wongolnegeori-N',
                '원골네거리_원신흥동방면_02': 'wongolnegeori-W', 
                '원골네거리_유성온천역2번출구방면_01': 'wongolnegeori-S',
                '원골네거리_유성온천역7번출구방면_04': 'wongolnegeori-E', 
                '유성네거리_구암역방면': 'yuseongnegeori-E', 
                '유성네거리_만년교방면': 'yuseongnegeori-W',
                '유성네거리_봉명동방면': 'yuseongnegeori-N', 
                '유성네거리_온천교방면': 'yuseongnegeori-S', 
                '진터지하차도_봉면중학교방면': 'jinteonegeori-W',
                '진터지하차도_만년교방면': 'jinteonegeori-S', 
                '진터지하차도_도안고등학교방면': 'jinteonegeori-N', 
                '진터지하차도_인삼골네거리방면': 'jinteonegeori-E'}          

def parsing1(name):
    country, dataset, site, day, time, index = name.split('-')
    country = 'KOR'
    dataset = 'DJ-RNBD'
    site = DAEJEON_SITE[site]
    day = day.replace('_', '')
    time = time.replace('_', '')
    date = day + 'T' + time + '+0900'
    
    new_name = '_'.join([country, dataset, site, date, index])
    return new_name

def parsing2(name):
    try:
        country, dataset, site, date, index = name.split('_')
        new_name = '_'.join([country, dataset, site, date, index])
    except:
        return name
    return new_name

def video_rename(file):
    path_splited = file.split(os.path.sep) # '', 'volume1', 'Nota-its', 'data', 'traffic', 'DJ-RNBD', '장교~', node, site
    file_name = path_splited[-1]
    try:
        site = DAEJEON_SITE[path_splited[-2]]
        
        date, enddate = file_name.split('_')
        date = date[:8] + 'T' + date[8:] + '00+0900'

        new_name = '_'.join(['KOR', 'DJ-RNBD', site, date + '.avi'])
        return new_name
    except:
        return file_name
    

def main():
    args = get_parser()
    input_dir = args.input_dir
    save_dir = args.save_dir
    ext = args.ext

    file_format = join(input_dir, '**', f'*.{ext}')
    files = glob(file_format, recursive=True)

    for file in files:
        path, name = split(file)
        if not save_dir:
            save_dir = path
        new_name = video_rename(file)
        os.rename(file, join(save_dir, new_name))

if __name__=="__main__":
    main()