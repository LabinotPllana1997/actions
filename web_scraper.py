
from ctypes import c_void_p
import inspect
import os
from typing import Dict
import uuid
#from msilib.schema import CreateFolder
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from uuid import uuid4
import json
import urllib
import pandas as pd
import unittest
import boto3
import sqlalchemy
# import psycopg2_SQLAlchemy_notes as psn
from dotenv import load_dotenv
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from sqlite3 import Cursor

class WebScrape:
    '''
    This class is used to to webscrape. 

    Attributres:
    web URL to Ted Baker website.    
    '''
    def __init__(self, URL) -> None:
        load_dotenv()
        aws_session = boto3.Session(aws_access_key_id=os.environ['aws_access_key_id'], aws_secret_access_key=os.environ['aws_secret_access_key'])
        self.s3_client = aws_session.client('s3')
        self.bucket_name = 'labinotbucket'
        self.engine = sqlalchemy.create_engine(f"{os.environ['DATABASE_TYPE']}+{os.environ['DBAPI']}://{os.environ['pdUSER']}:{os.environ['PASSWORD']}@{os.environ['HOST']}:{os.environ['PORT']}/{os.environ['DATABASE']}")
        # self.table = pd.read_sql_table('ted_baker_trial', self.engine)

        user_input = input('Would you like to run headless mode? [y/n]')
        if user_input == 'y':
            # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            # options.add_argument(f'user-agent={user_agent}')
            options.add_argument("--window-size=1920,1080")
            # options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            # options.add_argument("--disable-extensions")
            # options.add_argument("--proxy-server='direct://'")
            # options.add_argument("--proxy-bypass-list=*")
            options.add_argument("--start-maximized")
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome((ChromeDriverManager().install()), options=options)
        else:
            self.driver = webdriver.Chrome((ChromeDriverManager().install()))

        self.URL = URL
        URL = "https://www.tedbaker.com/uk/c/mens/clothing/shirts/680"
        self.driver.get(URL)


    def accept_cookies(self):
        '''
        Accepts cookies on the Ted Baker website.

        Returns
            .......
            'Cookies accepted' once button is clicked
        '''

        time.sleep(2) # Wait a couple of seconds, so the website doesn't suspect you are a bot
        try:
            # driver.switch_to_frame('gdpr-consent-notice') # This is the id of the frame
            accept_cookies_button = self.driver.find_element(By.XPATH, '//*[@id="consent_prompt_submit"]')
            accept_cookies_button.click()
            print('Cookies accepted')

        except AttributeError: # If you have the latest version of Selenium, the code above won't run because the "switch_to_frame" is deprecated
            # driver.switch_to.frame('gdpr-consent-notice') # This is the id of the frame
            accept_cookies_button = self.driver.find_element(By.XPATH, '//*[@id="consent_prompt_submit"]')
            accept_cookies_button.click()
            print('Attribute Error')
        except:
            pass # cookies did not show

        # return self.driver()


