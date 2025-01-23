from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

import pandas as pd
import time
import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.chrome.options import Options

class CoupangCrawler(BaseCrawler):
    def __init__(self, output_dir: str):

        """
        CoupangCrawler 생성자.

        Args:
            output_dir (str): 크롤링 결과를 저장할 디렉토리 경로
        """

        super().__init__(output_dir)
        self.base_url = (
            "https://www.coupang.com/vp/products/7958974?itemId=19421766393"
            "&vendorItemId=3058658009&q=%EC%8B%A0%EB%9D%BC%EB%A9%B4"
            "&itemsCount=36&searchId=13424d858927815&rank=0&searchRank=0&isAddedCart="
        )
        self.driver_path = r"C:\Users\user\.cache\selenium\chromedriver\win64\131.0.6778.264\chromedriver.exe"

        # WebDriver 및 크롤링된 결과를 저장할 멤버 변수
        self.driver = None
        self.all_reviews : list[dict] = []
        
    def start_browser(self):
        """
        Selenium WebDriver(Chrome) 객체를 생성하고 준비하는 메서드.

        """
        options = webdriver.ChromeOptions()
        # 필요 시 headless 옵션 활성화 가능 
        # options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        # Chrome 97 이상 버전부터는 executable_path 대신 driver_path를 options로 설정 가능
        # 하지만 여기서는 기존 로직과 동일하게 유지
        self.driver = webdriver.Chrome(
            executable_path=self.driver_path,
            options=options
        )
    
    def scrape_reviews(self):
        """
          
        1) 드라이버가 준비된 상태에서 self.base_url로 이동
        2) 각 페이지 버튼(2~11)을 차례대로 클릭하며 리뷰(5개 단위)를 수집
        3) 1,000개 이상 수집 후 종료하거나, 더 이상 페이지가 없으면 반복 종료
        4) 페이지 세트(1~10, 11~20, ...) 사이 이동을 위해 '다음' 버튼 클릭
        5) 최종적으로 pandas DataFrame 형태로 반환


        """
        self.start_browser()
        if self.driver is None:
            raise RuntimeError("start_browser()를 먼저 호출")

        # URL 이동
        self.driver.get(self.base_url)
        time.sleep(3)  # 페이지 로딩 대기

        self.all_reviews = []

        # 리뷰 추출을 위해 반복
        while len(self.all_reviews) < 1000:
            # 페이지 버튼 [2] ~ [11] 순회
            for page_btn_idx in range(2, 12):
                try:
                    page_btn_xpath = (
                        "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/"
                        f"div/div[6]/section[4]/div[3]/button[{page_btn_idx}]"
                    )
                    page_button = self.driver.find_element(By.XPATH, page_btn_xpath)
                    page_button.click()
                    time.sleep(2)  # 페이지 전환 대기

                    # ========== [기존 _get_reviews_from_current_page() 로직 인라인] ==========
                    review_section_xpaths = [
                        "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/div/"
                        "div[6]/section[4]/article[1]",
                        "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/div/"
                        "div[6]/section[4]/article[2]",
                        "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/div/"
                        "div[6]/section[4]/article[3]",
                        "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/div/"
                        "div[6]/section[4]/article[4]",
                        "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/div/"
                        "div[6]/section[4]/article[5]",
                    ]

                    page_reviews = []
                    for article_xpath in review_section_xpaths:
                        try:
                            article_element = self.driver.find_element(By.XPATH, article_xpath)

                            # 리뷰 텍스트
                            text_div = article_element.find_element(By.XPATH, "./div[4]/div")
                            raw_text = text_div.text.strip()
                            review_text = raw_text.replace("\n", " ")

                            # 별점
                            try:
                                rating_div = article_element.find_element(
                                    By.XPATH, "./div[1]/div[3]/div[1]/div"
                                )
                                rating = rating_div.get_attribute('data-rating')
                            except:
                                rating = None

                            # 날짜
                            try:
                                date_div = article_element.find_element(
                                    By.XPATH, "./div[1]/div[3]/div[2]"
                                )
                                date_text = date_div.text.strip()
                            except:
                                date_text = None

                            page_reviews.append({
                                'review': review_text,
                                'rating': rating,
                                'date': date_text
                            })
                        except Exception as e:
                            print(f"[오류 발생] 리뷰 정보 추출 실패: {e}")
                            page_reviews.append({
                                'review': "",
                                'rating': None,
                                'date': None
                            })

                    # ========== [인라인 로직 끝] ==========
                    self.all_reviews.extend(page_reviews)

                    # 1,000개 이상이면 종료
                    if len(self.all_reviews) >= 1000:
                        break

                except Exception as e:
                    print(f"[오류 발생] 페이지 버튼({page_btn_idx}) 클릭 실패: {e}")
                    # 더 이상 페이지가 없다고 가정, 반복 종료 가능
                    break

            # 1,000개 이상이면 최종 종료
            if len(self.all_reviews) >= 1000:
                break

            # 다음 10페이지 세트로 이동
            try:
                next_btn_xpath = (
                    "/html/body/div[2]/section/div[2]/div[2]/div[7]/ul[2]/li[2]/"
                    "div/div[6]/section[4]/div[3]/button[12]"
                )
                next_button = self.driver.find_element(By.XPATH, next_btn_xpath)
                next_button.click()
                time.sleep(2)
            except Exception as e:
                print("[오류 발생] 다음 세트 버튼 클릭 실패 또는 더 이상 페이지가 없습니다:", e)
                break

    
    def save_to_database(self):
        df_reviews = pd.DataFrame(self.all_reviews, columns=['review', 'rating', 'date'])
        df_reviews.to_csv('coupang_review.csv', index=False, encoding='utf-8-sig')
