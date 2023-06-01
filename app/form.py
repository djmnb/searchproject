
from django import forms
from .models import User

class UserForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[(True, '解封'), (False, '封禁')],label="账户操作")
    # is_admin = forms.ChoiceField(choices=[(True, ''), (False, '普通用户')],label="用户身份")

    class Meta:
        model = User
        fields = '__all__'

