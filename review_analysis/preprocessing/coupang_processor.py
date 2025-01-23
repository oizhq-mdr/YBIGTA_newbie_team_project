from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore

from kiwipiepy import Kiwi # type: ignore
import re
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore
kiwi: Any = Kiwi()
class CoupangProcessor(BaseDataProcessor):
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
        """
        데이터 전처리 method
        
        1. 결측치 처리:
           content, score, date 중 하나라도 공백이면 해당 행 제거
        2. 별점 이상치 처리:
            - 1-5 사이가 아니면 제거
        3. 작성일자열 datetime 변환
        4. 텍스트 전처리:
            - 명사만 추출
            - 특수문자 제거
        """
        self.df.dropna(subset=['review', 'rating', 'date'], inplace=True)

        self.df = self.df[(self.df['score'] >= 1) & (self.df['rating'] <= 5)]
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df = self.df[self.df['date'].notnull()]

        self.df['content'] = self.df['content'].astype(str).apply(
            lambda content: ' '.join([
                token.form
                for token in kiwi.tokenize(
                    re.sub(r'[^\s\w\d]', " ", content)
                )
                if 'NN' in token.tag  
            ])
        )

        print("Preprocessing completed.")
        


    
    def feature_engineering(self):
        """
        특징 엔지니어링
        - 텍스트 단어 수 계산
        - 텍스트 길이 분류(short/middle/long)
        - (별점)-(텍스트길이) 파생변수
        - TF-IDF 벡터화
        """

        self.df['word_count'] = self.df['review'].apply(lambda x: len(x.split()))
        self.df['text_length_category'] = self.df['word_count'].apply(
            lambda count: 'short' if count <= 1 else (
                'middle' if 2 <= count <= 4 else 'long'
            )
        )

        self.df['rating_length_category'] = self.df.apply(
            lambda row: f"{int(row['rating'])}-{row['text_length_category']}", axis=1
        )

        vectorizer: Any = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.df['review'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), 
                                columns=vectorizer.get_feature_names_out())

        self.df = pd.concat([self.df.reset_index(drop=True), 
                               tfidf_df.reset_index(drop=True)], axis=1)

        self.df = self.df[self.df['word_count'] > 0]

        print("Feature engineering completed.")



    def save_to_database(self):
        output_file = f"{self.output_dir}/preprocessed_reviews_coupang.csv"
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')

