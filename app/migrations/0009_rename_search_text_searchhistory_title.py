# Generated by Django 4.0.4 on 2023-05-13 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_searchhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='searchhistory',
            old_name='search_text',
            new_name='title',
        ),
    ]