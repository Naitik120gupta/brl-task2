from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('notes', views.notes_list, name='notes_list'),                 
    path('note', views.note_detail, name='note_detail'),                 
    # path('note/search', views.note_search, name='note_search'),          
    # path('note/recent', views.recent_notes, name='recent_notes'),        
    # path('note/archive', views.archive_note, name='archive_note'),
    
    #Authentication   
    path('register/', views.register_user, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),    
]
