from django.contrib import admin
from app.form import UserForm

# Register your models here.
from app.models import User,Question



class UserAdmin(admin.ModelAdmin):
    list_display = ('email','account_status','is_admin','tokens','upload_count','create_time','login_ip','login_time')
    form = UserForm




admin.site.register(User,UserAdmin)
admin.site.register(Question)

