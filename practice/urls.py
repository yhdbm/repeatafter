from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/next/', views.next_sentence, name='next'),
    path('api/score/', views.score, name='score'),
    path('api/tts/', views.tts, name='tts'),
    path('api/saved/', views.saved, name='saved'),
    path('api/stats/', views.stats, name='stats'),
]
