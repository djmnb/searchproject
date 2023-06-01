"""searchproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views
from app.views import quesion_views, user_views,views




userUrlPatterns = [
    path('login/', user_views.login),
    path('register/', user_views.register),
    path('changepassword/', user_views.changepassword),
    path('sendcode/', user_views.sendcode),
    path('logout/', user_views.logout),
    path('getuserinfo/', user_views.getUserInfo),
]

questionUrlPatterns = [
    path('getquestion/', quesion_views.getquestion),
    path('uploadquestion/', quesion_views.uploadquestion),
    path('gethistory/',quesion_views.getsearchhistory),
    path('deletequestion/',quesion_views.deletequestion),
    path('changequestion/',quesion_views.changequestion),
    path('deletehistory/',quesion_views.deletehistory),
]


# 这里设置url路径

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include(userUrlPatterns)),
    path('question/',include(questionUrlPatterns)),
    path('search/', views.search),
    path('uploadpic/', views.uploadpic),
    path('chat/', views.chat),
    path("test/",views.test)
]

