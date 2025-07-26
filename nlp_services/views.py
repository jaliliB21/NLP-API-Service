import json
import asyncio
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db import transaction
from django.core.cache import caches

# Import the processor instance
from nlp_services.processors.llm_processor import processor_instance

from nlp_services.serializers import (
    SentimentAnalysisRequestSerializer,
    SentimentAnalysisResultSerializer,
    AnalysisHistorySerializer,
)


from nlp_services.models import AnalysisHistory
from django.contrib.auth import get_user_model

User = get_user_model()
processor = processor_instance


class BaseNLPView(APIView):
    """
    A base view for NLP tasks that handles shared logic like
    authentication and usage deduction.
    This version is synchronous.
    """
    permission_classes = [IsAuthenticated]

    # This is a synchronous method
    def _check_and_deduct_usage(self, user, num_items: int = 1):
        with transaction.atomic():
            user_instance = User.objects.select_for_update().get(pk=user.pk)
            if not user_instance.is_pro:
                if user_instance.free_analysis_count >= num_items:
                    user_instance.free_analysis_count -= num_items
                    user_instance.save(update_fields=['free_analysis_count'])
                else:
                    raise Exception("Free usage limit exceeded. Please upgrade your plan.")

    # This is also a synchronous method
    def _save_analysis_history(self, user, text_input, result, source):
        AnalysisHistory.objects.create(
            user=user,
            text_input=text_input,
            analysis_result=result,
            analysis_source=source
        )


# This view now inherits from the synchronous BaseNLPView
class SentimentAnalysisAPIView(BaseNLPView):
    """
    API endpoint for sentiment analysis. Inherits from the sync BaseNLPView.
    """
    # The main view method is a synchronous 'def'
    def post(self, request):
        if not processor:
            return Response({"detail": "AI service not available."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = SentimentAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        texts = serializer.validated_data['texts']
        analysis_type = serializer.validated_data['analysis_type']

        try:
            # Calls the method from the parent BaseNLPView class
            self._check_and_deduct_usage(request.user, len(texts))
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        results = []
        for text in texts:
            cache_key = f"sentiment_cache:{analysis_type}:{hash(text)}"
            cached_result = cache.get(cache_key)

            if cached_result:
                llm_result = json.loads(cached_result)
            else:
                try:
                    # ✅ Key Point: Call the async processor from the sync view using asyncio.run()
                    llm_result = asyncio.run(processor.analyze_sentiment(
                        text=text,
                        analysis_type=analysis_type
                    ))
                    cache.set(cache_key, json.dumps(llm_result), timeout=60*60*24)
                    print(f"Sentiment analysis for '{text[:20]}...' processed by LLM and cached.")

                    # Calls the method from the parent BaseNLPView class
                    self._save_analysis_history(request.user, text, llm_result, processor.provider_name)

                except Exception as e:
                    # We create a dictionary that matches the serializer's structure
                    results.append({
                        "text_input": text,
                        "sentiment_type": "ERROR", # A placeholder value
                        "score": 0.0,
                        "notes": f"Failed to process: {str(e)}" # The error message
                    })
                    continue

            results.append({
                "text_input": text,
                "sentiment_type": llm_result.get('sentiment_type') or llm_result.get('sentiment'),
                "score": llm_result.get('score'),
                "notes": llm_result.get('notes', '')
            })

        response_serializer = SentimentAnalysisResultSerializer(instance=results, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AnalysisHistoryListView(BaseNLPView):
    """
    API endpoint to retrieve the sentiment analysis history for the logged-in user.
    """
    def get(self, request):
        # Filter the history to get records only for the currently authenticated user.
        # The records are ordered by timestamp descending (newest first) by default in the model's Meta class.
        user_history = AnalysisHistory.objects.filter(user=request.user)
        
        # Use the serializer we already created to format the data.
        serializer = AnalysisHistorySerializer(user_history, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
