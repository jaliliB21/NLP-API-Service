# nlp_services/views.py

import json
import asyncio
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db import transaction

# Import the processor instance
from nlp_services.processors.llm_processor import processor_instance


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

