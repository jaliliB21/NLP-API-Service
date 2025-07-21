from django.urls import path
from .views import (
    SentimentAnalysisAPIView,

)

urlpatterns = [
    path('sentiment/analyze/', SentimentAnalysisAPIView.as_view(), name='sentiment_analyze'),
]