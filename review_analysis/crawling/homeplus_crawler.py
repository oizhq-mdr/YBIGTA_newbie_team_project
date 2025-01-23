from review_analysis.crawling.base_crawler import BaseCrawler
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import os
import csv
import sys


class HomeplusCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        '''
        Args:
            output_dir: 크롤링 결과를 저장할 디렉토리 경로
            
        '''
        super().__init__(os.path.join(os.getcwd(), 'database'))
        self.base_url = 'https://mfront.homeplus.co.kr/item?itemNo=120074651&storeType=HYPER&storeId&optNo'
        self.driver: WebDriver = None
        self.reviews_data = []

    def start_browser(self):
        """
        크롬 드라이버를 실행하고 목표 페이지에 접속한 뒤, 리뷰가 있는 '상품리뷰' 클릭하기
        
        클릭 후 페이지 로딩은 2초간 대기
        """
        
        from selenium.webdriver.chrome.service import Service
        service = Service("/Users/joseph/Desktop/chromedriver-mac-arm64/chromedriver")
        
        self.driver = webdriver.Chrome(service=service)
        self.driver.get(self.base_url)
        time.sleep(3)

        review_tab_btn = self.driver.find_element(By.XPATH, '//*[@id="prodDetailTab"]/div[1]/div/ul/li[2]/button')
        review_tab_btn.click()
        time.sleep(2)
        
    def scrape_reviews(self):
        '''
        리뷰(텍스트, 별점, 작성일자)를 최대 1500개까지 수집하기
        
        1. 현재 페이지에서 인덱스 1부터 60까지의 리뷰 탐색 및 스크래이핑
        2. 더이상의 리뷰가 없으면 스톱
        3. "더보기"를 계속 누르면서 크롤링할 리뷰 추가 탐색
        4. 더이상의 '더보기'가 없거나 크롤링한 리뷰 수가 1500개가 넘어가면 스톱
        5. 수집한 리뷰는 self.reviews_data 리스트에 저장
        
        '''
        if self.driver is None:
            self.start_browser()
            
        total_scraped = 0
        start_index = 1

        while total_scraped < 1500:
            new_reviews_in_page = 0
            
            end_index = start_index + 29
            for i in range(start_index, end_index +1):
                content = ""
                found_content = False
                review_xpath_candidates = [
                    f'//*[@id="prodDetailTab"]/div[2]/div[1]/div/div[5]/div[4]/div[{i}]/div[3]/div/pre',
                    f'//*[@id="prodDetailTab"]/div[2]/div[1]/div/div[5]/div[4]/div[{i}]/div[3]/div[2]/pre',
                ]
                for rx in review_xpath_candidates:
                    try:
                        content_elem = self.driver.find_element(By.XPATH, rx)
                        if content_elem:
                            content = content_elem.text.strip()
                            found_content = True
                            break
                    except:
                        pass

                score = ""
                star_xpath = f'//*[@id="prodDetailTab"]/div[2]/div[1]/div/div[5]/div[4]/div[{i}]/div[1]/strong'
                try:
                    score_elem = self.driver.find_element(By.XPATH, star_xpath)
                    if score_elem:
                        score = score_elem.text.strip()
                except:
                    pass

                review_date = ""
                date_xpath = f'//*[@id="prodDetailTab"]/div[2]/div[1]/div/div[5]/div[4]/div[{i}]/div[2]/span'
                try:
                    date_elem = self.driver.find_element(By.XPATH, date_xpath)
                    if date_elem:
                        review_date = date_elem.text.strip()
                except:
                    pass

                if not found_content and not score and not review_date:
                    break

                self.reviews_data.append({
                    'content': content,
                    'score': score,
                    'date': review_date
                })
                total_scraped += 1
                new_reviews_in_page += 1

                if total_scraped >= 1500:
                    break

            if new_reviews_in_page == 0:
                break
            if total_scraped >= 1500:
                break


            more_button_index = 31
            while True:
                if more_button_index > 1501:
                    print("더보기 버튼 인덱스가 1501을 초과했습니다. 더 이상 시도하지 않습니다.")
                    break

                more_button_xpath = f'//*[@id="prodDetailTab"]/div[2]/div[1]/div/div[5]/div[4]/div[{more_button_index}]/button'
                try:
                    more_button = self.driver.find_element(By.XPATH, more_button_xpath)
                    more_button.click()
                    time.sleep(2)  # 다음 페이지 로딩 대기
                    more_button_index += 30
                except:
                    break
                    # print("더보기 버튼이 없거나 더 이상 로드할 리뷰가 없습니다.")
                
            start_index = end_index +1
                    

    def save_to_database(self):
        """
        수집한 리뷰 데이터를 CSV 파일로 저장하기

        - output_dir가 존재하지 않으면 생성
        - homeplus_reviews.csv 파일로 결과를 저장
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        output_file = os.path.join(self.output_dir, 'reviews_homeplus.csv')
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['content', 'score', 'date'])
            writer.writeheader()
            for review in self.reviews_data:
                writer.writerow(review)

        print(f"수집한 리뷰 {len(self.reviews_data)}개를 {output_file} 파일로 저장했습니다.")

