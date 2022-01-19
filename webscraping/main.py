# -*- coding: utf-8 -*-
import argparse
import yaml

from crawler.crawler import MineralsNet

def main():
    parser = argparse.ArgumentParser(description="Download data/details of gemstones")

    parser.add_argument("--destination", "-d", type=str, choices=["local", "cloud"], default="local", help="Local or cloud destination")
    parser.add_argument("--mode", "-m", type=str, choices=["images", "details", "full"], default="full", help="Download images, details or both")
    parser.add_argument("--path", "-p", type=str, default="data", help="Foder to store data")
    parser.add_argument("--coordinates", "-c", type=bool, default=True, help="Generate coordinates from localities")

    args = parser.parse_args()

    crawler = MineralsNet(args.path)

    if args.mode == "images":
        crawler.download_images()
    elif args.mode == "details":
        crawler.download_information()
    else:
        crawler.download_images()
        crawler.download_information()

    if args.destination == "cloud":
        with open("config.yaml", "r") as stream:
            try:
                config = yaml.safe_load(stream)
                crawler.save_to_cloud(config)
            except yaml.YAMLError as exc:
                print(exc)

    if args.coordinates == True:
        crawler.retrieve_coordinates_from_countries(config)

if __name__ == "__main__":
    main()