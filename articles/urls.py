from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('<int:pk>/record/', views.article_record, name='article_record'),
    
    path('user/recordings/', views.user_recording_list, name='user_recording_list'),
    path('user/recordings/<int:pk>/', views.user_recording_detail, name='user_recording_detail'),
    
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
]
