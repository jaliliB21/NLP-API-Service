import json
import asyncio
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db import transaction
from django.core.cache import caches
import hashlib

# Import the processor instance
from nlp_services.processors.llm_processor import processor_instance

from nlp_services.serializers import (
    SentimentAnalysisRequestSerializer,
    SentimentAnalysisResultSerializer,
    AnalysisHistorySerializer,
    SummarizationRequestSerializer,
    SummarizationResultSerializer,
    SummarizationHistorySerializer,
    AggregateAnalysisRequestSerializer, 
    AggregateAnalysisResultSerializer,
)


from nlp_services.models import AnalysisHistory, SummarizationHistory, AggregateAnalysisHistory
from django.contrib.auth import get_user_model

User = get_user_model()
processor = processor_instance


def normalize_text_simple(text: str) -> str:
    """
    A simple normalization function for Persian text.
    It removes extra whitespace and trailing periods.
    """
    if not isinstance(text, str):
        return ""

    # 1. Remove leading/trailing whitespace
    text = text.strip()
    
    # 2. Collapse multiple spaces/tabs/newlines in the middle of the text into a single space
    text = ' '.join(text.split())
    
    # 3. Remove all trailing periods from the end of the string
    text = text.strip('.')
    
    return text


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
    def _save_analysis_history(self, user, text_input, result, source, analysis_type):
        AnalysisHistory.objects.create(
            user=user,
            text_input=text_input,
            analysis_result=result,
            analysis_source=source,
            analysis_type=analysis_type
        )

    def _save_summarization_history(self, user, text_input, summarized_text, source, max_words):
        """
        Saves the text summarization result to history.
        """
        history_entry = SummarizationHistory.objects.create(
            user=user,
            text_input=text_input,
            summarized_text=summarized_text,
            summarization_source=source,
            max_words_summarization=max_words
        )

    def _save_aggregate_history(self, user, url, result, source, analysis_type, fingerprint, original_texts):
        """
        Saves the aggregate analysis result to its dedicated history model.
        """
        AggregateAnalysisHistory.objects.create(
            user=user,
            url=url, # Use the 'url' field we defined in the model
            analysis_result=result,
            analysis_source=source,
            analysis_type=analysis_type,
            input_fingerprint=fingerprint,
            input_texts=original_texts
        )


