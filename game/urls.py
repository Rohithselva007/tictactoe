from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_view, name='game'),
    path('register/', views.register, name='register'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('history/', views.history, name='history'),
    path('api/move/<int:session_id>/', views.make_move, name='make_move'),
]
