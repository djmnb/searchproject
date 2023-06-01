import json
import logging
import os
import random

import string
import time
import requests

from searchproject import settings
from django.core.mail import EmailMultiAlternatives
from email.utils import formataddr
from app import code as Code
from app.models import User, Question
from elasticsearch import Elasticsearch, helpers
import websockets
import asyncio

import openai
import json

from threading import Thread
from django.contrib.sessions.models import Session

# 获得openai的api_key
openai.api_key = "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"


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    
# websocket_server.py
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from asgiref.sync import sync_to_async

# 令牌桶算法
class TokenBucket:
    # tokens: 令牌桶的大小
    # fill_rate: 令牌桶的填充速率(每秒填充的令牌数)
    def __init__(self, tokens, fill_rate):
        self.tokens = tokens
        self.fill_rate = fill_rate
        self.last_time = time.monotonic()

    async def consume(self,nums):
        while self.tokens < nums:
            await asyncio.sleep(nums)
            self.tokens += (time.monotonic() - self.last_time) * self.fill_rate
            self.last_time = time.monotonic()

        self.tokens -= nums

tokenBucket = TokenBucket(50, 1)

def mySplit(s):
    try:
        return s.split(".")[1].strip()
    except Exception as e:
        return ""

# 拿到我们想要的数据函数
def getData(content):
    # 进行分割,去除无用的分割,并且去掉首尾空白字符,以及去掉序号
    data = map(mySplit, filter(lambda x: x.strip() != "", content.split("\n")))
    # 再过滤一下,去掉空字符串
    data = list(filter(lambda x: x != "", data))
    return data

class GenerateQuesions:

    def __init__(self,questionsType,send) -> None:
        self.questionsType = questionsType
        self.aiRole = "你是一个无所不知的教师" 
        self.send = send
        
    # 获得大纲
    async def getOutlines(self):

        logging.info("正在获取大纲")

        response = await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt=f"全面总结一下关于{self.questionsType}的学习知识点,每个知识点不涉及太多内容,必须严格返回格式为: 序号. 内容(内容是一行)",
            max_tokens=2500,
        )


        content = response["choices"][0]["text"].strip()
        print("获得大纲:=========================================================")
        print(content)
        print("=========================================================")        
        return getData(content),response["usage"]["total_tokens"]
    # 获的问题和知识点
    async def getKnowledges(self,outline):

        logging.info("正在获取知识点")

        response =await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt=f"全面总结一下关于{self.questionsType}中的{outline}问题,请尽可能多一点,如果不存在问题,可以返回空数据: 序号.问题",
            max_tokens=2500,
        )

        content = response["choices"][0]["text"].strip()
        knowledges = getData(content)
        print(f"大纲{outline}涉及的知识点和问题:=========================================================")
        print(knowledges)
        print("=========================================================")

        
        return knowledges,response["usage"]["total_tokens"]
    

    # 获得题目或者知识点的解答
    async def getAnswer(self,knowledge):

        response = await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt=f"解答或者总结一下关于{self.questionsType}中的{knowledge}",
            max_tokens=2000,
        )

        return response["choices"][0]["text"].strip(),response["usage"]["total_tokens"]
        
    
    # 获得所有的题目和解答
    async def getQuesions(self):

        outlines,total_tokens = await self.getOutlines()
        print("获取大纲消耗的token数:=========================================================")
        print(f"{total_tokens}")
        print(f"大纲: {outlines}")

        await self.send(json.dumps({"type":"outlines","content":outlines}))


        allQuestions = []

        for outline in outlines:
            knowledges,tempt = await self.getKnowledges(outline)
            print("获取知识点消耗的token数:=========================================================")
            print(f"{tempt}")
            total_tokens += tempt
            print(f"大纲{outline}涉及的知识点和问题: {knowledges}")
            await self.send(json.dumps({"type":"total_tokens","content":total_tokens}))

            i = 0

            knowledgeQuestions = []
            nums = 15

            while i < len(knowledges):
                tasks = [asyncio.create_task(self.getAnswer(knowledge)) for knowledge in knowledges[i:i+nums]]
                await tokenBucket.consume(nums)
                results = await asyncio.gather(*tasks)
                tempQuestions = [{"title":knowledge,"answer":result[0]} for knowledge,result in zip(knowledges[i:i+nums],results)]
                print(tempQuestions)
                allQuestions.extend(tempQuestions)
                knowledgeQuestions.extend(tempQuestions)
                tempt = sum([result[1] for result in results])
                total_tokens += tempt
                await self.send(json.dumps({"type":"total_tokens","content":total_tokens}))
                print("获取题目消耗的token数:=========================================================")
                print(f"{tempt}")
                i += nums
            await self.send(json.dumps({"type":"questions","content":knowledgeQuestions}))  
    

        print("total_tokens:=========================================================")
        print(f"{total_tokens}")                       
        return allQuestions,total_tokens