# This view now inherits from the synchronous BaseNLPView
class SentimentAnalysisAPIView(BaseNLPView):
    """
    API endpoint for sentiment analysis. Inherits from the sync BaseNLPView.
    """

    def post(self, request):
        if not processor:
            return Response({"detail": "AI service not available."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = SentimentAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        originalـtexts = serializer.validated_data['texts']
        analysis_type = serializer.validated_data['analysis_type']

        try:
            
            self._check_and_deduct_usage(request.user, len(originalـtexts))

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        results = []
        for text in originalـtexts:
            llm_result = None

            normalized_text = normalize_text_simple(text)

            # --- Multi-level Caching Logic Starts Here ---

            # 1. Check Redis cache first (L1 Cache)
            cache_key = f"sentiment_cache:{analysis_type}:{hash(normalized_text)}"
            cached_result = cache.get(cache_key)

            if cached_result:
                print(f"Retrieved sentiment analysis for '{normalized_text[:30]}...' from L1 Cache (Redis).")
                llm_result = json.loads(cached_result)
            else:
                # 2. If not in Redis, check the database (L2 Cache)
                # We search for an existing analysis of the same text by the same user.
                history_entry = AnalysisHistory.objects.filter(user=request.user, text_input=normalized_text, analysis_type=analysis_type).first()
                
                if history_entry:
                    print(f"Retrieved from L2 Cache (Database) and re-populating Redis.")
                    llm_result = history_entry.analysis_result
                    # Re-populate the Redis cache for the next 24 hours
                    cache.set(cache_key, json.dumps(llm_result), timeout=60*60*24)
                else:
                    # 3. If not in any cache, call the external API
                    try:
                        print(f"No cache hit. Calling external API for '{normalized_text[:30]}...'.")
                        llm_result = asyncio.run(processor.analyze_sentiment(
                            text=normalized_text,
                            analysis_type=analysis_type
                        ))
                        # Save to both caches for future requests
                        cache.set(cache_key, json.dumps(llm_result), timeout=60*60*24)
                        self._save_analysis_history(request.user, normalized_text, llm_result, processor.provider_name, analysis_type)

                    except Exception as e:
                        results.append({
                            "text_input": normalized_text, "sentiment_type": "ERROR", "score": 0.0,
                            "notes": f"Failed to process: {str(e)}"
                        })
                        continue
            
            # This part runs for all successful outcomes (from any cache or API)
            results.append({
                "text_input": normalized_text,
                "sentiment_type": llm_result.get('sentiment'),
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


# -- Summarization -- 

class SummarizationAPIView(BaseNLPView):
    """
    API endpoint for text summarization with multi-level caching.
    """
    def post(self, request):
        if not processor:
            return Response({"detail": "AI service not available."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = SummarizationRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data['text']
        max_words = serializer.validated_data['max_words']

        normalized_text = normalize_text_simple(text)

        try:
            self._check_and_deduct_usage(request.user, 1)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        summarized_text = None
        # --- Multi-level Caching Logic Starts Here ---

        # 1. Check Redis cache first (L1 Cache)
        cache_key = f"summarization_cache:{max_words}:{hash(normalized_text)}"
        cached_summary = cache.get(cache_key)

        if cached_summary:
            print(f"Retrieved summarization for '{normalized_text[:30]}...' from L1 Cache (Redis).")
            summarized_text = cached_summary

        else:
            # 2. If not in Redis, check the database (L2 Cache)
            history_entry = SummarizationHistory.objects.filter(user=request.user, text_input=normalized_text, max_words_summarization=max_words).first()

            if history_entry:
                print(f"Retrieved from L2 Cache (Database) and re-populating Redis.")
                summarized_text = history_entry.summarized_text
                # Re-populate the Redis cache for the next 24 hours
                cache.set(cache_key, summarized_text, timeout=60*60*24)
            else:
                # 3. If not in any cache, call the external API
                try:
                    print(f"No cache hit. Calling external API for summarization of '{normalized_text[:30]}...'.")
                    summarized_text = asyncio.run(processor.summarize_text(
                        text=normalized_text,
                        max_words=max_words
                    ))
                    
                    # Save to both caches for future requests
                    cache.set(cache_key, summarized_text, timeout=60*60*24)
                    self._save_summarization_history(
                        request.user, normalized_text, summarized_text, processor.provider_name, max_words
                    )
                except Exception as e:
                    return Response(
                        {"detail": "Failed to summarize text.", "error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        # Prepare and return the response
        response_data = {
            "original_text": normalized_text,
            "summarized_text": summarized_text
        }

        response_serializer = SummarizationResultSerializer(instance=response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class SummarizationHistoryListView(BaseNLPView):
    """
    API endpoint to retrieve the summarization history for the logged-in user.
    """
    def get(self, request):
        user_history = SummarizationHistory.objects.filter(user=request.user)
        serializer = SummarizationHistorySerializer(user_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AggregateSentimentAPIView(BaseNLPView):
    """
    API endpoint for aggregate sentiment analysis with smart URL and content caching.
    """
    def post(self, request):
        if not processor:
            return Response({"detail": "AI service not available."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = AggregateAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        analysis_type = validated_data['analysis_type']
        url = validated_data.get('url')
        force_reanalyze = validated_data.get('force_reanalyze', False)

        # --- Smart URL Handling Logic ---
        if url and not force_reanalyze:
            # Check if this URL has been analyzed before
            existing_analysis = AggregateAnalysisHistory.objects.filter(user=request.user, url=url).first()
            if existing_analysis:
                return Response({
                    "status": "previously_analyzed",
                    "message": "This URL has been analyzed before. To re-analyze, send the request again with 'force_reanalyze': true.",
                    "previous_result": existing_analysis.analysis_result
                }, status=status.HTTP_200_OK)

        try:
            # --- Get the list of texts to analyze ---
            if url:
                texts_to_analyze = ["I am completely satisfied with the product quality and the shipping speed.",
                                        "Unfortunately, my package arrived very late and damaged.",
                                        "I just wanted to ask if this model is also available in another color."
                                    ]
            else:
                texts_to_analyze = validated_data['texts']

            if not texts_to_analyze:
                return Response({"detail": "No texts found to analyze."}, status=status.HTTP_400_BAD_REQUEST)

            # --- Multi-level Caching Logic ---
            normalized_texts = sorted([normalize_text_simple(t) for t in texts_to_analyze])
            content_string = "".join(normalized_texts)
            fingerprint = hashlib.sha256(content_string.encode('utf-8')).hexdigest()

            cache_key = f"aggregate_cache:{analysis_type}:{fingerprint}"
            llm_result = cache.get(cache_key)

            if not llm_result:
                history_entry = AggregateAnalysisHistory.objects.filter(input_fingerprint=fingerprint, analysis_type=analysis_type).first()
                if history_entry:
                    llm_result = history_entry.analysis_result
                    cache.set(cache_key, llm_result, timeout=60*60*24)
                else:
                    self._check_and_deduct_usage(request.user, 1)

                    llm_result = asyncio.run(processor.analyze_aggregate_sentiment(texts_to_analyze, analysis_type))
                    cache.set(cache_key, llm_result, timeout=60*60*24)
                    
                    self._save_aggregate_history(
                        request.user, url, llm_result, processor.provider_name, 
                        analysis_type, fingerprint, texts_to_analyze
                    )
            
            response_serializer = AggregateAnalysisResultSerializer(instance=llm_result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Failed to perform aggregate analysis.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )