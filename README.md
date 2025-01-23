

# 주제

국민 라면인 신라면의 쿠팡, 홈플러스, SSG 구매자 리뷰를 크롤링하고 분석했습니다. 원활한 데이터 분석을 위해 데이터의 형식은 별점, 리뷰 내용, 날짜로 통일하였습니다.

- 쿠팡: [https://www.coupang.com/vp/products/7038366959?itemId=17397483274&vendorItemId=84566941756&pickType=COU_PICK&q=%EC%8B%A0%EB%9D%BC%EB%A9%B4&itemsCount=36&searchId=1b0fd29413788560&rank=16&searchRank=16&isAddedCart=](쿠팡)

    - 리뷰 수: 1,615개 / 38,788개
    
- 홈플러스: [https://mfront.homeplus.co.kr/item?itemNo=120074651&storeType=HYPER&storeId&optNo](홈플러스)

    - 리뷰 수: 1,500개 / 97,947개

- SSG: [https://www.ssg.com/item/itemView.ssg?itemId=0000008333648&siteNo=6001&salestrNo=2037](SSG)

    - 리뷰 수: 23,440개 / 485,266개


# 실행 방법

## 텍스트 크롤링

루트 디렉토리에서 다음의 명령어를 실행하면 각 웹사이트에 대한 크롤러가 순차적으로 모두 실행됩니다. `/database` 경로에 크롤링 결과가 저장됩니다. 

```
python -m review_analysis.crawling.main -o database -a
```

개별 크롤러를 실행하려면 다음의 명령어를 실행해야 합니다. 

```
python -m review_analysis.crawling.main -o database -c {크롤러 이름 eg. Ssg, Homeplus, Coupang}
```

## 전처리 및 FE

전처리 및 FE가 완료된 파일을 확인하기 위해서는 루트 디렉토리에서 아래의 명령어를 실행해야 합니다. 

```
python -m review_analysis.preprocessing.main -o database -a
```


결과는 `/database` 경로에 저장됩니다. 

# EDA/FE/시각화 결과

## 쿠팡

![coupang_output](https://github.com/user-attachments/assets/43c07cf2-f653-4574-9c0a-2c211cb1a58d)

- (전처리 이후) 별점 분포
- (전처리 이후) 길이 분포
- (전처리 이후) 날짜 분포
  
LDA 토픽모델링 결과
![coupang_lda](https://github.com/user-attachments/assets/f1ded55c-1117-4ff0-b40f-1b2e55da0963)


## 홈플러스

![homeplus_output](https://github.com/user-attachments/assets/31d1bc1a-7c60-4489-b241-de16bdb39215)

- (전처리 이후) 별점 분포
- (전처리 이후) 길이 분포
- (전처리 이후) 날짜 분포

- LDA 토픽모델링 결과
![homeplus_lda](https://github.com/user-attachments/assets/38902ce8-40b1-43cc-bdab-099af89b75ed)


## SSG

![ssg_output](https://github.com/user-attachments/assets/706fd2f3-cbb4-4611-958a-29ee4c99b08d)

- (전처리 이후) 별점 분포
- (전처리 이후) 길이 분포
- (전처리 이후) 날짜 분포

- LDA 토픽 모델링 결과
- ![ssg_lda](https://github.com/user-attachments/assets/01bff19f-69ec-4e6c-8f94-c0974409e026)

