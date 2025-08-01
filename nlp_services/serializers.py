from rest_framework import serializers
from nlp_services.models import AnalysisHistory, SummarizationHistory, AggregateAnalysisHistory


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
    timestamp = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = AnalysisHistory
        # Define the exact fields you want to show in the API response
        fields = [
            'text_input', 
            'analysis_source',    # This field will show the model name (e.g., 'mock', 'gemini')
            'analysis_result',    # This field will show the full JSON result from the API
            'timestamp'
        ]


# --- Serializers for Text Summarization ---

class SummarizationRequestSerializer(serializers.Serializer):
    """
    Serializer for accepting a text summarization request.
    """
    text = serializers.CharField(max_length=10000) # Text to be summarized
    max_words = serializers.IntegerField(default=50, min_value=10, max_value=300) # Optional word limit


class SummarizationResultSerializer(serializers.Serializer):
    """
    Serializer for displaying the summarization result.
    """
    original_text = serializers.CharField()
    summarized_text = serializers.CharField()


class SummarizationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the SummarizationHistory model.
    """
    timestamp = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = SummarizationHistory
        # Define the fields to be included in the history response
        fields = [
            'text_input',
            'summarized_text',
            'summarization_source',
            'timestamp',
        ]


# -- AggregateAnalysis Serializers -- 

class AggregateAnalysisRequestSerializer(serializers.Serializer):
    """
    Serializer to accept either a list of texts OR a URL for aggregate analysis.
    """
    texts = serializers.ListField(
        child=serializers.CharField(max_length=5000), 
        required=False, # Not required if a URL is provided
        max_length=200  # As requested, limit to 200 texts
    )
    url = serializers.URLField(required=False) # Not required if texts are provided
    analysis_type = serializers.CharField(default='business_intent')

    
    force_reanalyze = serializers.BooleanField(default=False)

    def validate(self, data):
        """
        Check that either 'texts' or 'url' is provided, but not both.
        """
        if not data.get('texts') and not data.get('url'):
            raise serializers.ValidationError("Either 'texts' or a 'url' must be provided.")
        if data.get('texts') and data.get('url'):
            raise serializers.ValidationError("Provide either 'texts' or a 'url', not both.")
        return data


class AggregateAnalysisResultSerializer(serializers.Serializer):
    """
    Serializer for the result of an aggregate analysis.
    """
    overall_sentiment = serializers.CharField()
    satisfaction_score = serializers.IntegerField()
    key_positives = serializers.ListField(child=serializers.CharField())
    key_negatives = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()


class AggregateAnalysisHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the AggregateAnalysisHistory model to display the user's history.
    """
    timestamp = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = AggregateAnalysisHistory
        # Define the exact fields you want to return in the API response
        fields = [
            'url',
            'input_texts',
            'analysis_result',
            'analysis_source',
            'analysis_type',
            'timestamp',
        ]