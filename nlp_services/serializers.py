from rest_framework import serializers
from nlp_services.models import AnalysisHistory


class SentimentAnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer for accepting sentiment analysis requests.
    Accepts a list of texts and an analysis_type.
    """
    texts = serializers.ListField(
        child=serializers.CharField(max_length=5000), 
        min_length=1, 
        max_length=10 
    )
    analysis_type = serializers.CharField(required=True, max_length=50) 

    def validate_analysis_type(self, value):
        supported_types = ['general_sentiment', 'business_intent']
        if value not in supported_types:
            raise serializers.ValidationError(f"Invalid analysis_type. Must be one of: {', '.join(supported_types)}")
        return value


class SentimentAnalysisResultSerializer(serializers.Serializer):
    """
    Serializer for displaying a single sentiment analysis result to the user.
    This is the format returned for each text in the API response.
    """
    text_input = serializers.CharField() 
    sentiment_type = serializers.CharField() 
    score = serializers.FloatField()
    notes = serializers.CharField(allow_blank=True, required=False) 


class AnalysisHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the AnalysisHistory model.
    Displays the model name (analysis_source) and the full JSON result.
    """
    class Meta:
        model = AnalysisHistory
        # Define the exact fields you want to show in the API response
        fields = [
            'text_input', 
            'analysis_source',    # This field will show the model name (e.g., 'mock', 'gemini')
            'analysis_result',    # This field will show the full JSON result from the API
            'timestamp'
        ]