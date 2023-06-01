import json
import logging
import time

from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from app.models import User,Question,SearchHistory
import app.code as Code
from app.utils import Data, send_verification_code,generate_email_verification_code, pic_to_text,questionElasticsearch
from django.core.cache import cache
from app.form import UserForm
from django.core.validators import EmailValidator, ValidationError
from app.middleware import check_is_login
import openai
import json




# 添加自己的api_key
openai.api_key = "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"


@csrf_exempt
def test(request):
    print("hello")
    return HttpResponse("hello world")

@csrf_exempt
@check_is_login
def uploadpic(request):
    if request.method != 'POST':
        return HttpResponse("")
    data = json.loads(request.body)
    
    image = data['image']
    text,code = pic_to_text(image)

    if code != Code.IS_OK:
        return JsonResponse({"code": code,"info":"图片识别失败"})
    return JsonResponse({"code": Code.IS_OK,"info":"图片识别成功","data":text})



@csrf_exempt
@check_is_login
def search(request):
    if request.method != 'POST':
        return HttpResponse("")

    data = Data(json.loads(request.body))
    searchText = data["searchText"]
    questionNums = data["questionNums"]
    result = questionElasticsearch.search_questions(searchText,questionNums)
    
    SearchHistory.objects.create(user=User.objects.get(email=request.session["email"]),title=searchText)

    

    return JsonResponse({"code": Code.IS_OK,"info":"搜索成功","data":result})


# 在线问答功能
@csrf_exempt
@check_is_login
def chat(request):

    user = User.objects.get(email=request.session.get("email"))
    data = Data(json.loads(request.body))

    if user.tokens <= 0:
        return JsonResponse({"code": Code.NOT_ENOUGH,"info":"token数量不足,请联系管理员充值"})
    modelType = data["modelType"]
    messages = data["messages"]

    logging.info(modelType)
    logging.info(messages)

    response = openai.ChatCompletion.create(
        model=modelType,
        messages=messages,
        max_tokens=2048,
    )
    result = response["choices"][0]["message"]
    usage = response["usage"]
    user.tokens -= usage["total_tokens"]
    user.save()

    logging.info(result)
    return JsonResponse({"code": Code.IS_OK,"info":"搜索成功","data":{"result":result,"totalTokens":usage["total_tokens"],"allTokens":user.tokens}})

    



   