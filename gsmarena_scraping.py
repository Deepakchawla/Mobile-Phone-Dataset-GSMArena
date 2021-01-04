import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Set

import bs4
import requests
from bs4 import BeautifulSoup, Tag


class GSMArena:

    def __init__(self):
        self.url: str = "https://www.gsmarena.com/"
        self.data_folder_name: str = "GSMArenaDataset"
        self.data_folder_path: Path = Path(__file__).parent / self.data_folder_name

    # This function crawl the html code of the requested URL.
    def crawl_html_page(self, sub_url) -> bs4.BeautifulSoup:
        url = self.url + sub_url  # Url for html content parsing.
        header={"User-Agent":"#user agent of your system  "}
        time.sleep(30)  #SO that your IP does not gets blocked by the website
        # Handing the connection error of the url.
        try:
            page = requests.get(url,timeout= 5, headers=header)
            soup = BeautifulSoup(page.text, 'html.parser')  # It parses the html data from requested url.
            return soup

        except ConnectionError as err:
            print("Please check your network connection and re-run the script.")
            exit()

        except Exception:
            print("Please check your network connection and re-run the script.")
            exit()

    # This function crawl mobile phones brands and return the list of the brands.
    def crawl_phone_brands(self) -> List[Tuple[str, str]]:
        """
        Gathers phone brands and their primary nav links
        """
        brand_metadata = []
        crawled_response: bs4.BeautifulSoup = self.crawl_html_page("makers.php3")
        crawled_response_table_tag: bs4.element.Tag = crawled_response.find_all("table")[0]
        """
        <table>
        <tr><td><a href="acer-phones-59.php">Acer<br/><span>100 devices</span></a></td>
        <td><a href="alcatel-phones-5.php">alcatel<br/><span>400 devices</span></a></td></tr>
        </table>
        """
        crawled_response_table_hyperlinks: List[
            bs4.element.Tag
        ] = crawled_response_table_tag.find_all("a")
        """
        [<a href="acer-phones-59.php">Acer<br/><span>100 devices</span></a>, 
        <a href="alcatel-phones-5.php">alcatel<br/><span>400 devices</span></a>]
        """
        for hyperlink in crawled_response_table_hyperlinks:
            brand_name_link = (hyperlink["href"].split("-")[0], hyperlink["href"])
            """
            brand_name_link = [("acer", 'acer-phones-59.php'), (...)]
            """
            brand_metadata.append(brand_name_link)
        return brand_metadata

    # This function crawl mobile phones brands models links and return the list of the links.
    def crawl_phones_models(self, phone_brand_link) -> Set[Tag]:
        """
        Gathers models per brand and their nav links
        """
        phone_model_links = set()
        nav_links = [phone_brand_link]
        crawled_response: bs4.BeautifulSoup = self.crawl_html_page(phone_brand_link)
        crawled_response_nav_page_tag = crawled_response.find(class_="nav-pages")
        """
        <div class="nav-pages">
        <span>Pages:</span>
        <strong>1</strong> <a href="acer-phones-f-59-0-p2.php">2</a> <a href="acer-phones-f-59-0-p3.php">3</a> 
        </div>
        """
        if crawled_response_nav_page_tag:
            crawled_response_hyperlinks: List[
                bs4.element.Tag
            ] = crawled_response_nav_page_tag.findAll("a")
            """
            [<a href="acer-phones-f-59-0-p2.php">2</a>, <a href="acer-phones-f-59-0-p3.php">3</a>]
            """
            nav_links.extend(link["href"] for link in crawled_response_hyperlinks)
            """
            nav_links = ['acer-phones-59.php', 'acer-phones-f-59-0-p2.php', 'acer-phones-f-59-0-p3.php']
            """
        for link in nav_links:
            crawled_response: bs4.BeautifulSoup = self.crawl_html_page(link)
            crawled_response_section_body_tag = crawled_response.find(class_="section-body")
            for crawled_response_hyperlinks in crawled_response_section_body_tag.findAll(
                "a"
            ):
                phone_model_links.add(crawled_response_hyperlinks["href"])
                """
                crawled_response_hyperlinks:
                <a href="acer_chromebook_tab_10-9139.php">
                <img src="https://fdn2.gsmarena.com/vv/bigpic/acer-chromebook-tab-10.jpg" 
                title="Acer Chromebook Tab 10 tablet. Announced Mar 2018. Features 9.7″  
                display, Rockchip RK3399 chipset, 5 MP primary camera, 2 MP front camera, 
                4500 mAh battery, 32 GB storage, 4 GB RAM."/><strong><span>Chromebook Tab 10</span></strong></a>
                """
        """
        phone_model_links: ('acer_chromebook_tab_10-9139.php', ...)
        """
        return phone_model_links

    # This function crawl mobile phones specification and return the list of the all devices list of single brand.
    def crawl_phones_models_specification(self, link, phone_brand, field_names) -> Dict[str, str]:
        """
        Gathers model spec per model per brand
        """
        phone_data = {}
        crawled_response: bs4.BeautifulSoup = self.crawl_html_page(link)
        model_name = crawled_response.find(class_="specs-phone-name-title").text
        """
        'Acer Iconia Tab A110'
        """
        model_img_html = crawled_response.find(class_="specs-photo-main")
        """
        <div class="specs-photo-main">
        <a href="acer_iconia_tab_a110-pictures-5067.php"><img alt="Acer Iconia Tab A110
        MORE PICTURES" src="https://fdn2.gsmarena.com/vv/bigpic/acer-iconia-tab-a210.jpg"/></a>
        </div>
        """
        model_img = model_img_html.find("img")["src"]
        """
        'https://fdn2.gsmarena.com/vv/bigpic/acer-iconia-tab-a210.jpg'
        """
        phone_data.update({"Brand": phone_brand})
        phone_data.update({"Model Name": model_name})
        phone_data.update({"Model Image": model_img})
        for data1 in range(len(crawled_response.findAll("table"))):
            table = crawled_response.findAll("table")[data1]
            for line in table.findAll("tr"):
                temp = []
                for l in line.findAll("td"):
                    text = l.getText()
                    text = text.strip()
                    text = text.lstrip()
                    text = text.rstrip()
                    text = text.replace("\n", "")
                    temp.append(text)
                    if temp[0] in phone_data.keys():
                        temp[0] = temp[0] + "_1"
                phone_data.update({temp[0]: temp[1]}) if temp else None
                field_names.add(temp[0]) if temp else None
        """
        {'Brand': 'acer', 'Model Name': 'Acer Iconia Tab A110', 
        'Model Image': 'https://fdn2.gsmarena.com/vv/bigpic/acer-iconia-tab-a210.jpg', 
        'Technology': 'No cellular connectivity', '2G bands': 'N/A', 'GPRS': 'No', 'EDGE': 'No',....}
        """
        return phone_data

    # This function save the devices specification to csv file.
    def save_specification_to_file(self) -> None:
        """
        Saves spec to file for each model for each brand found on the GSMArena website

        Technical terms:
            metadata here to refers to basic naming and nav links
        Flow:
            crawl brands and get nav links
            craw models for each brand and update nav link list
            for each nav link get the spec data
            Write the spec data for each brand to a csv

        FIXME: This flow suffers from status code 429 due to Too many requests.
        """
        print("Preparing data...")
        self.data_folder_path.mkdir(exist_ok=True)
        phone_brands_metadata = self.crawl_phone_brands()
        for brand_metadata in phone_brands_metadata:
            brand_name, brand_page_link = brand_metadata
            phones_data = []
            field_names = {"Brand", "Model Name", "Model Image"}
            if self.data_folder_path / f"{brand_name.title()}.csv" in self.data_folder_path.iterdir():
                print(brand_name.title() + f".csv file already in {self.data_folder_name}/")
            else:
                model_links_metadata = self.crawl_phones_models(brand_page_link)
                model_value = 1
                print("Working on", brand_name.title(), "brand.")
                for model_link in model_links_metadata:
                    phone_specification_data = self.crawl_phones_models_specification(
                        model_link, brand_name, field_names
                    )
                    phone_specification_data = {
                        k: v.replace("\n", " ").replace("\r", " ")
                        for k, v in phone_specification_data.items()
                    }
                    phones_data.append(phone_specification_data)
                    print("Completed ", model_value, "/", len(model_links_metadata))
                    model_value += 1
                with open(self.data_folder_path / f"{brand_name.title()}.csv", "w") as file:
                    dict_writer = csv.DictWriter(file, fieldnames=field_names)
                    dict_writer.writeheader()
                    str_phones_data = json.dumps(phones_data)
                    encoded = str_phones_data.encode("utf-8")
                    load_list = json.loads(encoded)
                    for dicti in load_list:
                        dict_writer.writerow(
                            {k: v.encode("utf-8") for k, v in dicti.items()}
                        )
                print(f"Data loaded in {self.data_folder_name}/{brand_name.title()}.csv file")


try:
    # This is the main function which create the object of Gsmarena class
    # and call the save_specificiton_to_file function.
    GSMArena().save_specification_to_file()
except ConnectionError as connErr:
    print(f"Connection Error: {connErr}")
