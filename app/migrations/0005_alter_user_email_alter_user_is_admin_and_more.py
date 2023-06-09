# Generated by Django 4.0.4 on 2023-04-18 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_is_admin_user_online_count_user_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(editable=False, max_length=254, unique=True, verbose_name='邮箱'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, editable=False, verbose_name='是否是管理员'),
        ),
        migrations.AlterField(
            model_name='user',
            name='login_ip',
            field=models.GenericIPAddressField(editable=False, verbose_name='登录ip'),
        ),
        migrations.AlterField(
            model_name='user',
            name='online_count',
            field=models.IntegerField(default=10, editable=False, verbose_name='剩余在线问答次数'),
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.IntegerField(default=0, editable=False, verbose_name='账号状态'),
        ),
        migrations.AlterField(
            model_name='user',
            name='upload_count',
            field=models.IntegerField(default=0, editable=False, verbose_name='上传题目数量'),
        ),
    ]
