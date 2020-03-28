"""image downloader"""
from typing import Dict, List
import urllib.request
from bs4 import BeautifulSoup
import re
import requests
import os
from tqdm.auto import tqdm
import cv2 as cv
import numpy as np


website = "https://www.jav.ink/category/graphis-collection-2002-2018/"
image_root = "D:/PPic/GraphisDataSet/"
label_file = "D:/PycharmProjects/Projects_for_Fun/oppai/GraphisLabel.csv"
download_completed_record = 'D:/PycharmProjects/Projects_for_Fun/oppai/GraphisCompleted.txt'


def link_to_soup(url: str) -> BeautifulSoup:
    head = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    request = urllib.request.Request(url, headers=head)
    response = urllib.request.urlopen(request)
    if response.status != 200:
        print('error opening :', url)
        raise ValueError
    soup = BeautifulSoup(response.read().decode('utf-8'), 'lxml')
    return soup


def get_actress_from_menu(page_id: int) -> Dict[str, str]:
    if page_id == 1:
        url = website
    else:
        url = website + 'page/' + str(page_id) + '/'
    soup = link_to_soup(url)
    display_boxes = soup.find_all('li', class_=re.compile('ex34 post-'))
    name_link_dict = dict()
    for box in display_boxes:
        single_record = box.find_all('h2', class_='article-title entry-title')
        assert len(single_record) == 1
        link = single_record[0].a.attrs['href']
        name = single_record[0].a.string.replace(' ', '_')
        if link[-3] == '-' and link[-2].isnumeric():  # duplicate in the folder name, link end with "-n"
            name = name + '_' + link[-2]
        name_link_dict[name] = link
    # print(len(name_link_dict))
    return name_link_dict


def get_image_list(link: str) -> List[str]:
    soup = link_to_soup(link)
    image_list = []
    for image_container in soup.find_all('dt', class_='gallery-icon portrait'):
        image_list.append(image_container.a.attrs['href'])
    return image_list
        

def save_image(link: str, folder: str):
    file_name = link.split('/')[-1]
    myfile = requests.get(link)
    out_file = image_root + folder + '/' + file_name
    if not os.path.exists(image_root + folder):
        os.mkdir(image_root + folder)
    open(out_file, 'wb').write(myfile.content)
    key = record_label(out_file)
    return out_file + ',' + key + '\n'


def record_label(image_file):
    f = open(image_file, "rb")
    chunk = f.read()
    chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
    image = cv.imdecode(chunk_arr, cv.IMREAD_COLOR)
    cv.namedWindow('image', cv.WINDOW_NORMAL)
    cv.resizeWindow('image', image.shape[1]//2, image.shape[0]//2)
    cv.imshow('image', image)
    key_naked = key_posture = key_parts = key_4 = '/'
    while key_naked == '/' or key_posture == '/' or key_parts == '/' or key_4 == '/':  # if there is a mistake
        print(image_file, end=':')
        key_naked = chr(cv.waitKey(0))
        print(key_naked, end='')
        key_posture = chr(cv.waitKey(0))
        print(key_posture, end='')
        key_parts = chr(cv.waitKey(0))
        print(key_parts, end='\n')
        key_4 = chr(cv.waitKey(0))
    cv.destroyAllWindows()
    key = key_naked + key_posture + key_parts
    if key == '|||':
        exit()
    # print(key)
    return key


def main(page_start, page_end=None):
    if page_end is None:
        page_end = page_start + 1
    records = []
    try:
        with open(download_completed_record, 'r') as record_file:
            for line in record_file:
                records.append(line.rstrip())
    except FileNotFoundError:
        pass
    for page_id in range(page_start, page_end):
        print('page:', page_id)
        actress_dict = get_actress_from_menu(page_id)
        for actress in actress_dict:
            temp_result = []
            print('actress:', actress)
            if actress in records:
                print('actress:', actress, 'already downloaded')
                continue  # already downloaded
            else:
                image_list = get_image_list(actress_dict[actress])
                for image_link in image_list:  # download all image
                    temp_result.append(image_link + ',' + save_image(image_link, actress))

                with open(label_file, 'a+') as label:
                    for line in temp_result:
                        label.write(line)
                with open(download_completed_record, 'a+') as record_file:  # after download completed
                    record_file.write(actress + '\n')


if __name__ == '__main__':
    # print(get_actress_from_menu(1))
    # save_image('https://www.jav.ink/wp-content/uploads/2020/02/10/gra_uta-y_sp121.jpg', 'Uta_Yumemite_夢見照うた')
    # record_label("D:/PPic/GraphisDataSet/Uta_Yumemite_夢見照うた/gra_uta-y_sp121.jpg")
    main(1)
