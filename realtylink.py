import json
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ScraperRealEstate:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.chrome_options)
        self.driver.maximize_window()

    def click_next_button(self):
        btn_click = '//*[@id="divWrapperPager"]/ul/li[4]'
        next_button = self.driver.find_element(By.XPATH, btn_click)
        next_button.click()
        time.sleep(2)

    def extract_image_urls(self, soup):
        summary_photos = soup.find('div', class_='summary-photos')
        image_tags = summary_photos.find_all('img')
        image_urls = []
        for img in image_tags:
            if 'src' in img.attrs:
                image_urls.append(img['src'])
        return image_urls

    def extract_number_of_rooms(self, soup):
        number_rooms_tag = soup.find('div', attrs={'class': 'col-lg-3 col-sm-6 cac'})
        number_rooms = number_rooms_tag.text.strip().split(' ')[0] if number_rooms_tag else None
        return number_rooms

    def extract_title(self, soup):
        title_tag = soup.find('span', attrs={'data-id': 'PageTitle'})
        title = title_tag.text.strip() if title_tag else None
        return title

    def extract_address(self, soup):
        address_tag = soup.find('h2', attrs={'itemprop': 'address'})
        address = address_tag.text.strip() if address_tag else None
        return address

    def extract_region(self, soup):
        address_tag = soup.find('h2', attrs={'itemprop': 'address'})
        address = address_tag.text.strip() if address_tag else None
        region = address.split(',', 1)[1].strip() if address else None
        return region

    def extract_description(self, soup):
        description_tag = soup.select_one('div[itemprop="description"]')
        description = description_tag.text.strip() if description_tag else None
        return description

    def extract_price(self, soup):
        price_tag = soup.find('meta', itemprop='price')
        price = price_tag['content'] if price_tag else None
        return price

    def extract_estate_area(self, soup):
        estate_area_tag = soup.find('div', attrs={'class': 'carac-value'})
        estate_area = estate_area_tag.text.strip().split(' ')[0] if estate_area_tag else None
        return estate_area

    def get_list_urls(self):
        all_data = []
        max_pages = 3

        for _ in range(max_pages -1):
            self.driver.get('https://realtylink.org/en/properties~for-rent')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.thumbnail.property-thumbnail-feature.legacy-reset')))
            soup_main = BeautifulSoup(self.driver.page_source, 'html.parser')
            properties = soup_main.find_all('div', attrs={'class': 'thumbnail property-thumbnail-feature legacy-reset'})

            for property in properties:
                property_url = 'https://realtylink.org' + property.find('a').get('href')
                all_data.append(property_url)

            self.click_next_button()

        return all_data

    def get_data(self, all_data):
        list_all_data = []
        for url in all_data:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.find_element(By.CSS_SELECTOR, 'span[data-id="PageTitle"]'))
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            title = self.extract_title(soup)
            region = self.extract_region(soup)
            address = self.extract_address(soup)
            description = self.extract_description(soup)
            image_urls = self.extract_image_urls(soup)
            price = self.extract_price(soup)
            number_rooms = self.extract_number_of_rooms(soup)
            estate_area = self.extract_estate_area(soup)
            date_publication = None   # Could not find the required object on the site

            add_data = {
                "url": url,
                "title": title,
                "region": region,
                "address": address,
                "description": description,
                "image_urls": image_urls,
                "price": price,
                "number_rooms": number_rooms,
                "estate_area": estate_area,
                "date_publication": date_publication
            }

            list_all_data.append(add_data)

        with open('result.json', 'w', encoding='utf-8') as json_file:
            json.dump(list_all_data, json_file, ensure_ascii=False, indent=4)

        self.driver.quit()
        self.driver.close()


if __name__ == '__main__':
    bot = ScraperRealEstate()
    urls = bot.get_list_urls()
    data = bot.get_data(urls)