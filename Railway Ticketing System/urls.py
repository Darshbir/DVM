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
    path('admin_register/', admin_register, name = "admin_register"),
    path('ban_screen/', ban_screen, name = "ban_screen"),
    path('ban_user/', ban_user, name = "ban_user"),
    path('ban/<int:user_id>/', ban, name = "ban"),
    path('unban/<int:user_id>/', unban, name = "unban"),
    path('staff/', staff, name = "staff"),
    path('add_train/', add_train, name = "add_train"),
    path('update_train/<int:train_id>/' , update_train , name="update_train"),
    path('delete_train/<int:train_id>/' , delete_train , name="delete_train"),
    path('booking/', booking, name = "booking"),
    path('bookings/<int:train_id>/', train_bookings, name = "train_bookings"),
    path('delete_booking/<int:booking_id>/', delete_booking, name = "delete_booking"),
    path('user_delete_booking/<int:booking_id>/', user_delete_booking, name = "user_delete_booking")
]
