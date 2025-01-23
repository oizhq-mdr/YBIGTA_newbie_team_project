from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore

class ExampleProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):

        """
        ExampleProcessor 클래스의 생성자입니다.

        Args:
            input_path (str): 입력 CSV 파일의 경로
            output_path (str): 출력 파일을 저장할 디렉토리 경로
        """
        super().__init__(input_path, output_path)

        self.df = pd.read_csv(self.input_path)

    def preprocess(self):
        # 'date' 열을 datetime 형식으로 변환
        self.df['date'] = pd.to_datetime(self.df['date'])

        # 'review' 열의 결측치 제거
        self.df['review'].fillna("리뷰 없음", inplace=True)

        # 'review_length' 열 추가
        self.df['review_length'] = self.df['review'].apply(lambda x: len(str(x)))
        threshold = self.df['review_length'].quantile(0.95)

        # 상위 5% 이상치 제거
        self.df = self.df[self.df['review_length'] <= threshold]

        self.df['review'] = self.df['review'].apply(lambda x: len(x.split()))
        
        # 'review' 열의 텍스트 전처리
        self.df['review'] = self.df['review'].astype(str)  # NaN 또는 None 값 처리

        # 한글과 공백을 제외한 모든 문자 제거
        self.df['review'] = self.df['review'].apply(lambda x: re.sub(r"[^가-힣\s]", "", x))

        # 불필요한 공백 제거
        self.df['review'] = self.df['review'].apply(lambda x: re.sub(r"\s+", " ", x).strip())


    
    def feature_engineering(self):
        """
        특징 엔지니어링
        - 텍스트 단어 수 계산
        - 텍스트 길이 분류(short/middle/long)
        - (별점)-(텍스트길이) 파생변수
        - TF-IDF 벡터화
        """

        self.data['word_count'] = self.data['content'].apply(lambda x: len(x.split()))
        self.data['text_length_category'] = self.data['word_count'].apply(
            lambda count: 'short' if count <= 1 else (
                'middle' if 2 <= count <= 4 else 'long'
            )
        )

        self.data['rating_length_category'] = self.data.apply(
            lambda row: f"{int(row['score'])}-{row['text_length_category']}", axis=1
        )

        vectorizer: Any = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.data['content'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), 
                                columns=vectorizer.get_feature_names_out())

        self.data = pd.concat([self.data.reset_index(drop=True), 
                               tfidf_df.reset_index(drop=True)], axis=1)

        self.data = self.data[self.data['word_count'] > 0]

        print("Feature engineering completed.")



    def save_to_database(self):
        output_file = f"{self.output_dir}/preprocessed_reviews_coupang.csv"
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')

