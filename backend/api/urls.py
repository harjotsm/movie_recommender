from django.urls import path
from . import views

urlpatterns = [
    path('options/', views.get_options, name='get_options'),
    path('recommend/', views.recommend_movies, name='recommend_movies'),
]