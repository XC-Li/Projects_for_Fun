"""image downloader"""
from typing import Dict, List
import urllib.request
from bs4 import BeautifulSoup
import re
import requests
import os
from tqdm.auto import tqdm
import cv2


website = "https://www.jav.ink/category/graphis-collection-2002-2018/"
image_root = "D:/PPic/GraphisDataSet/"


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

def main():
    pass


if __name__ == '__main__':
    print(get_actress_from_menu(1))
    # save_image('https://www.jav.ink/wp-content/uploads/2020/02/10/gra_uta-y_sp121.jpg', 'Uta_Yumemite_夢見照うた')