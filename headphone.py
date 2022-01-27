import scrapy

from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

from scrapy.shell import inspect_response
from scrapy.selector import Selector

import traceback

import random

from selenium.webdriver.common.action_chains import ActionChains

import logging


class HeadphoneSpider(scrapy.Spider):
    name = 'headphone'
    allowed_domains = ['www.amazon.de']

    def start_requests(self):
        yield SeleniumRequest(url='https://www.amazon.de/s?k=headphones&ref=nb_sb_noss', callback=self.parse_item)
    



# ------------ DECISION MAKER
    def parse_item(self, response):
        self.driver = response.meta['driver']
        try: # accept cookies
            self.driver.find_element(By.ID, 'sp-cc-accept').click()
        except:
            pass

        if not self.driver.current_url == 'https://www.amazon.de/s?k=headphones&ref=nb_sb_noss':
            self.driver.get('https://www.amazon.de/s?k=headphones&ref=nb_sb_noss')



        url_list = []
        for i in range(19):
            response = Selector(text=self.driver.page_source)
            for url in response.css('h2 > a.a-link-normal.s-link-style.a-text-normal::attr(href)').getall():
                url_list.append(url)
            self.driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-item.s-pagination-next').click()
            time.sleep(3)
        random.shuffle(url_list)

        x = 0
        with open('url_list.txt', 'w') as file:
            for url in url_list:
                x += 1
                file.write(f'{x}. {url}\n')
        
        with open('un_url_list.txt', 'w') as file:
                file.write('\n')


        x = 0
        for url in url_list:
            print(url)
            try:
                self.driver.get('https://www.amazon.de' + url)
                response = Selector(text=self.driver.page_source)
                
                colour_choice =  '//span[@class="a-size-base a-color-secondary" and contains(text(), "Colour Name:")]/parent::div/parent::div/parent::div/parent::span/following-sibling::div//li[not(contains(@class, "swatch-prototype"))]'
                if not response.xpath(colour_choice).getall():
                    colour_choice = '//ul[@class="a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches"]/li'

                style_choice =  '//span[@class="a-size-base a-color-secondary" and contains(text(), "Style Name:")]/parent::div/parent::div/parent::div/parent::span/following-sibling::div//li[not(contains(@class, "swatch-prototype"))]'
                if not response.xpath(style_choice).getall():
                    style_choice = '//label[@class="a-form-label" and contains(text(), "Style")]/parent::div/following-sibling::ul/li'

                pattern_choice =  '//span[@class="a-size-base a-color-secondary" and contains(text(), "Pattern Name:")]/parent::div/parent::div/parent::div/parent::span/following-sibling::div//li[not(contains(@class, "swatch-prototype"))]'
                if not response.xpath(pattern_choice).getall():
                    pattern_choice = '//label[@class="a-form-label" and contains(text(), "Pattern")]/parent::div/following-sibling::ul/li'
                # [not(contains(@class, "Unavailable"))]


                choice_list = []
                choice_list.append(len(response.xpath(colour_choice).getall()))
                choice_list.append(len(response.xpath(style_choice).getall()))
                choice_list.append(len(response.xpath(pattern_choice).getall()))

                if any(choice_list):
                    print('\n\n\n\n')
                    print(len(response.xpath(colour_choice).getall()))
                    print(len(response.xpath(style_choice).getall()))
                    print(len(response.xpath(pattern_choice).getall()))
                    print('\n\n\n')
                    colour_len = choice_list[0]
                    style_len = choice_list[1]
                    pattern_len = choice_list[2]

                    if colour_len:

                        if not style_len and not pattern_len: # just colour
                            cc = 0
                            for c in range(colour_len):
                                WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))

                                try:
                                    action = ActionChains(self.driver)
                                    element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    action.move_to_element(element)
                                    action.perform()
                                    WebDriverWait(self.driver, 0.3).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))
                                    element.click()
                                except:
                                    time.sleep(0.2)
                                    action = ActionChains(self.driver)
                                    element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    action.move_to_element(element)
                                    action.perform()
                                    time.sleep(0.5)

                                    element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    action = ActionChains(self.driver)
                                    action.move_to_element(element)
                                    action.perform()
                                    WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, colour_choice)))
                                    element.click()


                                WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))
                                yield self.get_info(Selector(text=self.driver.page_source))
                                cc += 1

                        elif style_len and not pattern_len: # colour and style
                            cc = 0
                            for c in range(colour_len):
                                ss = 0
                                for s in range(style_len):
                                    try:
                                        style = self.driver.find_elements(By.XPATH, style_choice + '//div[@class="a-section a-spacing-none swatch-title-text-container"]/following-sibling::div[@class="a-section slots-padding fully-selected"]//div[not(contains(@class, "hidden"))]/span')[ss].get_attribute('innetHTML')
                                    except:
                                        style=''
                                    # if ('Currently unavailable' in style) or ('See available options' in style):
                                    #     pass
                                    # else:
                                    WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))

                                    try:
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.3).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))
                                        element.click()
                                    except:
                                        time.sleep(0.2)
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        time.sleep(0.5)
                                    
                                        element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action = ActionChains(self.driver)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, colour_choice)))
                                        element.click()

                                    try:
                                        WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.3).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))
                                        element.click()
                                    except:
                                        time.sleep(0.2)
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        time.sleep(0.5)
                                    
                                        element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action = ActionChains(self.driver)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                        element.click()

                                    WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))
                                    yield self.get_info(Selector(text=self.driver.page_source))
                                    ss += 1
                                cc += 1

                        elif not style_len and pattern_len: # colour and pattern
                            cc = 0
                            for c in range(colour_len):
                                pp = 0
                                for p in range(pattern_len):
                                    try:
                                        pattern = self.driver.find_elements(By.XPATH, pattern_choice + '//div[@class="a-section a-spacing-none swatch-title-text-container"]/following-sibling::div[@class="a-section slots-padding fully-selected"]//div[not(contains(@class, "hidden"))]/span')[pp].get_attribute('innetHTML')
                                    except:
                                        pattern=''
                                    WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))
                                    
                                    try:
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, colour_choice)))
                                        element.click()
                                    except:
                                        time.sleep(0.2)
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        time.sleep(0.5)
                                    
                                        element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action = ActionChains(self.driver)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, colour_choice)))
                                        element.click()

                                    try:
                                        WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                        element.click()
                                    except:
                                        time.sleep(0.2)
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        time.sleep(0.5)
                                    
                                        element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action = ActionChains(self.driver)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                        element.click()
                                    
                                    WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                    yield self.get_info(Selector(text=self.driver.page_source))
                                    pp += 1
                                cc += 1

                        else: # 3 of them
                            self.driver.save_screenshot('png.png')
                            cc = 0
                            for c in range(colour_len):
                                ss = 0
                                for s in range(style_len):
                                    pp = 0
                                    for p in range(pattern_len):
                                        WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, colour_choice)))
                                        
                                        try:
                                            action = ActionChains(self.driver)
                                            element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action.move_to_element(element)
                                            action.perform()
                                            WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, colour_choice)))
                                            element.click()
                                        except:
                                            time.sleep(0.2)
                                            action = ActionChains(self.driver)
                                            element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action.move_to_element(element)
                                            action.perform()
                                            time.sleep(0.5)
                                    
                                            element = self.driver.find_elements(By.XPATH, colour_choice)[cc]
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action = ActionChains(self.driver)
                                            action.move_to_element(element)
                                            action.perform()
                                            WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, colour_choice)))
                                            element.click()

                                        try:
                                            WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))
                                            action = ActionChains(self.driver)
                                            element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action.move_to_element(element)
                                            action.perform()
                                            WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                            element.click()
                                        except:
                                            time.sleep(0.2)
                                            action = ActionChains(self.driver)
                                            element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action.move_to_element(element)
                                            action.perform()
                                            time.sleep(0.5)
                                    
                                            element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action = ActionChains(self.driver)
                                            action.move_to_element(element)
                                            action.perform()
                                            WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                            element.click()
                                        
                                        try:
                                            WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                            action = ActionChains(self.driver)
                                            element = self.driver.find_elements(By.XPATH, pattern_choice)[cc]
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action.move_to_element(element)
                                            action.perform()
                                            time.sleep(0.5)
                                            element.click()
                                        except:
                                            time.sleep(0.2)
                                            action = ActionChains(self.driver)
                                            element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action.move_to_element(element)
                                            action.perform()
                                            WebDriverWait(self.driver, 0.3).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                    
                                            element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            action = ActionChains(self.driver)
                                            action.move_to_element(element)
                                            action.perform()
                                            WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                            element.click()

                                        WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                        yield self.get_info(Selector(text=self.driver.page_source))
                                        pp += 1
                                    ss += 1
                                cc += 1

                    elif style_len:

                        if pattern_len: # style and pattern
                            ss = 0
                            for s in range(style_len):
                                pp = 0
                                for p in range(pattern_len):
                                    try:
                                        pattern = self.driver.find_elements(By.XPATH, pattern_choice + '//div[@class="a-section a-spacing-none swatch-title-text-container"]/following-sibling::div[@class="a-section slots-padding fully-selected"]//div[not(contains(@class, "hidden"))]/span')[pp].get_attribute('innetHTML')
                                    except:
                                        pattern=''
                                    # if ('Currently unavailable' in style) or ('See available options' in pattern):
                                    #     pass
                                    # else:
                                    WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))

                                    try:
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                        element.click()
                                    except:
                                        time.sleep(0.2)
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        time.sleep(0.5)
                                    
                                        element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action = ActionChains(self.driver)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                        element.click()

                                    try:
                                        WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                        element.click()
                                    except:
                                        time.sleep(0.2)
                                        action = ActionChains(self.driver)
                                        element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action.move_to_element(element)
                                        action.perform()
                                        time.sleep(0.5)
                                    
                                        element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        action = ActionChains(self.driver)
                                        action.move_to_element(element)
                                        action.perform()
                                        WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                        element.click()

                                    WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                                    yield self.get_info(Selector(text=self.driver.page_source))
                                    pp += 1
                                ss += 1

                        else: # just style
                            ss = 0
                            for s in range(style_len):
                                WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))

                                try:
                                    action = ActionChains(self.driver)
                                    element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    action.move_to_element(element)
                                    action.perform()
                                    WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                    element.click()
                                except:
                                    time.sleep(0.2)
                                    action = ActionChains(self.driver)
                                    element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    action.move_to_element(element)
                                    action.perform()
                                    time.sleep(0.5)
                                    
                                    element = self.driver.find_elements(By.XPATH, style_choice)[ss]
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    action = ActionChains(self.driver)
                                    action.move_to_element(element)
                                    action.perform()
                                    WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, style_choice)))
                                    element.click()

                                WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, style_choice)))
                                yield self.get_info(Selector(text=self.driver.page_source))
                                ss += 1

                    elif pattern_len: # just pattern
                        pp = 0
                        for p in range(pattern_len):
                            WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                            
                            try:
                                action = ActionChains(self.driver)
                                element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                action.move_to_element(element)
                                action.perform()
                                WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                element.click()
                            except:
                                time.sleep(0.2)
                                action = ActionChains(self.driver)
                                element = self.driver.find_element(By.XPATH, '//div[@id="nav-logo"]/a')
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                action.move_to_element(element)
                                action.perform()
                                time.sleep(0.5)
                                    
                                element = self.driver.find_elements(By.XPATH, pattern_choice)[pp]
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                action = ActionChains(self.driver)
                                action.move_to_element(element)
                                action.perform()
                                WebDriverWait(self.driver, 0.7).until(EC.element_to_be_clickable((By.XPATH, pattern_choice)))
                                element.click()

                            WebDriverWait(self.driver, 6).until(EC.presence_of_all_elements_located((By.XPATH, pattern_choice)))
                            yield self.get_info(Selector(text=self.driver.page_source))
                            pp += 1
                    
                    else:
                        print("\n\n\n the else that we don't know why it's here\n\n\n")
                        self.driver.save_screenshot('png.png')
                        yield self.get_info(Selector(text=self.driver.page_source))
                    
                else:
                    yield self.get_info(Selector(text=self.driver.page_source))
            except:
                print(traceback.format_exc())
                self.driver.save_screenshot('png.png')
                print('\n\n\nerror\n\n\n')
                with open('un_url_list.txt', 'a') as file:
                        file.write(f'{url}\n')
                time.sleep(20)
            x += 1
            print(f'\n\n\n\n{x}th url in the list\n\n\n\n')

    # ----------------------


    # ----------- MAIN PARSE ALL
    def get_info(self, response):
        # PRICE
        price_xpath1 = '//td[@class="a-color-secondary a-size-base a-text-right a-nowrap" and contains(text(), "Price")]/following-sibling::td//span[@class="a-offscreen"]'
        price_xpath2_symbol = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-symbol"]'
        price_xpath2_whole = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-whole"]'
        price_xpath2_fraction = '//div[@id="corePriceDisplay_desktop_feature_div"]//span[@class="a-price-fraction"]'
        price_xpath3 = '//td[@class="a-color-secondary a-size-base a-text-right a-nowrap" and contains(text(), "Now")]/following-sibling::td//span[@class="a-offscreen"]'
        price_xpath_from = '//span[contains(text(), "from")]/following-sibling::span'

        response = response
        # PRICE
        price = response.xpath(price_xpath1 + '/text()').get()
        if not price:
            price = response.xpath(price_xpath3 + '/text()').get()
        if not price:
            if response.xpath(price_xpath2_symbol + '/text()').get():
                price = response.xpath(price_xpath2_symbol + '/text()').get() + response.xpath(price_xpath2_whole + '/text()').get() + '.' + response.xpath(price_xpath2_fraction + '/text()').get()
            else:
                price = response.xpath(price_xpath_from + '/text()').get()
        if not price:
            price = response.xpath('//div[@id="availability"]/span/text()').get()

        #TITLE
        title = response.xpath('//h1[@id="title"]/span/text()').get().strip()

        # TABLE
        brand = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Brand"]/parent::td/following-sibling::td/span/text()').get()
        model_name = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Model name"]/parent::td/following-sibling::td/span/text()').get()
        item_weight = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Item weight"]/parent::td/following-sibling::td/span/text()').get()
        color = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Colour"]/parent::td/following-sibling::td/span/text()').get()
        material = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Material"]/parent::td/following-sibling::td/span/text()').get()
        form_factor = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Form factor"]/parent::td/following-sibling::td/span/text()').get()

        ear_placement = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Ear placement"]/parent::td/following-sibling::td/span/text()').get()
        headphone_jack = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Headphone jack"]/parent::td/following-sibling::td/span/text()').get()
        cable_feature = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Cable feature"]/parent::td/following-sibling::td/span/text()').get()

        control_type = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Control type"]/parent::td/following-sibling::td/span/text()').get()
        connectivity_tech = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Connectivity technology"]/parent::td/following-sibling::td/span/text()').get()
        noise_control = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Noise control"]/parent::td/following-sibling::td/span/text()').get()
        wireless_communication_tech = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Wireless communication technology"]/parent::td/following-sibling::td/span/text()').get()

        style = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Style"]/parent::td/following-sibling::td/span/text()').get()
        special_feature = response.xpath('//table[@class="a-normal a-spacing-micro"]//tr/td[1]/span[text()="Special feature"]/parent::td/following-sibling::td/span/text()').get()

        ddict = {
            'title': title,
            'brand': brand,
            'model_name': model_name,
            'colour': color,
            'price': price,
            'item weight': item_weight,
            'material': material,
            'form factor': form_factor,
            'ear placement': ear_placement, 
            'headphone jack': headphone_jack,
            'cable future': cable_feature,
            'control type': control_type,
            'connectivity': connectivity_tech,
            'noise control': noise_control,
            'wireless communication': wireless_communication_tech,
            'style': style,
            'special feature': special_feature,
        }
        print(f'\n\n\n{ddict}\n\n\n')
        return ddict
# ------------
