from review_analysis.crawling.base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from datetime import datetime
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import random
import time
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import requests

class SsgCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.ssg.com/item/itemView.ssg?itemId=0000008333648&siteNo=6001&salestrNo=2037'
        self.reviews: list[tuple[int, str, str]] = []  # reviews 리스트 초기화
        
    def start_browser(self):
        # chromedriver 경로 설정
        CHROMEDRIVER_PATH = '/Users/jaewoolee/chromedriver-mac-arm64'
        os.environ["PATH"] += os.pathsep + CHROMEDRIVER_PATH

        # 브라우저 옵션 설정
        chrome_options = Options()

        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        # User-Agent 설정
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        driver = webdriver.Chrome(options=chrome_options)

        # 브라우저 열기
        try:
            driver.get(self.base_url)
            return driver
        except Exception as e:
            print(f"Error starting browser: {e}")
            return None

    def scrape_reviews(self):
        driver = self.start_browser()
        if not driver:
            return []

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            while True:
                try:
                    # 페이지 로딩을 위한 명시적 대기 추가
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'rvw_expansion_panel_list'))
                    )
                    
                    # 현재 스크롤 위치 저장
                    last_height = driver.execute_script("return document.body.scrollHeight")
                    
                    review_section_button = driver.find_element(By.XPATH, '/html/body/div[5]/div[4]/div/div[2]/div[5]/div[1]/div/div[1]/ul/li[3]/a')
                    review_section_button.click()
                    time.sleep(1)  # 스크롤 후 대기 시간 감소
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    data_rows = soup.find_all('li', class_='rvw_expansion_panel v2')
                    current_page: int = int(soup.find('div', class_ = 'rvw_paging').find('strong').text)

                    for data in data_rows:
                        rating: int = int(data.find('em').text) * 2
                        comment: str = data.find('p', class_ = 'rvw_item_text').text
                        date: str = data.find('div', class_ = 'rvw_item_label rvw_item_date').text
                        date = date.replace('.', '-')
                        self.reviews.append((rating, comment, date))
                        print(f"rating: {rating}, comment: {comment}, date: {date}")
                        

                    # current_page: int = int(soup.find('div', class_ = 'rvw_paging').find('strong').text)
                    next_page: int = current_page + 1
                    # 다음 페이지 버튼 찾기
                    try:
                        if current_page == 10:
                            next_button = driver.find_element(By.XPATH, '/html/body/div[5]/div[4]/div/div[2]/div[5]/div[1]/div/div[2]/div[3]/div[2]/section[2]/div/div[4]/a[2]')
                        elif current_page % 10 == 0:
                            next_button = driver.find_element(By.XPATH, '/html/body/div[5]/div[4]/div/div[2]/div[5]/div[1]/div/div[2]/div[3]/div[2]/section[2]/div/div[4]/a[3]')
                        else:
                            next_button = driver.find_element(By.XPATH,f'/html/body/div[5]/div[4]/div/div[2]/div[5]/div[1]/div/div[2]/div[3]/div[2]/section[2]/div/div[4]/div/a[{current_page % 10}]')
                        next_button.click()
                        time.sleep(random.uniform(1, 2))
                        self.save_to_database()

                        
                            
                    except Exception as e:
                        print(f"Error with next button: {e}")
                        

                    # 매 3페이지마다 중간 저장 (더 자주 저장하도록 수정)
                    if current_page % 3 == 0:
                        self.save_to_database()
                        print(f"Progress saved at page {current_page}")
                
                    print(f"Page {current_page} completed. Total reviews: {len(self.reviews)}")
                    current_page += 1
                    
                except Exception as e:
                    print(f"Error during scraping: {e}")                    
                    self.save_to_database()  # 에러 발생 시에도 저장
                    time.sleep(random.uniform(5, 8))  # 에러 발생 시 대기 시간 감소
                    continue  # 다음 시도 계속
        
        finally:
            print("Saving final results...")
            self.save_to_database()
            driver.quit()
        
        return None

    def save_to_database(self):
        df = pd.DataFrame(self.reviews, columns=['rating', 'comment', 'date'])
        df.to_csv(os.path.join(self.output_dir, 'reviews_ssg.csv'), index=True)
