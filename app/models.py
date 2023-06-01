from django.utils import timezone
from django.db import models



# Create your models here.

class User(models.Model):
    email = models.EmailField(verbose_name="邮箱",unique=True,editable=False)
    password = models.CharField(max_length=100,verbose_name="密码",editable=False)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间",editable=False)
    login_time = models.DateTimeField(auto_now=True,verbose_name="登录时间",editable=False) 
    login_ip = models.GenericIPAddressField(verbose_name="登录ip",editable=False)  
    tokens = models.IntegerField(verbose_name="剩余token数量",default=10000)
    upload_count = models.IntegerField(verbose_name="上传题目数量",default=0,editable=False)
    has_permission = models.BooleanField(verbose_name="是否具有通过chatgpt生成题目的权限",default=False)
    status = models.BooleanField(verbose_name="账号状态",default=True)  # 账号当前状态,True为正常,False为被封禁

    def __str__(self):
        return self.email
    
    def account_status(self):
        return "被封禁" if not self.status else "正常"
    account_status.short_description = '账号状态'


    

class Question(models.Model):
    title = models.TextField(verbose_name="题目")
    content = models.TextField(verbose_name="解答内容")
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="用户",default=1)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")
    def __str__(self):
        return self.title


class SearchHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="用户",default=1)
    title = models.TextField(verbose_name="搜索内容")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")


    
