

import json
import logging
import time
from django.http import HttpResponse, JsonResponse
from app import code as Code    
from app.middleware import check_is_login
from app.models import Question, User,SearchHistory
from django.views.decorators.csrf import csrf_exempt

from app.utils import Data,questionSearchSystem
from django.core.paginator import Paginator
from django.core import serializers



@check_is_login
@csrf_exempt
def getquestion(request):
    if request.method == 'GET':
        return HttpResponse("")
    
    data = Data(json.loads(request.body))

    id = data["id"]
    
    if id == -1:

        getType = data["getType"]

        allQuestion = Question.objects.all() if getType == Code.ALL_QUESTION else Question.objects.filter(user__email=request.session["email"])

        total = allQuestion.count()
        
        page = data["page"]
        pageSize = data["pageSize"]
        paginator = Paginator(allQuestion, pageSize)
        questions = paginator.page(page)

    else:
        total = Question.objects.count()
        questions = list(Question.objects.filter(id=id))
        getType = Code.SINGEL_QUESTION
    
    result = []
    for q in questions:
        result.append({
                "title": q.title,
                "id": q.id,
                "answer": q.content,
                "createTime": q.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "updateTime": q.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                "user": q.user.username
        })
    

    

    
    return JsonResponse({"code": Code.IS_OK, "info": "获取成功", "data": result,"total":total,"getType":getType})

@check_is_login
@csrf_exempt
def uploadquestion(request):
    if request.method == 'GET':
        return HttpResponse("")
    
    email = request.session["email"]
    user = User.objects.get(email=email)

    data = Data(json.loads(request.body))
    title = data["title"]
    content = data["content"]
    question = Question.objects.create(title=title,content=content,user=user)
    
    questionSearchSystem.train_new_question(question)
    # questionSearchSystem.train_new_question(question)
    return JsonResponse({"code": Code.IS_OK, "info": "上传成功"})

@check_is_login
@csrf_exempt
def deletequestion(request):
    if request.method == 'GET':
        return HttpResponse("")
    
    data = Data(json.loads(request.body))
    id = data["id"]
    Question.objects.filter(id=id).delete()
    return JsonResponse({"code": Code.IS_OK, "info": "删除成功"})

@check_is_login
@csrf_exempt
def getsearchhistory(request):
    if request.method == 'GET':
        return HttpResponse("")
    
    
    email = request.session["email"]
    data = Data(json.loads(request.body))

    searchHistory = SearchHistory.objects.filter(user__email=email)

    total = searchHistory.count()
    
    page = data["page"]
    pageSize = data["pageSize"]
    paginator = Paginator(searchHistory, pageSize)
    histories = paginator.page(page)

    result = []

    for h in histories:
        result.append({
                "id": h.id,
                "title": h.title,
                "createTime": h.create_time.strftime("%Y-%m-%d %H:%M:%S")
        })


    return JsonResponse({"code": Code.IS_OK, "info": "获取成功", "data": result,"total":total})
    
    