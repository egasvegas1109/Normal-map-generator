# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 19:12:47 2021

@author: gama0
"""

import requests
import urllib3
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from fake_useragent import UserAgent
import copy
import os
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# a list of textures to NOT include
filters = ['AcousticFoam',
  'Candy',
  'ChristmasTreeOrnament',
  'Facade',
  'Fence',
  'Fingerprint',
  'Foam',
  'Metal Walkway',
  'OfficeCeiling',
  'Pathway',
  'Paint00',
  'Painting',
  'PineNeedles',
  'Porcelain',
  'Road',
  'RockBrush',
  'Rust001',
  'Sign',
  'Scratches',
  'Smear',
  'Sticker',
  'Tape',
  'TreeEnd',
  'SurfaceImperfections',
  'Footsteps',
  'Substance']

# ambientCG website:
output_path = '../dataset/zip/'
home = 'https://ambientcg.com/'
url = "https://ambientcg.com/list?category=&type=Material&sort=Alphabet"

if not os.path.exists(output_path):
    os.makedirs(output_path)

#%%
def main():
    # agent to request
    user_agent = UserAgent()
    download_url = []
    method_url = [url + '&method=PBRMultiAngle']

    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)

    # for methods with multiple pages of content (1 page has 180 links)
    offsets = [0, 180, 360, 540, 720, 900]
    for offset in offsets:
        method_url.append(url + '&method=PBRApproximated' + '&offset={}'.format(offset))
        method_url.append(url + '&method=PBRPhotogrammetry' + '&offset={}'.format(offset))
        method_url.append(url + '&method=PBRProcedural' + '&offset={}'.format(offset))

    #%%
    # =========================== request the list to "download_url"===================
    for i in method_url:
        driver.get(i)
        re = driver.page_source
        soup = BeautifulSoup(re,'html.parser')

        elems = soup.find_all('a')
        for elem in elems:
            # texture_url + elem = each download url
            if elem.get('href') and elem.get('href').startswith("/view?id="):
                n = elem.get('href').split('/')[-1]
                download_url.append(home + n)

    copy_download_url = copy.deepcopy(download_url)

    # =========================== filters ===================
    # ( I don't know the reason why there's 99 elements need to be removed, but it can't do it completely at once.)
    n = 0
    for _ in range(5):
        for i in copy_download_url:
            for word in filters:
                if i.split('=')[-1].startswith(word):
                    # print('remove this!', i)
                    copy_download_url.remove(i)
                    n += 1

    copy_download_url.sort()
    # np.savetxt('test.txt',copy_download_url,delimiter="\n", fmt="%s")

    #%%
    # =========================== request download url ===================
    counts = 0
    for i in tqdm(range(len(copy_download_url))):
    # ==========================
        # 如果爬的過程斷掉，從多少開始...
        if i<counts:
            # counts += 1
            continue
    # ==========================
        # print(copy_download_url[i])
        import urllib3
        import requests
        import warnings

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

        driver.get(copy_download_url[i])
        re = driver.page_source
        soup = BeautifulSoup(re,'html.parser')

        # if you want to choose png or JPG
        zip_url = []
        elems = soup.find_all('a', class_= "asset-download")
        for elem in elems:
            zip_url.append(elem.get('href'))

        r = requests.get(zip_url[0], # https://ambientcg.com/get?file=Tiles098_1K-JPG.zip
                        headers = { 'user-agent': user_agent.random }, verify=False)

        with open(output_path + zip_url[0].split('=')[-1], "wb") as zipfile:
            zipfile.write(r.content)

        time.sleep(0.1)
        counts += 1

if __name__ == "__main__":
    main()
