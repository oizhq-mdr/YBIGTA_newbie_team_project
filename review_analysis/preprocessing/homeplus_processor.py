from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import numpy as np
import re
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer

# Kiwi 초기화
kiwi = Kiwi()

class HomeplusProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        """
        Args:
            input_path: 원본 데이터 경로
            output_dir: 전처리 및 FE 결과 저장 경로
        """
        super().__init__(input_path, output_dir)
        self.data = pd.read_csv(self.input_path)
        
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
        self.data.dropna(subset=['content', 'score', 'date'], inplace=True)

        self.data = self.data[(self.data['score'] >= 1) & (self.data['score'] <= 5)]
        self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')
        self.data = self.data[self.data['date'].notnull()]

        self.data['content'] = self.data['content'].astype(str).apply(
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

        self.data['word_count'] = self.data['content'].apply(lambda x: len(x.split()))
        self.data['text_length_category'] = self.data['word_count'].apply(
            lambda count: 'short' if count <= 1 else (
                'middle' if 2 <= count <= 4 else 'long'
            )
        )

        self.data['rating_length_category'] = self.data.apply(
            lambda row: f"{int(row['score'])}-{row['text_length_category']}", axis=1
        )

        vectorizer = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.data['content'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), 
                                columns=vectorizer.get_feature_names_out())

        self.data = pd.concat([self.data.reset_index(drop=True), 
                               tfidf_df.reset_index(drop=True)], axis=1)

        self.data = self.data[self.data['word_count'] > 0]

        print("Feature engineering completed.")

    def save_to_database(self):
        """
        전처리 및 FE 결과 저장
            - (주석 제거시)최종 CSV에는 date, score, content, rating_length_category만 남김
        """
        # final_cols = ['date', 'score', 'content', 'rating_length_category']
        # self.data = self.data[final_cols]

        output_file = f"{self.output_dir}/preprocessed_reviews_homeplus.csv"
        self.data.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Processed data saved to {output_file}.")

