from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from mainapp import views

urlpatterns = [
    path('post/', views.PostListCreate.as_view()),
    path('post/<int:pk>/', views.PostRetrieveDestroy.as_view()),
    path('post/<int:pk>/like/', views.PostLikeCreate.as_view()),
    path('post/<int:pk>/dislike/', views.PostDislikeCreate.as_view()),
    path('post/<int:pk>/comment/', views.CommentListCreate.as_view()),
    path('comment/<int:pk>/', views.CommentRetrieveDestroy.as_view()),
    path('comment/<int:pk>/like/', views.CommentLikeCreate.as_view()),
    path('comment/<int:pk>/dislike/', views.CommentDislikeCreate.as_view()),
    path('rest-auth/registration/phone/activate', views.ActivatePhonenumber.as_view()),
    path('rest-auth/registration/phone/send-activation-code', views.SendPhonenumberActivationCode.as_view()),
    path('rest-auth/registration/phone/reset-password-confirm', views.PasswordResetConfirmByPhoneActivationCode.as_view()),
]
