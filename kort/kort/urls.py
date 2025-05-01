"""
URL configuration for kort project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from ristiseiska.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('players/', PlayerListView.as_view(), name='player_list'),
    path('players/create/', PlayerCreateView.as_view(), name='player_create'),
    path('players/<int:pk>/update/', PlayerUpdateView.as_view(), name='player_update'),
    path('players/<int:pk>/delete/', PlayerDeleteView.as_view(), name='player_delete'),
    path('seasons/', SeasonListView.as_view(), name='season_list'),
    path('seasons/create/', SeasonCreateView.as_view(), name='season_create'),
    path('seasons/<int:pk>/update/', SeasonUpdateView.as_view(), name='season_update'),
    path('seasons/<int:pk>/delete/', SeasonDeleteView.as_view(), name='season_delete'),
    path('season/<int:pk>/', SeasonDetailView.as_view(), name='season_detail'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/create/', GameCreateView.as_view(), name='game_create'),
    path('', GameCreateView.as_view(), name='game_create'),
    path('games/<int:pk>/update/', GameUpdateView.as_view(), name='game_update'),
    path('games/<int:pk>/delete/', GameDeleteView.as_view(), name='game_delete'),
    path("check_password/", check_password, name="check_password"),
]

