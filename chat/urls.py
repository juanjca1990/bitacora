from django.urls import path
from chat.views import *

urlpatterns = [
    path('', chat_view, name='chat'),
    path('api/message/', send_message, name='send_message'),
]