import os
import sys
import json
import requests
from importlib import reload
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup as bs
from bs4.element import ResultSet
import shutil
import unicodedata


import os.path as osp
sys.path.append(osp.dirname(os.getcwd()))
reload(sys)

from utils.utils import create_dir, insert_gemstone, upload_file, retrieve_coordinates_from_countries


class Crawler(ABC):
    def __init__(self, download_location: str, destination = None):
        self.download_location = download_location
        self.homepage = None

    def get_homepage(self) -> str:
        return self.homepage

    @abstractmethod
    def download_images(self):
        pass

    @abstractmethod
    def download_information(self):
        pass

    def save_to_cloud(self, configuration: dict):
        # Upload images to S3 and save records at database

        for root, subdirs, files in os.walk(self.download_location):
            gemstone_info = {}

            if root != self.download_location:
                with open(os.path.abspath(root) + os.sep + 'info.json', 'r', encoding='utf8') as f:
                    gemstone_info = json.load(f)
                    gemstone_info['Images'] = []

                for image in [file for file in files if file.endswith('.jpg')]:
                    filename = (self.download_location + os.sep + os.path.basename(root) + os.sep + image).replace("\\", "/")

                    print('Uploading file: ' + filename)

                    if upload_file(configuration, filename, filename):
                        gemstone_info['Images'].append(filename)

                gemstone_name = root.split("\\")[1]

                if not(insert_gemstone(configuration, "gemstone", gemstone_name, gemstone_info)):
                    print("Failed to insert record: " + gemstone_info['name'])

    def get_page(self, url: str) -> bs:
        print('Acessing page: ' + url)
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        return soup

    def retrieve_coordinates_from_countries(self, configuration: dict):
        print("Generating localities of gemstones")
        retrieve_coordinates_from_countries(configuration)


class MineralsNet(Crawler):
    def __init__(self, download_location: str):
        super().__init__(download_location)

        self.homepage = "https://www.minerals.net/"
        self.gemstone_dict = self.get_gemstone_list()
        

    def get_gemstone_list(self) -> dict:
        url = self.homepage + 'GemStoneMain.aspx'
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        table = soup.find_all('table',{'id':'ctl00_ContentPlaceHolder1_DataList1'})
        return self.get_gemstones_names(table)

    def get_gemstones_names(self, table) -> ResultSet:
        names_paths = {}
        for data in table:
            for link in data.find_all('a'):
                if(link.text!=''):
                    names_paths[link.text] = link.get('href')
        return names_paths

    def download_images(self) -> None:
        for key, value in self.gemstone_dict.items():
            image_link = ''
            print('-'*8, key, '-'*8)
            gem_link = self.homepage + value
            soup = self.get_page(gem_link)
            

            possible_table_id = ['ctl00_ContentPlaceHolder1_DataList1', 'ctl00_ContentPlaceHolder1_DataList2', 'ctl00_ContentPlaceHolder1_tblPhotos1', 'ctl00_ContentPlaceHolder1_tblPhotos1']

            # Checking possible table 
            for table_id in possible_table_id:
                table_images = soup.find_all('table',{'id': table_id})
                if table_images != []:
                    break        
            
            if(table_images):
                create_dir(self.download_location + os.sep + key)

                for data in table_images:
                    for link in data.find_all('img'):
                        img_link = self.homepage + link.get('src')#.replace('-t','')
                        print("Downloading image: " + img_link)
                        r = requests.get(img_link, stream=True)
                        if r.status_code == 200:    # OK
                            with open(self.download_location + os.sep + key + os.sep + img_link.split('/')[-1], 'wb') as f:
                                r.raw.decode_content = True
                                shutil.copyfileobj(r.raw, f)

    def download_information(self):
        for key, value in self.gemstone_dict.items():
            image_link = ''
            print('-'*8, key, '-'*8)
            gem_link = self.homepage + value
            soup = self.get_page(gem_link)

            # Get gemstone information
            chemical_formula = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trChemicalFormula > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trChemicalFormula > td.t2')) != 0 else None
            color = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trColor > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trColor > td.t2')) != 0 else None
            hardness = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trHardness > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trHardness > td.t2')) != 0 else None
            crystal_system = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trCrystalSystem > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trCrystalSystem > td.t2')) != 0 else None
            refractive_index = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trRefractiveIndex > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trRefractiveIndex > td.t2')) != 0 else None
            sg = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trSG > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trSG > td.t2')) != 0 else None
            transparency = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trTransparency > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trTransparency > td.t2')) != 0 else None
            double_refraction = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trDoubleRefraction > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trDoubleRefraction > td.t2')) != 0 else None
            luster = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trLuster > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trLuster > td.t2')) != 0 else None
            cleavage = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trCleavage > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trCleavage > td.t2')) != 0 else None
            mineral_class = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_trMineralClass > td.t2')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_trMineralClass > td.t2')) != 0 else None
            source = unicodedata.normalize("NFKD", soup.select('#ctl00_ContentPlaceHolder1_lblSource')[0].get_text().strip()) if len(soup.select('#ctl00_ContentPlaceHolder1_lblSource')) != 0 else None

            gemstone_info = {'chemical_formula': chemical_formula, 'color': color, 'hardness': hardness, 'crystal_system': crystal_system, 'refractive_index': refractive_index, 'sg': sg, 'transparency': transparency,
                            'double_refraction': double_refraction, 'luster': luster, 'cleavage': cleavage, 'mineral_class': mineral_class, 'source': source
                            }

            create_dir(self.download_location + os.sep + key)

            with open(self.download_location + os.sep + key + os.sep + 'info.json', 'w', encoding='utf8') as f:
                json.dump(gemstone_info, f, ensure_ascii=False)