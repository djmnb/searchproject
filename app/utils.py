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
from app.models import User, Question
import numpy as np
from elasticsearch import Elasticsearch, helpers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    


class QuestionElasticsearch:
    def __init__(self):
        self.es = Elasticsearch()
        self.index_name = "questions"
        self.create_index()

    def create_index(self):
        
        self.es.indices.create(index=self.index_name, ignore=400)

    def add_question(self, question):
        doc = {
            'title': question.title,
            'id': question.id,
        }
        self.es.index(index=self.index_name, id=question.id, document=doc)

    def delete_question(self, question_id):
        self.es.delete(index=self.index_name, id=question_id)
        
    def update_question(self, question):
        doc = {
            'title': question.title,
            'id': question.id,
        }
        self.es.update(index=self.index_name, id=question.id, doc=doc)

    def search_questions(self, title, size=10):
        query = {
             "match": {
                    "title": title
                }
        }
        res = self.es.search(index=self.index_name,query=query, size=size)
        data = []
        for hit in res['hits']['hits']:
            hit["_source"]["score"] = hit["_score"]
            data.append(hit["_source"])
        print(data)
        return data
    
    def bulk_add_questions(self, questions):
        actions = [
            {
                "_index": self.index_name,
                "_id": question.id,
                "_source": {
                    "title": question.title,
                    "id": question.id,
                }
            }
            for question in questions
        ]
        helpers.bulk(self.es, actions)
    def clear_index(self):
        self.es.indices.delete(index=self.index_name, ignore=[400, 404])
        self.create_index()
    
    def load_data(self):

        if self.es.indices.exists(index=self.index_name):
            return
        logging.debug("load data")
        self.clear_index()
        questions = Question.objects.all()
        self.bulk_add_questions(questions)
    

questionElasticsearch = QuestionElasticsearch()
questionElasticsearch.load_data()



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

