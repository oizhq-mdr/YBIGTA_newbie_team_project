from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import os
import emoji
import re
import kiwipiepy  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer  # type: ignore
# from konlpy.tag import Okt

class SsgProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.processed_df = None

    def preprocess(self):
        # 데이터 로드
        self.df = pd.read_csv(self.input_path, index_col=0)

        print(len(self.df))

        # 날짜 str에서 datetime으로 변환
        self.df['date'] = pd.to_datetime(self.df['date'])

        # comment 내 whitespace 제거
        self.df['comment'] = self.df['comment'].str.replace('\n', ' ') 
        self.df['comment'] = self.df['comment'].str.strip()
        
        # 결측치 처리
        self.df['rating'].fillna('점수 없음', inplace=True)
        self.df['comment'].fillna('리뷰 없음', inplace=True)
        self.df['date'].fillna('날짜 없음', inplace=True)

        # 특수문자 및 이모지 제거
        self.df['comment'] = self.df['comment'].apply(lambda x: emoji.replace_emoji(x, ''))  # 이모지 제거
        self.df['comment'] = self.df['comment'].apply(lambda x: re.sub(r'[^가-힣a-zA-Z0-9\s]', '', x))  # 특수문자 제거
        self.df['comment'] = self.df['comment'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())  # 중복 공백 제거

        # # 텍스트 정규화 및 토큰화
        # okt = Okt()
        # self.df['comment'] = self.df['comment'].apply(lambda x: okt.normalize(x))  # 정규화
        # self.df['comment'] = self.df['comment'].apply(lambda x: ' '.join([word for word, pos in okt.pos(x)                                                                        if pos in ['Noun', 'Adjective', 'Verb']]))  # 형태소 분석 및 필터링
        
        
        # 토큰화
        kiwi = kiwipiepy.Kiwi()
        self.df['comment'] = self.df['comment'].astype(str).apply(
            lambda content: ' '.join([
                token.form
                for token in kiwi.tokenize(
                    re.sub(r'[^\s\w\d]', " ", content)
                )
                if 'NN' in token.tag  
            ])
        )
        

        # 불용어 리스트 정의 및 불용어 제거
        stopwords = ['배송']  # 여기에 실제 불용어 리스트를 넣으시면 됩니다
        self.df['comment'] = self.df['comment'].apply(lambda x: ' '.join([word for word in x.split() if word not in stopwords]))
        
        # comment 길이 상위 5%는 제거
        threshold = self.df['comment'].str.len().quantile(0.95)
        self.df = self.df[self.df['comment'].str.len() <= threshold]

        # 빈 문자열, 공백만 있는 문자열, NaN 값을 가진 행 모두 제거
        self.df = self.df[
            (self.df['comment'].notna()) &  # NaN 제거
            (self.df['comment'].str.strip() != '') &  # 공백만 있는 문자열 제거
            (self.df['comment'].str.len() > 0)  # 빈 문자열 제거
        ]

        self.processed_df = self.df
        print(len(self.processed_df))


    def feature_engineering(self):
        self.df['word_count'] = self.df['comment'].apply(lambda x: len(x.split()))
        self.df['text_length_category'] = self.df['word_count'].apply(
            lambda count: 'short' if count <= 1 else (
                'middle' if 2 <= count <= 4 else 'long'
            )
        )

        self.df['rating_length_category'] = self.df.apply(
            lambda row: f"{int(row['rating'])}-{row['text_length_category']}", axis=1
        )

        vectorizer: Any = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.df['comment'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), 
                                columns=vectorizer.get_feature_names_out())

        self.df = pd.concat([self.df.reset_index(drop=True), 
                               tfidf_df.reset_index(drop=True)], axis=1)

        self.df = self.df[self.df['word_count'] > 0]

        print("Feature engineering completed.")


    def save_to_database(self):
        self.processed_df.to_csv(os.path.join(self.output_dir, 'preprocessed_reviews_ssg.csv'))
        
