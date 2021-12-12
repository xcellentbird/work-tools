import subprocess
import sys
from os.path import join
import os

try:
    import pip
except ImportError:
    print("Install pip for python3")
    subprocess.call(['sudo', 'apt-get', 'install', 'python3-pip'])


try:
    import argparse
except ModuleNotFoundError:
    print("Install argparse in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'argparse'])
finally:
    import argparse

try:
    import ffmpeg
except ModuleNotFoundError:
    print("Install ffmpeg-python in python3")
    subprocess.call([sys.executable, "-m", "pip", "install", 'ffmpeg-python'])
finally:
    import ffmpeg


def GetArgument():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_path", required=True, help="video input dir path")
    ap.add_argument("-o", "--output_path", required=True, help="video output dir path")
    ap.add_argument("-ste", "--start_to_end", required=True, help="input start time and end time", nargs=2)
    args = ap.parse_args()
    
    return args.input_path, args.output_path, args.start_to_end

def main():
    input_path, output_path, (start, end) = GetArgument()

    for video_names in os.listdir(input_path):
        input_name = join(input_path, video_names)
        output_name = join(output_path, video_names.split('.')[0] + '.mp4')
        print(output_name)
        
        video = ffmpeg.input(input_name)
        video = ffmpeg.trim(video, start=start, end=end)
        video = ffmpeg.output(video, output_path)
        ffmpeg.run(video)
        print('saved', join(output_path, video_names.split('.')[0]))
    

if __name__ == "__main__":
    main()
