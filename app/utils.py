import json
import logging
import random
import re
import string
import requests

from searchproject import settings
from django.core.mail import EmailMultiAlternatives
from email.utils import formataddr
from app import code as Code
from app.models import Question, User
import numpy as np
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
from scipy.sparse import vstack


def tokenize_question(question):

    tokens = list(jieba.cut(question))
    print(tokens)
    return tokens
    # # 使用正则表达式匹配中文字符和英文单词
    # words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', question)
    # tokens = []
    
    # for word in words:
    #     # 如果是中文，使用 jieba 分词
    #     if re.match(r'[\u4e00-\u9fff]+', word):
    #         tokens.extend(list(jieba.cut(word)))
    #     # 如果是英文，直接添加到 tokens 列表
    #     else:
    #         tokens.append(word)
    # print(tokens)
    # return tokens

def load_questions_from_database():
    return Question.objects.all()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    

class QuestionSearchSystem:
    def __init__(self,flag=True,matrix_path='tfidf_matrix.pickle', ids_path='ids.pickle', vectorizer_path='vectorizer.pickle'):
        self.matrix_path = matrix_path
        self.ids_path = ids_path
        self.vectorizer_path = vectorizer_path

        if os.path.exists(matrix_path) and os.path.exists(ids_path) and os.path.exists(vectorizer_path) and flag:
            self.tfidf_matrix = self.load_matrix(matrix_path)
            self.ids = self.load_ids(ids_path)
            self.vectorizer = self.load_vectorizer(vectorizer_path)
            logging.debug("==========load data from pickle==========")
        else:
            all_questions = load_questions_from_database()
            self.ids = [question.id for question in all_questions]
            all_questions = [str(question.title) for question in all_questions]
            
            self.vectorizer = TfidfVectorizer(tokenizer=tokenize_question) # 生成tfidf向量
            self.tfidf_matrix = self.vectorizer.fit_transform(all_questions) # 生成tfidf矩阵
            logging.debug("==========load data from database==========")
            print(self.ids)
            print(self.tfidf_matrix)

            # self.save_all_data(matrix_path, ids_path, vectorizer_path)  # 保存所有数据
       

    def load_matrix(self, matrix_path):
        with open(matrix_path, 'rb') as f:
            matrix = pickle.load(f)
        return matrix

    def save_matrix(self, matrix_path, matrix):
        with open(matrix_path, 'wb') as f:
            pickle.dump(matrix, f)

    def load_ids(self, ids_path):
        with open(ids_path, 'rb') as f:
            ids = pickle.load(f)
        return ids

    def save_ids(self, ids_path, ids):
        with open(ids_path, 'wb') as f:
            pickle.dump(ids, f)

    def load_vectorizer(self, vectorizer_path):
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        return vectorizer

    def save_vectorizer(self, vectorizer_path, vectorizer):
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)

    def save_all_data(self):
        self.save_matrix(self.matrix_path, self.tfidf_matrix)
        self.save_ids(self.ids_path, self.ids)
        self.save_vectorizer(self.vectorizer_path, self.vectorizer)

    def train_new_question(self, new_question):

        self.ids.append(new_question.id)

        # 使用向量器处理新问题
        new_question_vector = self.vectorizer.transform([new_question.title])

        # 如果 tfidf_matrix 为空（即没有之前的问题），则将 new_question_vector 赋值给它
        if self.tfidf_matrix is None:
            self.tfidf_matrix = new_question_vector
        else:
            # 否则，将新问题向量添加到现有矩阵中
            self.tfidf_matrix = vstack((self.tfidf_matrix, new_question_vector))
            # self.tfidf_matrix = np.concatenate((self.tfidf_matrix, new_question_vector), axis=0)
        
        # self.ids.append(new_question.id)
        # new_question_vector = self.vectorizer.transform([new_question.title]) # 生成新问题的tfidf向量
        # self.tfidf_matrix = np.vstack([self.tfidf_matrix, new_question_vector]) # 将新问题的tfidf向量添加到tfidf矩阵中

        # self.save_all_data(self.matrix_path, self.ids_path, self.vectorizer_path) # 保存所有数据

    def find_similar_question_ids(self, query, top_n=10):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)
        sorted_indices = np.argsort(similarities[0])[::-1]  # 按降序排列
        top_n_indices = sorted_indices[:top_n]
        top_n_ids = [self.ids[index] for index in top_n_indices]
        top_n_similarities = [similarities[0][index] for index in top_n_indices]

        return list(zip(top_n_ids, top_n_similarities))


# questionSearchSystem = QuestionSearchSystem(False)
questionSearchSystem = None


class ParamError(Exception):
    pass

class Data:
    def __init__(self,data) -> None:
        self.data = data

    def __getitem__(self,key):

        if key not in self.data:
            raise ParamError(f"paramer {key} not found")
        return self.data[key]
    
    def __setitem__(self,key,value):
        self.data[key] = value
    
    def __getter__(self,key):
        if key not in self.data:
            raise ParamError(f"paramer {key} not found")
        return self.data[key]
    
    def __setter__(self,key,value):
        self.data[key] = value
        

def generate_email_verification_code(length=6):
    characters = string.digits

    return ''.join(random.choice(characters) for _ in range(length))



def send_verification_code(to_email, verification_code):
    subject = f'搜题系统验证码'
    plain_text_message = f'您的验证码为: {verification_code},五分钟内有效'
    html_message = f'<p>您的验证码为: <span style="color: blue; text-decoration: underline;">{verification_code}</span>,五分钟内有效</p>'
    from_email = formataddr(('搜题系统',settings.EMAIL_HOST_USER))

    email = EmailMultiAlternatives(subject, plain_text_message, from_email, [to_email])
    email.attach_alternative(html_message, "text/html")
    email.send()

def pic_to_text(base):

    response = requests.post("https://apis.tianapi.com/ocrimg/index",data={
        "key":"5e9360db6f03f34a8060c210a636bc48",
        "img":base
    },headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    info = json.loads(response.content.decode("utf-8"))
    print(info)


    if info["code"] == 200:
        data,code = "".join(map(lambda text:text["texts"],info["result"]["list"])),Code.IS_OK
    else:
        data,code = info, Code.PICTRURE_ERROR
        print(info)
    return data,code

def getUserFiled(fieldname,attrname="editable"):
    if hasattr(User._meta.get_field(fieldname),attrname):
        return getattr(User._meta.get_field(fieldname),attrname)
    return False

