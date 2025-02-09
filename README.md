

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

결과는 `/database`에 저장됩니다.

# 전처리 및 파생변수 생성

전처리는 크게 다음과 같은 과정을 거쳤습니다
1. 리뷰/별점/작성일자 중 하나라도 공란이면 삭제
2. 별점 이상치(1미만 혹은 5 초과)면 삭제
3. 작성일자 date를 datetime으로 변환
4. 텍스트 전처리
   - 특정 품사만 추출
   - 불용어 제거
   - 특수문자 제거

파생변수로는 rating_length_category를 생성했습니다.
신라면에 대한 평점이 대부분 만점이었기에 별점만으로는 별다른 패턴을 보일 수 없다고 판단해, 별점-텍스트길이를 나타내는 변수를 만들었습니다.
텍스트길이는 벡터화를 거친 단어 수 기준으로 1개면 short, 2개부터 4개는 middle, 5개 이상은 long으로 분류했습니다.

예) 
별점 4점 단어수 2개 : 4-middle
별점 5점 단어수 1개 : 5-short
별점 5점 단어수 6개 : 5-long

# EDA/FE/시각화 결과 & 비교분석

## 쿠팡

![coupang_output](https://github.com/user-attachments/assets/43c07cf2-f653-4574-9c0a-2c211cb1a58d)

전처리 이후 작성일자에 따른 리뷰 갯수를 나타낸다
- 최신 리뷰에 비중을 두었긴 하나, 23년 이전 데이터도 조금씩 수집되었다. 그래프 상으로는 23년도를 기준으로 데이터가 거의 절단된 것을 볼 수 있다.
- 특이하게도 2025년에 리뷰 갯수가 폭증한 것을 볼 수 있다.


![coupang_lda](https://github.com/user-attachments/assets/f1ded55c-1117-4ff0-b40f-1b2e55da0963)

LDA 토픽모델링 결과
- 후술할 두 사이트에 비해 전반적으로 키워드들이 고른 분포를 지닌다.



## 홈플러스

![homeplus_output](https://github.com/user-attachments/assets/31d1bc1a-7c60-4489-b241-de16bdb39215)

전처리 이후 작성일자에 따른 리뷰 갯수를 나타낸다
- 홈플러스는 최신 리뷰 기준으로 1,500개를 크롤링했기에, 작성일자가 25.01.01부터 25.01.21까지 최근 3주의 데이터만 수집된 것을 볼 수 있다
- 2-3일과 19-20일 즈음에 리뷰가 제일 많이 작성되었고, 미세하게 쌍봉형 분포의 경향을 띈다.


![homeplus_lda](https://github.com/user-attachments/assets/38902ce8-40b1-43cc-bdab-099af89b75ed)

LDA 토픽모델링 결과
- '저렴하다' '행사'와 같은 금액적인 부분과 관련한 단어들이 높은 순위를 차지하고 있다.


## SSG

![ssg_output](https://github.com/user-attachments/assets/706fd2f3-cbb4-4611-958a-29ee4c99b08d)

전처리 이후 작성일자에 따른 리뷰 갯수를 나타낸다
- 쿠팡과 마찬가지로 23,000개를 수집했으나 24년도 하반기-25년의 리뷰가 대다수를 차지하고 있으며, 24년도 상반기부터 데이터가 거의 절단된 걸 볼 수 있다


![ssg_lda](https://github.com/user-attachments/assets/01bff19f-69ec-4e6c-8f94-c0974409e026)

LDA 토픽 모델링 결과
- '맛있다' '먹다' '좋아하다' '최고' 등 맛과 관련해 긍정적인 뉘앙스를 지닌 단어가 높은 순위를 자치하고 있는 것을 볼 수 있다.



## 비교분석
빈도 히스토그램
- 세 사이트 모두 최신 리뷰에 중점을 두어 수집했으나, 쿠팡과 ssg는 x축의 범위가 해 기준이고, 홈플러스는 최근 3주 이내의 데이터로 이루어져있다. 따라서 현재의 그래프만으로는 사이트 간 유의미한 차이를 판단하기 어렵다.

LDA 토픽모델링
- 세 사이트 모두 공통적으로 긍정적인 늬앙스를 지닌 키워드들로 이루어졌다
- 다만, 높은 순위를 차지한 키워드를 보면 ssg는 맛과 관련된 단어들이 주를 이뤘고, 홈플러스는 금액적인 부분과 관련된 키워드가 눈에 띈다. 쿠팡은 전반적으로 키워드들이 모두 고르게 분포해 있다.
- 물론 과대해석일 가능성이 존재하며 데이터 수 또한 부족하다는 것을 알지만, 상위 키워드에 기반해 플랫폼별 차이를 구분짓자면:
- 홈플러스가 대형 마트인 특성을 고려하면, 홈플러스 사용자들은 소비에 있어 금액적인 부분에 좀 더 비중을 둔다고 볼 수 있고
- SSG의 사용자들은 맛(질), 그리고 쿠팡 사용자들은 별다른 특성이 없다고 추론할 수 있다.

추후 관련 프로젝트를 진행한다면, 플랫폼 자체의 특성(대형 마켓, 압도적 점유율을 가진 전자상거래 기업 등)을 고려하면 유의미한 인사이트를 제공할 수 있을 것이라 생각한다.


-------

# YBIGTA 26기 교육세션 3조

## Introduction

안녕하세요! YBIGTA 26기 교육세션 3조입니다.

### 팀원 소개
- 이준찬: gamma4638, 산업공학과 19학번
- 조요셉: kulusevski, 응용통계학과 21학번
- 이재우: oizhq-mdr, 언론홍보영상학부 20학번

## Attachments

### Branch Protection 관련
![branch protection](github/branch_protection.png)
![push rejected](github/push_rejected.png)

### Merge 완료
![조요셉 merge 완료](<github/merged_kulusevski.png>)
![이재우 merge 완료](<github/merged_oizhq-mdr.png>)
![이준찬 merge 완료](<github/merged_gamma4638.png>)

## Project Architecture

### MVC 패턴
MVC(Model-View-Controller) 패턴은 애플리케이션을 세 가지 주요 컴포넌트로 분리합니다:

- **Model**: DB와 상호작용하여 데이터를 관리
- **View**: 사용자에게 보여지는 인터페이스
- **Controller**: Model과 View 사이의 중개자 역할

### 프로젝트 구조
#### Model
- `user/user_repository.py`
- `user/user_schema.py`

#### View
- `static/index.html`

#### Controller
- `user/user_router.py`: 요청에 따른 서비스 호출 담당
- `user/user_service.py`: 비즈니스 로직 처리 (로그인, 회원가입, 비밀번호 업데이트, 회원 삭제)

### 실행 흐름
1. 사용자가 `http://127.0.0.1:8000/static/index.html`에서 요청
2. 요청이 Controller(`user_router`)로 전달
3. `user_router`가 적절한 엔드포인트를 `user_service`로 전달
4. `user_service`가 `user_repository`를 통해 DB 작업 수행
5. `user_service`의 처리 결과를 바탕으로 `user_router`가 응답 생성
6. 생성된 응답을 View(HTML)로 전달!!!!


## DB Docker AWS 과제

- Docker Repository URL: https://hub.docker.com/repository/docker/oizhq/ybigta_newbie_team_project/general

![delete_api.png](<aws/delete_api.png>)
![login_api.png](<aws/login_api.png>)
![register_api.png](<aws/register_api.png>)
![update_password_api.png](<aws/update_password_api.png>)
![github_action.png](<aws/github_action.png>) 





















