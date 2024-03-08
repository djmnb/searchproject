# 搜题系统后端

## 简介

此项目用于搜索题目,  管理员可以后台添加题目, 也可以通过ChatGPT生成题库添加到题库中,  如果题库中没有相应题目, 还可以与ChatGPT直接问答,  使用elasticsearch引擎来通过关键字匹配题目

## 使用

### 安装依赖

```shell
pip install -r requirements.txt
```

### 安装elasticsearch

[下载地址](https://www.elastic.co/cn/downloads/past-releases/elasticsearch-7-9-3)

根据平台选择不同的版本, 下载后解压缩找到bin目录执行对应脚本启动

### 修改邮箱信息

在setting.py中修改成自己的邮箱信息, 当然,你也可以默认使用我的

![image-20240308150403037](img/READMEassets/image-20240308150403037.png)

### 启动项目

```shell
python .\manage.py runserver  #默认启动在8000端口
python manage.py runserver 8080  # 这样可以改成8080端口
```

### 修改openaikey

如果需要使用聊天功能, 以及自动生成题目功能, 需要提供自己的openaikey,在utils.py中

```Python
openai.api_key = "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"
```

## 自动生成题目介绍

大体流程: 

1. 用户输入题目类型关键字(比如c++)  
2. 获取这个关键字的大纲
3. 获取每个大纲对应的知识点
4. 获取知识点对应的题目
5. 根据题目获取答案

```python
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
```

# 后台管理系统

## 简介

这是用户数据, 题目数据 的管理系统,  在Django提供的后台管理系统的基础上进行的修改

## 使用

### 创建管理员用户

> 这一步也要启动那个搜索引擎elasticsearch的

```shell
python manage.py createsuperuser
```

按照提示一步步输入信息创建用户, 当然,如果使用了我的数据库, 可以使用默认的 :

```
账号: admin
密码: admin
```

### 登录

启动搜题系统后, 访问地址  服务器ip:端口/admin

## 展示

### 登录页面

![image-20240308151309805](img/READMEassets/image-20240308151309805.png)

### 主页面

![image-20240308151336591](img/READMEassets/image-20240308151336591.png)

### 用户和题目数据页面

![image-20240308151407465](img/READMEassets/image-20240308151407465.png)

![image-20240308151357669](img/READMEassets/image-20240308151357669.png)