"""ghermezit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/posts/', views.PostList.as_view()),
    path('api/posts/<int:pk>/', views.PostRetrieveDestroy.as_view()),
    path('api/create-post/', views.PostCreate.as_view()),
    path('api/posts/<int:pk>/like/', views.PostLikeCreate.as_view()),
    path('api/posts/<int:pk>/dislike/', views.PostDislikeCreate.as_view()),
    path('api/posts/<int:pk>/comments/', views.CommentList.as_view()),
    path('api/comments/<int:pk>/', views.CommentRetrieveDestroy.as_view()),
    path('api/posts/<int:pk>/create-comment/', views.CommentCreate.as_view()),
    path('api/comments/<int:pk>/like/', views.CommentLikeCreate.as_view()),
    path('api/comments/<int:pk>/dislike/', views.CommentDislikeCreate.as_view()),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/rest-auth/', include('dj_rest_auth.urls')),
    path('api/rest-auth/registration/', include('dj_rest_auth.registration.urls'))

]
