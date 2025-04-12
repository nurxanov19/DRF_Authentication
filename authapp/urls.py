from .views import RegisterApiView, LoginApiView, LogoutApiView, ProfileApiView
from django.urls import path

urlpatterns = [
    path('register', RegisterApiView.as_view(), name='register'),
    path('login', LoginApiView.as_view(), name='login'),
    path('logout', LogoutApiView.as_view(), name='logout'),
    path('profile', ProfileApiView.as_view(), name='profile'),
]