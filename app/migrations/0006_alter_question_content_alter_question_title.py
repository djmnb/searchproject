# Generated by Django 4.0.4 on 2023-04-18 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_user_email_alter_user_is_admin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='content',
            field=models.TextField(verbose_name='解答内容'),
        ),
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.TextField(max_length=100, verbose_name='题目'),
        ),
    ]
