import json
import logging
import time

from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from app.models import User,Question,SearchHistory
import app.code as Code
from app.utils import Data, send_verification_code,generate_email_verification_code, pic_to_text,questionSearchSystem
from django.core.cache import cache
from app.form import UserForm
from django.core.validators import EmailValidator, ValidationError
from app.middleware import check_is_login

   


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
    return JsonResponse({"code": Code.IS_OK,"info":"搜索成功","data":text})


ans = 1

@csrf_exempt
@check_is_login
def search(request):
    if request.method != 'POST':
        return HttpResponse("")

    
    data = Data(json.loads(request.body))
    
    searchText = data["searchText"]
    searchType = data["searchType"]

   
    if searchType == Code.SPECIAL_SEARCH:
        result = ""
        
    else:
         result = searchText

    top_n = questionSearchSystem.find_similar_question_ids(searchText,10)

    ids = [id for id,score in top_n]
    s = [score for id,score in top_n]
    logging.debug(s)

    # result = list(map(lambda id:Question.objects.get(id=id),ids))
    # result = list(map(lambda question:question.to_dict(),result))
    result = []
    for id in ids:
        question = Question.objects.get(id=id)
        result.append({"id":id,"title":question.title,"content":question.content})
    

    SearchHistory.objects.create(user=User.objects.get(email=request.session["email"]),search_text=searchText)
    

    return JsonResponse({"code": Code.IS_OK,"info":"搜索成功","data":result})


    
    



   