from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('',views.index),
    path('login',views.login),
    path('painelCampus/',views.selectCampus),
    path('painelCampus/<str:campus>/',views.showPainelCampus),
    path('indicesDeMerito',views.indicesDeMerito),
    path('envios', views.listaEnvios)
]