alreadys = set()

async def checkPermission(data,send):
    if "email" not in data or "password" not in data:
        await send(json.dumps({"type":"error","content":"认证信息不能为空"}))
        return False
    query = await sync_to_async(User.objects.filter)(email=data["email"])
    user = await sync_to_async(query.first)()
    if user is None:
        await send(json.dumps({"type":"error","content":"用户不存在"}))
        return False
    
    
    if data["password"] != user.password:
        await send(json.dumps({"type":"error","content":"认证失败"}))
        return False
    if not user.has_permission:
        await send(json.dumps({"type":"error","content":"您没有权限"}))
        return False
    return True


    

async def echo(websocket, path):
    async for message in websocket:
        
        if len(alreadys) == 1:
            await websocket.send(json.dumps({"type":"error","content":"请勿频繁请求,休息一会吧"}))
            if websocket not in alreadys:
                return 
        alreadys.add(websocket)

        logging.info(f"收到消息: {message}")
        try:
            data = json.loads(message)
        except Exception as e:
            await websocket.send(json.dumps({"type":"error","content":"数据格式错误"}))
            alreadys.remove(websocket)
            return

        isOk = await checkPermission(data,websocket.send)
        if isOk:
            # await asyncio.sleep(3)
            # await websocket.send(json.dumps({"type":"outlines","content":['outline1','outline2']}))
            # await asyncio.sleep(3)
            # await websocket.send(json.dumps({"type":"questions","content":[{"title":"hello","answer":"hello"},{"title":"hello","answer":"hello"}]}))
            # await asyncio.sleep(3)
            # await websocket.send(json.dumps({"type":"questions","content":[{"title":"hello2","answer":"hello2"},{"title":"hello2","answer":"hello2"}]}))
            # await asyncio.sleep(3)
            # await websocket.send(json.dumps({"type":"finish","content":"生成完毕"}))
            # await asyncio.sleep(100)

            if "content" not in data or data["content"] == "":
                await websocket.send(json.dumps({"type":"error","content":"content不能为空"}))
                alreadys.remove(websocket)
                return
            try:
                 allQuestions,total_tokens =  await GenerateQuesions(data["content"],websocket.send).getQuesions()
            except Exception as e:
                await websocket.send(json.dumps({"type":"finish","content":"出现网络问题,暂停生成,请稍后再试"}))
            else:
                await websocket.send(json.dumps({"type":"finish","content":"生成完毕"}))

            await websocket.send(json.dumps({"type":"total_tokens","content":total_tokens}))
       
        
        alreadys.remove(websocket)
        return
       


def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(echo, '0.0.0.0', 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()


thread = Thread(target=start_websocket_server)

thread.daemon = True

thread.start()


ES_HOST = os.getenv('ES_HOST', 'localhost')
class QuestionElasticsearch:
    def __init__(self):
        self.es = Elasticsearch(hosts=[ES_HOST]) 
        self.index_name = "questions"

        # 检查索引,主要是为了检测连接是否成功
        self.es.indices.exists(index=self.index_name)

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
        print('开始加载数据')
        self.create_index()
        questions = Question.objects.all()
        self.bulk_add_questions(questions)
        logging.info("加载数据完毕")
    
max_retries = 10
retry_count = 0

while retry_count < max_retries:
    try:
        logging.info("正在尝试连接Elasticsearch服务器")
        questionElasticsearch = QuestionElasticsearch()
        break
    except Exception as e:
        retry_count += 1
        print(f"连接失败 正在重试 ({retry_count}/{max_retries})...")
        time.sleep(5)

if retry_count == max_retries:
    print("连接失败,请检查Elasticsearch服务器是否出现问题")
else:
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

