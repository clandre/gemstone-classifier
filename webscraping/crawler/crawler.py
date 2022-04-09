# -*- coding: utf-8 -*-

import os
import sys
import json
import re
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

from utils.utils import create_dir, insert_gemstone, update_gemstone_images, upload_file, retrieve_coordinates_from_countries


class Crawler(ABC):
    """
    Class to represent crawler

    ...
    
    Attributes
    -----------
    download_location: str
        Path to store downloaded files
    homepage: str
        Link of site
    """
    def __init__(self, download_location: str, destination = None):
        self.download_location = download_location
        self.homepage = None

    def get_homepage(self) -> str:
        """
        Returns homepage
        
        Returns
        -------
            homepage (str): Site homepage
        """
        return self.homepage

    @abstractmethod
    def download_images(self):
        """
        Method to download images

        Returns
        -------
            None
        """
        pass

    @abstractmethod
    def download_information(self):
        """
        Method to download additional information of gemstone

        Returns
        -------
            None
        """
        pass

    def save_to_storage(self, configuration: dict):
        """
        Method to save image
        
        Returns
        -------
            None
        """


        for root, subdirs, files in os.walk(self.download_location):
            for image in [file for file in files if file.endswith('.jpg')]:
                filename = (self.download_location + os.sep + os.path.basename(root) + os.sep + image).replace("\\", "/")
                destination = (self.download_location.split(os.sep)[0] + os.sep + os.path.basename(root) + os.sep + image).replace("\\", "/")

                print('Uploading file: ' + destination)
                upload_file(configuration, filename, destination)

    @abstractmethod
    def save_to_database(self, configuration: dict):
        """
        Method to save additional information of gemstone

        Returns
        -------
            None
        """
        pass

    @abstractmethod
    def get_gemstone_list(self) -> dict:
        """
        Method to get list of gemstones availables at site

        Returns
        -------
            gemstone_info (dict): A dictionary containing gemstone name and link
        """
        pass

    @abstractmethod
    def get_gemstones_names(self, table) -> ResultSet:
        """
        Method to extract gemstone name from site

        Returns
        -------
            gemstone_info (dict): A dictionary containing gemstone name and link
        """
        pass

    def get_page(self, url: str) -> bs:
        """
        Method to access an url

        Returns
        -------
            BeautifoulSoup
        """

        print('Acessing page: ' + url)
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        return soup

    def retrieve_coordinates_from_countries(self, configuration: dict):
        """
        Function to retrieve coordinates from countries

        Parameters
        -----------

            credentials: dict
                credentials to connect no database

            Returns
            --------
                None
        """

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
                        img_link = self.homepage + link.get('src').replace('-t','')
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

    def save_to_database(self, configuration: dict):
        for root, subdirs, files in os.walk(self.download_location):
            gemstone_info = {}

            if root != self.download_location:
                with open(os.path.abspath(root) + os.sep + 'info.json', 'r', encoding='utf8') as f:
                    gemstone_info = json.load(f)
                    gemstone_info['Images'] = []

                for image in [file for file in files if file.endswith('.jpg')]:
                    filename = (self.download_location.split(os.sep)[0] + os.sep + os.path.basename(root) + os.sep + image).replace("\\", "/")
                    gemstone_info['Images'].append(filename)

                gemstone_name = root.split("\\")[2]

                if not(insert_gemstone(configuration, "gemstone", gemstone_name, gemstone_info)):
                    print("Failed to insert record: " + gemstone_info['name'])
        
        self.retrieve_coordinates_from_countries(configuration)


