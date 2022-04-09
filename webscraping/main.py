# -*- coding: utf-8 -*-

import os

import argparse
import yaml

from crawler.crawler import MineralsNet, GemSelect, RasavGems

def main():
    parser = argparse.ArgumentParser(description="Download data/details of gemstones")

    parser.add_argument("--destination", "-d", type=str, choices=["local", "cloud"], default="local", help="Local or cloud destination")
    parser.add_argument("--mode", "-m", type=str, choices=["images", "details", "full"], default="full", help="Download images, details or both")
    parser.add_argument("--path", "-p", type=str, default="data", help="Foder to store data")
    parser.add_argument("--sites", "-s", nargs="+", default=["MineralsNet", "GemSelect"])

    args = parser.parse_args()

    for site in args.sites:
        # Define crawler
        if site == "MineralsNet":
            crawler = MineralsNet(args.path + os.sep + site)
        elif site == "GemSelect":
            crawler = GemSelect(args.path + os.sep + site)

        print("Searching information on: " + crawler.get_homepage())

        # Execute search
        if args.mode == "images":
            crawler.download_images()
        elif args.mode == "details":
            crawler.download_information()
        else:
            crawler.download_images()
            crawler.download_information()

        if args.destination == "cloud":
            with open("../utils/config.yaml", "r") as stream:
                try:
                    config = yaml.safe_load(stream)
                    crawler.save_to_storage(config)
                    crawler.save_to_database(config)
                    
                except yaml.YAMLError as exc:
                    print(exc)

if __name__ == "__main__":
    main()