"""
URL configuration for DVM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from task.views import *
from django.urls import path , include, re_path
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home , name = "home"),
    path('login/', login_page, name = "login_page"),
    path('register/', register_page, name = "register_page"),
    path('logout/', logout_page, name ="logout_page"),
    path('book/', book_page , name = "book_page" ),
    path('book/<int:train_id>/', book_page, name="book_page"),
    path('profile/', profile, name = "profile"),
    path('accounts/', include('allauth.urls')),
]
