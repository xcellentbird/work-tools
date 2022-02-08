from utils.nas_client import NAS_client
from tqdm import tqdm
import os

dir = 'D:/NAS_backup/DJ/image/'
n_pth = 'Nota-its/data/traffic/DJ-RNBD/image/'
local_imgs = os.listdir(dir)

with NAS_client() as n:
    for img in tqdm(local_imgs):
        n.put(dir+img, n_pth+img)