class GemSelect(Crawler):
    def __init__(self, download_location: str):
        super().__init__(download_location)

        self.homepage = "https://www.gemselect.com/"
        self.gemstone_dict = self.get_gemstone_list()

    def get_gemstone_list(self) -> dict:
        url = self.homepage + 'all-gemstones.php'
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        table = soup.find_all('a', class_='in')
        
        return self.get_gemstones_names(table)

    def get_gemstones_names(self, table) -> dict:
        names_paths = {}
        pattern = re.compile(r"(([a-zA-z]-?\/?)+)+.php")

        for data in table:
            for name in data.find_all('h3'):
                if(name.text != '' and not name.text.startswith("Color-Change")):
                    link = data.get("href")
                    if not link.startswith("https://www.gemselect.com/"):
                        names_paths[name.text] = re.search(pattern, link).group()
        return names_paths

    def download_images(self) -> None:
        for key, value in self.gemstone_dict.items():
            image_link = ''
            print('-'*8, key, '-'*8)
            gem_link = self.homepage + value
            soup = self.get_page(gem_link)
                
            table_images = soup.find_all('img', class_='img_a')
                
            if(table_images):
                create_dir(self.download_location + os.sep + key)

                for data in table_images:
                    img_link = data.get('data-src')
                    
                    print("Downloading image: " + img_link)
                    r = requests.get(img_link, stream=True)
                    if r.status_code == 200:    # OK
                        with open(self.download_location + os.sep + key + os.sep + img_link.split('/')[-1], 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)

    def save_to_database(self, configuration: dict):
        for root, subdirs, files in os.walk(self.download_location):
            gemstone_images = []

            if root != self.download_location:
                for image in [file for file in files if file.endswith('.jpg')]:
                    filename = (self.download_location.split(os.sep)[0] + os.sep + os.path.basename(root) + os.sep + image).replace("\\", "/")
                    gemstone_images.append(filename)

                gemstone_name = root.split("\\")[2]

                if not(update_gemstone_images(configuration, "gemstone", gemstone_name, gemstone_images)):
                    print("Failed to add images: " + gemstone_name)

    def download_information(self):
        pass


class RasavGems(Crawler):
    def __init__(self, download_location: str):
        super().__init__(download_location)

        self.homepage = "https://www.rasavgems.com/"
        self.gemstone_dict = self.get_gemstone_list()

    def get_gemstone_list(self) -> dict:
        url = self.homepage + 'Choose-gemstone.html'
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        table = soup.find_all("table", class_="productlists")
        
        return self.get_gemstones_names(table)

    def get_gemstones_names(self, table) -> ResultSet:
        names_paths = {}
        for data in table:
            for name in data.find_all('a'):
                link = name.get("href")
                names_paths[link.split('.')[0].capitalize()] = link
        return names_paths

    def download_images(self) -> None:
        for key, value in self.gemstone_dict.items():
            image_link = ''
            print('-'*8, key, '-'*8)
            gem_link = self.homepage + value

            soup = self.get_page(gem_link)
                
            # table_images = soup.find_all('img', id='ImgBtnImagePath')

            print(soup)
            from time import sleep
            sleep(10)
            table_images = soup.find_all(id="ImgBtnImagePath3018")#, re.compile("^ImgBtnImagePath"))
            print(table_images)

            print(soup.find_all("table", class_="productlist"))
                
            # if(table_images):
            #     create_dir(self.download_location + os.sep + key)

            #     for data in table_images:

            #         print(data)

            #         img_link = self.homepage + data.get('src')
                    
            #         print("Downloading image: " + str(img_link))
                    # r = requests.get(img_link, stream=True)
                    # if r.status_code == 200:    # OK
                    #     with open(self.download_location + os.sep + key + os.sep + img_link.split('/')[-1], 'wb') as f:
                    #         r.raw.decode_content = True
                    #         shutil.copyfileobj(r.raw, f)
            break

    def save_to_database(self, configuration: dict):
        for root, subdirs, files in os.walk(self.download_location):
            gemstone_images = []

            if root != self.download_location:
                for image in [file for file in files if file.endswith('.jpg')]:
                    filename = (self.download_location.split(os.sep)[0] + os.sep + os.path.basename(root) + os.sep + image).replace("\\", "/")
                    gemstone_images.append(filename)

                gemstone_name = root.split("\\")[2]

                if not(update_gemstone_images(configuration, "gemstone", gemstone_name, gemstone_images)):
                    print("Failed to add images: " + gemstone_name)

    def download_information(self):
        pass