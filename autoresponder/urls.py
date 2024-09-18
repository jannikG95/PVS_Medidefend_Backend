from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('upload/', views.ExtractText.as_view(), name='file-upload'),
    path('analyze-text/', views.AnalyzeView.as_view(), name='analyze-text'),
    path('send-rating/', views.RatingView.as_view(), name='send-rating'),
    path('get-records/', views.GeneratedRecordView.as_view(), name='get-records'),
    path('get-records/<int:record_id>/', views.GeneratedRecordView.as_view(), name='get-record-detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('export_records/', views.ExtractRecordView.as_view(), name='export_records'),
]