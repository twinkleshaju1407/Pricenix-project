from django.urls import path
from . import views

urlpatterns = [
    path('approve/<int:product_id>/', views.approve_price, name='approve_price'),
    path('reject/<int:product_id>/', views.reject_price, name='reject_price'),

    # UiPath Bot Endpoints
    path('uipath/trigger/', views.trigger_uipath_job, name='trigger_uipath_job'),
    path('uipath/status/<str:job_key>/', views.uipath_job_status, name='uipath_job_status'),

    # AI Chatbot
    path('chatbot/', views.chatbot, name='chatbot'),
]
