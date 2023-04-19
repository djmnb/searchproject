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


    user.login_ip = request.META.get("REMOTE_ADDR")
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
            "username":user.username,
            "createTime":user.create_time,
            "loginTime":user.login_time,
            "loginIp":user.login_ip,
            "status":user.status,
            "onlineCount":user.online_count,
            "uploadCount":user.upload_count,
            "isAdmin":user.is_admin
            },
            "data1":{
                "email":{"data":user.email,"editable":getUserFiled("email")},
                "username":{"data":user.username,"editable":getUserFiled("username")},
                "createTime":{"data":user.create_time,"editable":getUserFiled("create_time")},
                "loginTime":{"data":user.login_time,"editable":getUserFiled("login_time")},
                "loginIp":{"data":user.login_ip,"editable":getUserFiled("login_ip")},
                "status":{"data":user.status,"editable":getUserFiled("status")},
                "onlineCount":{"data":user.online_count,"editable":getUserFiled("online_count")},
                "uploadCount":{"data":user.upload_count,"editable":getUserFiled("upload_count")},
                "isAdmin":{"data":user.is_admin,"editable":getUserFiled("is_admin")}
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
    user = User.objects.get(email=email)

    verificationCode = cache.get(email + f"{Code.CODE_FORGET_PASSWORD}")
    if verificationCode == data["verificationCode"]:
        user.password = make_password(data["password"])
        user.save()
        return JsonResponse({"code": Code.IS_OK,"info":"修改成功"})
    else:
        return JsonResponse({"code": Code.CODE_ERROR,"info":"验证码错误"})
    