# this is for the 10% sale pop-up, which happens randomly
# // find all elements, then * means any
    def close_pop_up(self) -> webdriver.Chrome:
        '''
        Closes promotion pop-up on the Ted Baker website

        Returns
           .......

        '''
        #time.sleep(20)
        try:
        #    time.sleep(5)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="smc-v5-overlay-87628"]')))
            element = self.driver.find_element(By.XPATH, '//*[@id="smc-v5-overlay-87628"]')
            self.driver.execute_script("""
            var element = arguments[0]
            if (element)
                element.parentNode.removeChild(element);
            """, element
            )

            print('pop up gone!')
        except TimeoutException:
            print('No pop up found')

    
    def click_shirt(self):
        '''
        Clicks on shirt from men's shirt section of website

        Returns
           .......
           prints links of each shirt on the page
        '''

        time.sleep(5)
        shirt_click = self.driver.find_element(By.XPATH, '//*[@id="plp-container"]/a[3]')
        link = shirt_click.get_attribute('href')
        print(link)
        self.driver.get(link)


    def page_scroll(self):
        '''
        Scrolls down page of website

        Returns
           .......
           prints links of each shirt on the page
        '''

        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, 1400)")
        print('page scrolled!') 


    def extract_page_links(self,
        xpath_to_container: str,
        attribute_to_return: str,
        page_to_extract_links: str,
        ):  
        '''
        Extracts page links for all shirts on the mens site

        It does this by iterating through all the a tags in the
        containter of the site, getting the 'href' attribute, 
        then appending this to a list

        Returns
           .......
           prints the list of all the href's of each shirt and 
           prints the length of the list, to check if all of the
           shirts have been extracted 
        '''
        
    # if anything messes up, xpath to container is '//div[@data-testid="plp-grid"]//a'
        self.driver.get(page_to_extract_links)
        page_link_list = []
        page_container = self.driver.find_elements(by=By.XPATH, value=xpath_to_container)
        #print(page_container) # print a list of selenium web elements

        for item in page_container:
            link_to_page = item.get_attribute(attribute_to_return)
            print(link_to_page)
            #iterating and adding to the empty list
            page_link_list.append(link_to_page)

        print(page_link_list)
        print(len(page_link_list))
        return page_link_list


    def retrieve_info(self): 
        '''
        Clicks on each shirt, extracts all the necessary info

        Returns:
           .......
           a list of dictionaries, with each dictionary having the 
           following keys: price, product code, description, UUID
           and image links
        '''
        product_page_list = self.extract_page_links('//div[@data-testid="plp-grid"]//a', 'href', self.URL)
        # all_prices = []
        # all_product_names = []
        # all_product_descriptions = []
        product_information = []
        #product_unique_uuid = []
        parent_dir = "/home/labinotpllana1997/Documents/raw_data"
        for product_page in product_page_list:
            self.driver.get(product_page)
            self.close_pop_up()
            product_information_dictionary = dict()
            try:
                price = self.driver.find_element(By.XPATH, '//h2[@class="product-pricesstyled__Price-sc-1hhcrv3-1 hJwDit"]').text
                # print(price)
                # all_prices.append(price)
            except:
                price = self.driver.find_element(By.XPATH, '//h2[@class="product-pricesstyled__Price-sc-1hhcrv3-1 fArSfN"]').text
                # print(price)
                # all_prices.append(price)
            product_information_dictionary['price'] = price
            
            product_names = self.driver.find_element(By.XPATH, '//h1[@class="product-detailsstyled__ProductName-tuq96a-0 dnwiVs"]').text
            # print(product_names)
            # all_product_names.append(product_names)
            product_information_dictionary['name'] = product_names
            
            product_descriptions = self.driver.find_element(By.XPATH, '//h2[@class="product-detailsstyled__ProductDescription-tuq96a-2 bbToXQ"]').text
            # print(product_descriptions)
            # all_product_descriptions.append(product_descriptions)
            product_information_dictionary['description'] = product_descriptions
            #product_information.append(product_information_dictionary)

            current_URL = self.driver.current_url.split('/')[-1]
            print(str(uuid4()))
            product_information_dictionary['product_code'] = self.get_product_code()
            product_information_dictionary['uuid'] = self.get_unique_id()
            product_information_dictionary['image_link'] = self.get_images_after_click()
            product_information.append(product_information_dictionary)
            file_name = f'{parent_dir}/{product_information_dictionary["product_code"]}/data.json'
            self.save_locally(product_information_dictionary, parent_dir, file_name)
            self.s3_upload(file_name, self.bucket_name, f'{product_information_dictionary["product_code"]}.json')
            self.upload_images_to_s3(product_information_dictionary)

        dfsf = pd.DataFrame(product_information)
        print(dfsf)
        #self.upload_to_rds_database_using_pandas(dfsf, 'ted_baker_trial')
        self.upload_rds_without_rescrape(product_information, 'ted_baker_trial')
        # print(df)
        return product_information


    def upload_rds_without_rescrape(self,
        product_information: list,
        table_name: str,
        ):
        '''
        This method will check the table on RDS database using sqlalchemy.
        It will then generate a list of product codes from the dataframe, 
        check if new entry exists and append the table if it does not.

        Args:
            product_information_dictionary: dict
            table_name: str

        Returns:
            None
        '''

        if sqlalchemy.inspect(self.engine).has_table(table_name):
            print('This table exists in postgresql. Beginning the upload..')
            unique_product_list = self.table["product_code"].tolist()
            print(self.table['product_code'])
            print(unique_product_list)

            for new_entry in product_information:
                rds_new_entry = pd.DataFrame([new_entry])
                new_entry_product_code = new_entry['product_code']

                if new_entry_product_code not in unique_product_list:
                    rds_new_entry.to_sql(table_name, self.engine, if_exists='append')
                    print('Uploading new entry to RDS database..')
            else:
                print('There we no new entries with this scrape.')
        else:
            print('This table does not exist in postgresql. Running method upload_to_rds_database_using_pandas..')
            self.upload_to_rds_database_using_pandas(pd.DataFrame(product_information), table_name)


    def save_locally(self,
        product_information_dictionary: dict,
        parent_dir: str,
        file_name: str,
        ):
        '''
        saves data in json file in the path /home/labinotpllana1997/Documents/raw_data
        by calling a another method to create a JSON file
        '''

        if os.path.exists(parent_dir)== False:
            os.makedirs(parent_dir)
        if os.path.exists(f'{parent_dir}/{product_information_dictionary["product_code"]}')== False:
            os.makedirs(f'{parent_dir}/{product_information_dictionary["product_code"]}')
        #self.create_json_file(product_information_dictionary, file_name)
        with open(f'{file_name}', 'w') as json_file:
            json.dump(product_information_dictionary, json_file)
        self.s3_upload(file_name, self.bucket_name, f'{product_information_dictionary["image_link"]}.jpg')

    def s3_upload(self,
        file_name: str,
        bucket_name: str,
        object_name: str,
        ):
        """
        Uploads to s3 bucket
        
        Args:
            filename (str): The filename on the local machine
            bucket_name (str): The name of the S3 bucket where the object is to be dumped
            object_name (str): The name to save the object as.
        
        Returns:
            None
        """
        # response = s3_client.upload_file(file_name, bucket, object_name)
        self.s3_client.upload_file(file_name, bucket_name, object_name)


    def create_json_file(self,
        product_information_dictionary: dict,
        file_name: str,
        ):
        with open(f'{file_name}/data.json', 'w') as json_file:
            json.dump(product_information_dictionary, json_file)


    def upload_to_rds_database_using_pandas(self,
        dataframe,
        table_name: str,
        ):
        dataframe.to_sql(table_name, self.engine, if_exists='append')


    def get_images_from_container(self,
        xpath_to_images: str,
        attribute_to_return: str,
        page_to_extract_images: str,
        ):
        '''
        gets image links for all products
        '''
        self.driver.get(page_to_extract_images)
        container = self.driver.find_elements(by=By.XPATH, value=xpath_to_images)
        container_images = []
        for image in container[:5]:
            image_src = image.get_attribute(attribute_to_return)
            print(image_src)
            container_images.append(image_src)
            self.upload_images_to_s3()

        print(container_images)
        return container_images


    def get_images_after_click(self,
        ):
        '''
        gets image links for all products
        '''
        img_link = self.driver.find_element(By.XPATH, '//div[@data-swiper-slide-index="0"]//img').get_attribute('src')
        print(img_link)

        return img_link

        #if shit hits the fan, this was the xpath and attribute, respecitvely
        #(By.XPATH, '//div[@data-swiper-slide-index="0"]//img').get_attribute('src')


    def download_images(self, image_link: str, img_name: str) -> None:
        """This function downloads an image from a URL
        Args:
            image_link (str): The link to the image to be downloaded
            img_name (str): The reference name for the image
        Returns:
            None
        """
        path  = img_name + '.jpg'
        urllib.request.urlretrieve(image_link, path)


    def upload_images_to_s3(self,
        product_information_dictionary: dict,
        ):
        with tempfile.TemporaryDirectory() as tempdir:
            self.download_images(product_information_dictionary["image_link"], f'{tempdir}/{product_information_dictionary["product_code"]}')
            tempdir_img = f'{tempdir}/{product_information_dictionary["product_code"]}'
            self.s3_upload(f'{tempdir_img}.jpg', self.bucket_name, f'{product_information_dictionary["product_code"]}.jpg')


    def get_product_code(self):
        '''
        extracts product code from item URL

        Returns:
           .......
           product code: the last unique part of the URL for
           each item
        '''
        product_code = self.driver.current_url.split('/')[-1]
        print(product_code)
        return product_code


    def get_product_code(self):
        product_code = self.driver.current_url.split('/')[-1]
        print(product_code)
        return product_code

    def get_unique_id(self):
        uuid = str(uuid4())
        return uuid

if __name__ == '__main__':
    ted_baker_scrape = WebScrape("https://www.tedbaker.com/uk/c/mens/clothing/shirts/680")
    ted_baker_scrape.accept_cookies()
    ted_baker_scrape.close_pop_up()

    ted_baker_scrape.retrieve_info()
    #ted_baker_scrape.save_locally()


