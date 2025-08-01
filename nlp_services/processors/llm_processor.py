import os
import json
from abc import ABC, abstractmethod 
import google.generativeai as genai # Only Google's library is needed now
from django.conf import settings 
import asyncio 
from .prompts import GEMINI_PROMPTS # Import only the Gemini prompts


# --- 1. Base Class (Your original structure, UNCHANGED for future use) ---
class BaseLLMProcessor(ABC): 
    _instances = {} 

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def __init__(self, api_key: str): 
        pass

    # This method is kept in the base class for when you re-add OpenAI later
    async def _call_llm_api_async(self, system_prompt: str, user_prompt: str, model: str = None, temperature: float = 0.5) -> str:
        raise NotImplementedError("This method is provider-specific and should be implemented in concrete classes if needed.")

    # This method is also kept for future compatibility
    async def _translate_to_persian(self, text: str, model: str = None) -> str:
        raise NotImplementedError("This method is provider-specific and should be implemented in concrete classes if needed.")

    @abstractmethod
    async def analyze_sentiment(self, text: str, analysis_type: str) -> dict:
        pass

    @abstractmethod
    async def summarize_text(self, text: str, max_words: int) -> str:
        pass

    @abstractmethod
    async def analyze_aggregate_sentiment(self, texts: list, analysis_type: str) -> dict:
        pass


# --- 2. Concrete Class for Google Gemini ---

class GeminiProcessor(BaseLLMProcessor):
    _initialized_concrete = False

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro-latest"):
        # This method initializes the Gemini client.
        if not GeminiProcessor._initialized_concrete:
            if not api_key:
                raise ValueError("API key must be provided for GeminiProcessor.")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.provider_name = "gemini"
            self.default_model = model_name
            GeminiProcessor._initialized_concrete = True
            print("GeminiProcessor client initialized successfully.")

    async def analyze_sentiment(self, text: str, analysis_type: str = "general_sentiment") -> dict:
        # --- LOGIC TO CHOOSE PROMPT BASED ON analysis_type ---
        if analysis_type == 'business_intent':
            prompt_template = GEMINI_PROMPTS["sentiment_template_business"]
        else: 
            prompt_template = GEMINI_PROMPTS["sentiment_template_general"]
        
        final_prompt = prompt_template.format(text=text)
        
        try:
            response = await self.model.generate_content_async(final_prompt)
            response_text = response.text.strip()


            if response_text.startswith("```json"):
                response_text = response_text.strip("```json").strip("```").strip()

            result = json.loads(response_text)
            return result

        except Exception as e:
            print(f"Error calling Gemini API for sentiment analysis: {e}")
            raise Exception(f"Gemini API sentiment analysis call failed: {e}")

    async def summarize_text(self, text: str, max_words: int) -> str:
        # This method also reads its prompt from your prompts.py file.
        prompt_template = GEMINI_PROMPTS["summarization_template"]
        final_prompt = prompt_template.format(text=text, max_words=max_words)
        
        try:
            response = await self.model.generate_content_async(final_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API for summarization: {e}")
            raise Exception(f"Gemini API summarization call failed: {e}")


class MockProcessor(BaseLLMProcessor):
    """
    A mock processor for development and testing.
    It simulates API calls without making any real network requests.
    """
    _initialized_concrete = False

    def __init__(self, api_key: str = "mock_key"):
        # The init method for the mock processor doesn't need to do much.
        if not MockProcessor._initialized_concrete:
            self.provider_name = "mock"
            MockProcessor._initialized_concrete = True
            print("MockProcessor client initialized successfully.")

    async def analyze_sentiment(self, text: str, analysis_type: str = "general_sentiment") -> dict:
        """
        Simulates a successful sentiment analysis API call.
        Returns a hardcoded, successful-looking response instantly.
        """

        print(f"--- MOCK: Analyzing sentiment for: '{text[:30]}...' with type: {analysis_type} ---")
        await asyncio.sleep(0.5) 
        
        # --- LOGIC TO RETURN DIFFERENT MOCK DATA ---
        if analysis_type == 'business_intent':
            return {
                "sentiment": "SATISFIED", 
                "score": 0.95,
                "notes": "This is a mock response for a business intent analysis."
            }
        else:
            return {
                "sentiment": "POSITIVE",
                "score": 0.98,
                "notes": "This is a mock response for a general sentiment analysis."
            }

    async def summarize_text(self, text: str, max_words: int) -> str:
        """
        Simulates a successful summarization API call.
        Returns a hardcoded summary.
        """
        print(f"--- MOCK: Summarizing text: '{text[:30]}...' ---")
        # Simulate a small amount of network/processing delay
        await asyncio.sleep(0.5)
        
        return f"This is a mock summary for the input text with a length of about {max_words} words."

    # --- ADD THIS NEW METHOD IMPLEMENTATION ---
    async def analyze_aggregate_sentiment(self, texts: list, analysis_type: str) -> dict:
        """
        Simulates a successful aggregate sentiment analysis call.
        """
        print(f"--- MOCK: Performing AGGREGATE analysis on {len(texts)} texts with type: {analysis_type} ---")
        await asyncio.sleep(1) # Simulate a longer processing time

        if analysis_type == "business_intent":
            # This dictionary now returns English strings
            return {
                "overall_sentiment": "MIXED",
                "satisfaction_score": 65,
                "key_positives": ["Build Quality", "Shipping Speed"],
                "key_negatives": ["Poor Battery Life", "High Price"],
                "summary": "Most users are satisfied with the quality, but battery life is a key weakness."
            }
        else: # Default to general
            # This dictionary is also updated to return English strings
            return {
                "overall_sentiment": "POSITIVE",
                "satisfaction_score": 82,
                "key_positives": [],
                "key_negatives": [],
                "summary": "Overall, 82% of the comments were evaluated as positive."
            }

# --- Instance Creation (Directly creates the Gemini processor) ---
# gemini_api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
# if not gemini_api_key:
#     raise ValueError("Google Gemini API key (GEMINI_API_KEY) not found.")

# Activate the mock processor
processor_instance = MockProcessor(api_key="mock_key")