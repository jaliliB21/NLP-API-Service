from django.urls import path
from .views import (
    SentimentAnalysisAPIView,
    AnalysisHistoryListView,
    SummarizationAPIView,          
    SummarizationHistoryListView,
)

urlpatterns = [
    path('sentiment/analyze/', SentimentAnalysisAPIView.as_view(), name='sentiment_analyze'),

    path('history/sentiment/', AnalysisHistoryListView.as_view(), name='sentiment_history'),

    # Summarization URLs (NEW)
    path('summarize/', SummarizationAPIView.as_view(), name='summarize_text'),
    path('history/summarize/', SummarizationHistoryListView.as_view(), name='summarize_history'),
]