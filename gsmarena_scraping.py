import requests
from bs4 import BeautifulSoup
import csv
import os
import time

# Class gsmarena scrap the website phones models and its devices and save to csv file individually.
class Gsmarena():

    # Constructor to initialize common useful varibales throughout the program.
    def __init__(self):
        self.phones = []
        self.features = ["Brand", "Model Name", "Model Image"]
        self.temp1 = []
        self.phones_brands = []
        self.url = 'https://www.gsmarena.com/' # GSMArena website url
        self.new_folder_name = 'GSMArenaDataset' # Folder name on which files going to save.
        self.absolute_path = os.popen('pwd').read().strip() + '/' + self.new_folder_name  # It create the absolute path of the GSMArenaDataset folder.

    # This function crawl the html code of the requested URL.
    def crawl_html_page(self, sub_url):

        url = self.url + sub_url  # Url for html content parsing.

        # Handing the connection error of the url.
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')  # It parses the html data from requested url.
            return soup

        except ConnectionError as err:
            print("Please check your network connection and re-run the script.")
            exit()

        except Exception:
            print("Please check your network connection and re-run the script.")
            exit()

    # This function crawl mobile phones brands and return the list of the brands.
    def crawl_phone_brands(self):
        phones_brands = []
        soup = self.crawl_html_page('makers.php3')
        table = soup.find_all('table')[0]
        table_a = table.find_all('a')
        for a in table_a:
            temp = [a['href'].split('-')[0], a.find('span').text.split(' ')[0], a['href']]
            phones_brands.append(temp)
        return phones_brands

    # This function crawl mobile phones brands models links and return the list of the links.
    def crawl_phones_models(self, phone_brand_link):
        links = []
        nav_link = []
        soup = self.crawl_html_page(phone_brand_link)
        nav_data = soup.find(class_='nav-pages')
        if not nav_data:
            nav_link.append(phone_brand_link)
        else:
            nav_link = nav_data.findAll('a')
            nav_link = [link['href'] for link in nav_link]
            nav_link.append(phone_brand_link)
            nav_link.insert(0, nav_link.pop())
        for link in nav_link:
            soup = self.crawl_html_page(link)
            data = soup.find(class_='section-body')
            for line1 in data.findAll('a'):
                links.append(line1['href'])

        return links

    # This function crawl mobile phones specification and return the list of the all devices list of single brand.
    def crawl_phones_models_specification(self, link, phone_brand):
        phone_data = {}
        soup = self.crawl_html_page(link)
        model_name = soup.find(class_='specs-phone-name-title').text
        model_img_html = soup.find(class_='specs-photo-main')
        model_img = model_img_html.find('img')['src']
        phone_data.update({"Brand": phone_brand})
        phone_data.update({"Model Name": model_name})
        phone_data.update({"Model Image": model_img})
        temp = []
        for data1 in range(len(soup.findAll('table'))):
            table = soup.findAll('table')[data1]
            for line in table.findAll('tr'):
                temp = []
                for l in line.findAll('td'):
                    text = l.getText()
                    text = text.strip()
                    text = text.lstrip()
                    text = text.rstrip()
                    text = text.replace("\n", "")
                    temp.append(text)
                    if temp[0] in phone_data.keys():
                        temp[0] = temp[0] + '_1'
                    if temp[0] not in self.features:
                        self.features.append(temp[0])
                if not temp:
                    continue
                else:
                    phone_data.update({temp[0]: temp[1]})
        return phone_data

    # This function create the folder 'GSMArenaDataset'.
    def create_folder(self):
        if not os.path.exists(self.new_folder_name):
            os.system('mkdir ' + self.new_folder_name)
            print("Creating ", self.new_folder_name, " Folder....")
            time.sleep(6)
            print("Folder Created.")
        else:
            print(self.new_folder_name , "directory already exists")

    # This function check the csv file exists in the 'GSMArenaDataset' directory or not.
    def check_file_exists(self):
        return os.listdir(self.absolute_path)

    # This function save the devices specification to csv file.
    def save_specification_to_file(self):
        phone_brand = self.crawl_phone_brands()
        self.create_folder()
        files_list = self.check_file_exists()
        for brand in phone_brand:
            phones_data = []
            if (brand[0].title() + '.csv') not in files_list:
                link = self.crawl_phones_models(brand[2])
                model_value = 1
                print("Working on", brand[0].title(), "brand.")
                for value in link:
                    datum = self.crawl_phones_models_specification(value, brand[0])
                    datum = { k:v.replace('\n', ' ').replace('\r', ' ') for k,v in datum.items() }
                    phones_data.append(datum)
                    print("Completed ", model_value, "/", len(link))
                    model_value+=1
                with open(self.absolute_path + '/' + brand[0].title() + ".csv", "w")  as file:
                    dict_writer = csv.DictWriter(file, fieldnames=self.features)
                    dict_writer.writeheader()
                    dict_writer.writerows(phones_data)
                print("Data loaded in the file")
            else:
                print(brand[0].title() + '.csv file already in your directory.')


# This is the main function which create the object of Gsmarena class and call the save_specificiton_to_file function.
i = 1
while i == 1:
    if __name__ == "__main__":
        obj = Gsmarena()
        try:
            obj.save_specification_to_file()
        except KeyboardInterrupt:
            print("File has been stopped due to KeyBoard Interruption.")
