from django.urls import path
from .views import (
    SentimentAnalysisAPIView,
    AnalysisHistoryListView,
)

urlpatterns = [
    path('sentiment/analyze/', SentimentAnalysisAPIView.as_view(), name='sentiment_analyze'),

    path('history/sentiment/', AnalysisHistoryListView.as_view(), name='sentiment_history'),
]