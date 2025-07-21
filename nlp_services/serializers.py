from rest_framework import serializers
# AnalysisHistory model is not needed directly in this serializer
# as we only define request/response formats for sentiment analysis.


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
