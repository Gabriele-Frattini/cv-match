from django.urls import path
from base import views

urlpatterns = [
    path("", views.formView, name="home"),
    path("info", views.infoView, name="info")
]
