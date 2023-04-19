from django.utils import timezone
from django.db import models



# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=20,verbose_name="用户名",editable=True)
    email = models.EmailField(verbose_name="邮箱",unique=True,editable=False)
    password = models.CharField(max_length=20,verbose_name="密码",editable=True)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间",editable=False)
    login_time = models.DateTimeField(auto_now=True,verbose_name="登录时间",editable=False)
    login_ip = models.GenericIPAddressField(verbose_name="登录ip",editable=False)  
    online_count = models.IntegerField(verbose_name="剩余在线问答次数",default=10,editable=False)
    upload_count = models.IntegerField(verbose_name="上传题目数量",default=0,editable=False)
    is_admin = models.BooleanField(verbose_name="是否是管理员",default=False,editable=False)
    status = models.IntegerField(verbose_name="账号状态",default=0,editable=False)  # 账号当前状态,0为正常,1为被封禁
    



    

class Question(models.Model):
    title = models.TextField(verbose_name="题目")
    content = models.TextField(verbose_name="解答内容")
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="用户",default=1)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")


class SearchHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="用户",default=1)
    search_text = models.TextField(verbose_name="搜索内容")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    
