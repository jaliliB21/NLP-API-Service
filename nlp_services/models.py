from django.db import models
from django.conf import settings # To access the CustomUser model

class AnalysisHistory(models.Model):
    """
    Model to store the history of sentiment analyses.
    """
    ANALYSIS_SOURCE_CHOICES = [
        ('gemini', 'Gemini API'),
        ('internal', 'Internal Model'),
        # Add more choices in the future for other APIs if needed
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analysis_history',
        verbose_name="User" # English verbose name
    )
    text_input = models.TextField(verbose_name="Input Text") # English verbose name
    analysis_result = models.JSONField(verbose_name="Analysis Result") # To store complex results (sentiment, score, business insights)
    analysis_source = models.CharField(
        max_length=20,
        choices=ANALYSIS_SOURCE_CHOICES,
        default='gemini', # Default to Gemini for initial phase
        verbose_name="Analysis Source" # English verbose name
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp") # English verbose name

    class Meta:
        verbose_name = "Sentiment Analysis History" # English verbose name
        verbose_name_plural = "Sentiment Analysis Histories" # English verbose name
        ordering = ['-timestamp'] # Order by timestamp, newest first

    def __str__(self):
        return f"Analysis for {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SummarizationHistory(models.Model):
    """
    Model to store the history of text summarizations.
    """
    SUMMARIZATION_SOURCE_CHOICES = [
        ('openai', 'OpenAI API'),
        ('gemini', 'Gemini API'), # new
        ('internal', 'Internal Model'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='summarization_history',
        verbose_name="User" # English verbose name
    )
    text_input = models.TextField(verbose_name="Input Text") # English verbose name
    summarized_text = models.TextField(verbose_name="Summarized Text") # English verbose name
    summarization_source = models.CharField(
        max_length=20,
        choices=SUMMARIZATION_SOURCE_CHOICES,
        default='gemini', # Default to Gemini for initial phase
        verbose_name="Summarization Source" # English verbose name
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp") # English verbose name

    class Meta:
        verbose_name = "Summarization History" # English verbose name
        verbose_name_plural = "Summarization Histories" # English verbose name
        ordering = ['-timestamp']

    def __str__(self):
        return f"Summarization for {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

