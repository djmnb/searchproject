import datetime
import json
import logging
from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from app.models import User
import app.code as Code
from app.utils import Data, send_verification_code,generate_email_verification_code,getUserFiled
from django.core.cache import cache
from app.form import UserForm
from django.core.validators import EmailValidator, ValidationError
from app.middleware import check_is_login
from django.contrib.auth.hashers import make_password, check_password

from django.utils import timezone




logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@csrf_exempt
def login(request):
    if request.method != 'POST':
       return HttpResponse("")
    

    
    data = Data(json.loads(request.body))
    user = User.objects.get(email=data["email"])


    
    logging.debug(user.login_time)
    if user.status == Code.USER_BAN:

        return JsonResponse({"code": Code.USER_BAN, "info": "用户已被封禁"})
    
    
    if not check_password(data["password"], user.password):
        return JsonResponse({"code": Code.PASSWORD_ERROR, "info": "密码错误"})
    
    request.session["email"] = data["email"]

    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if not ip:
        ip = request.META.get("REMOTE_ADDR") 
    user.login_ip = ip
    user.save()
    return JsonResponse({"code": Code.IS_OK, "info": "登录成功"})

@csrf_exempt
@check_is_login
def logout(request):
    if request.method != 'POST':
        return HttpResponse("")

    request.session.flush()
    return JsonResponse({"code": Code.IS_OK, "info": "退出成功"})


@check_is_login
@csrf_exempt
def getUserInfo(request):

    email = request.session.get("email")
    
    user = User.objects.get(email=email)
   
    return JsonResponse(
        {"code": Code.IS_OK,
         "info":"获取成功",
         "data":{
            "email":user.email,
            "password":user.password,
            "createTime":user.create_time,
            "loginTime":user.login_time,
            "loginIp":user.login_ip,
            "status":user.status,
            "tokens":user.tokens,
            "uploadCount":user.upload_count,
            "hasPermission":user.has_permission
            }
        })

@csrf_exempt
def sendcode(request):
    if request.method != "POST":
        return HttpResponse("")
    
    data = Data(json.loads(request.body))

    email = data["email"]
    codeType = data["codeType"]

    # 验证邮箱
    email_validator = EmailValidator()
    email_validator(email)

        
    if codeType == Code.CODE_REGISTER:
        try:
            User.objects.get(email=email)
            return JsonResponse({"code": Code.USER_EXIST, "info": "用户已经存在"})
        except User.DoesNotExist:
            pass
    elif codeType == Code.CODE_FORGET_PASSWORD:
        User.objects.get(email=email) 
    else:
        return HttpResponse("")
       
    verificationCode = generate_email_verification_code()
    send_verification_code(email, verificationCode)
    cache.set(email + f"{codeType}", verificationCode, 60 * 5)

    return JsonResponse({"code": Code.IS_OK, "info": "验证码发送成功"})
    

@csrf_exempt
def register(request):

    if request.method != 'POST':
        return HttpResponse("")

    data = Data(json.loads(request.body))
    email = data["email"]   
    password = data["password"]
    confirmPassword = data["confirmPassword"]

    if password != confirmPassword:
        return JsonResponse({"code": Code.PASSWORD_NOT_MATCH,"info":"两次密码不一致"})

    verificationCode = cache.get(email + f"{Code.CODE_REGISTER}")
    logging.debug(verificationCode)
    

    if verificationCode == data["verificationCode"]:
        User.objects.create(email=email, password=make_password(password),login_ip=request.META.get("REMOTE_ADDR"))
        return JsonResponse({"code": Code.IS_OK,"info":"注册成功"})
    else:
        return JsonResponse({"code": Code.CODE_ERROR,"info":"验证码错误或者过期"})
        
            
@csrf_exempt
def changepassword(request):
    if request.method != 'POST':
        return HttpResponse("")

    data = Data(json.loads(request.body)) 
    email = data["email"]
    password = data["password"]
    confirmPassword = data["confirmPassword"]
    if password != confirmPassword:
        return JsonResponse({"code": Code.PASSWORD_NOT_MATCH,"info":"两次密码不一致"})
    
    user = User.objects.get(email=email) 
    
    try:
        oldPassword = data["oldPassword"]
        if not check_password(oldPassword, user.password):
            return JsonResponse({"code": Code.PASSWORD_ERROR, "info": "密码错误"})
        else:
            user.password = make_password(password)
            user.save()
            request.session.flush()
            return JsonResponse({"code": Code.IS_OK,"info":"修改成功,请重新登录"})
    except Exception as e:
        pass
    

    

    verificationCode = cache.get(email + f"{Code.CODE_FORGET_PASSWORD}")  
    if verificationCode == data["verificationCode"]:
        user.password = make_password(data["password"])
        user.save()
        return JsonResponse({"code": Code.IS_OK,"info":"修改成功"})
    else:
        return JsonResponse({"code": Code.CODE_ERROR,"info":"验证码错误"})
    
