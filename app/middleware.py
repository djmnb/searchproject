from functools import wraps
from json import JSONDecodeError
import logging
from smtplib import SMTPRecipientsRefused
from django.urls import resolve
from app import code as Code
from django.http import JsonResponse
from django.core.exceptions import SuspiciousFileOperation,RequestDataTooBig,ValidationError
from app.models import User,Question
from app.utils import ParamError
from django.core.paginator import EmptyPage



def check_is_login(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.session.get("email") is None:
            return JsonResponse({"code": Code.USER_NOT_LOGIN, "info": "用户未登录"})
        return func(request, *args, **kwargs)
    return wrapper

class ExcptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            match = resolve(request.path)
        except Exception as e:
            return JsonResponse({"code": Code.NOT_FOUND, "info": "请求不存在"})

        return self.get_response(request)

    def process_view(self,request,view_func,view_args,view_kwargs):
        try:
            return view_func(request,*view_args,**view_kwargs)
        except User.DoesNotExist as e:
            return JsonResponse({"code": Code.USER_NOTFOUND, "info": "用户不存在","error":str(e)})

        except (SuspiciousFileOperation,RequestDataTooBig) as e:
            return JsonResponse({"code": Code.FILE_LAGER_THAN_5M, "info": "文件超过5M","error":str(e)})

        except (SMTPRecipientsRefused) as e :
            return JsonResponse({"code": Code.EMAIL_NOT_VALID, "info": "验证码发送失败,请检查邮箱是否正确","error":str(e)})
        
        except ValidationError as e:
            return JsonResponse({"code": Code.EMAIL_NOT_VALID, "info": "邮箱不合法","error":str(e)})
        
        except Question.DoesNotExist as e:
            
            return JsonResponse({"code": Code.QUESTION_NOT_FOUND, "info": "题目不存在","error":str(e)})
        
        except JSONDecodeError as e:
            return JsonResponse({"code": Code.DATA_FORMAT_ERROR, "info": "数据格式错误","error":str(e)})

        except ParamError as e:
            logging.exception(e)
            return JsonResponse({"code": Code.PARAM_ERROR, "info": "参数错误","error":str(e)})
        
        except EmptyPage as e:
            return JsonResponse({"code": Code.PAGE_NOT_FOUND, "info": "页码不存在","error":str(e)})
        except Exception as e:
            logging.debug(type(e))
            logging.exception(e)
            return JsonResponse({"code": Code.SERVER_ERROR, "info": "服务器错误","error":str(e)})
        
    

    