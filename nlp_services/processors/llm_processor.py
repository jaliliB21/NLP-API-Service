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
        # --- NEW DEBUGGING LINE ---
        # This will confirm that the method is being called.
        print(f"DEBUG: Entering analyze_sentiment for text: '{text[:30]}...'")

        prompt_template = GEMINI_PROMPTS["sentiment_template"]
        final_prompt = prompt_template.format(text=text)
        
        try:
            response = await self.model.generate_content_async(final_prompt)
            response_text = response.text.strip()
            
            # Original debug line, which we expect to NOT see
            print(f"DEBUG: Raw response from Gemini: {response_text}")

            if response_text.startswith("```json"):
                response_text = response_text.strip("```json").strip("```").strip()
            
            data = json.loads(response_text)

            sentiment_value = data.get('sentiment') or data.get('label')
            
            if not sentiment_value:
                raise KeyError("Response JSON did not contain a 'sentiment' or 'label' key.")

            result = {
                "sentiment": sentiment_value.upper(),
                "score": data.get('score', 0.0),
                "notes": data.get('notes', f'Analyzed by {self.provider_name}')
            }
            return result

        except Exception as e:
            print(f"Error processing Gemini response: {e}")
            raise Exception(f"Gemini processing failed: {e}")

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


# --- Instance Creation (Directly creates the Gemini processor) ---
gemini_api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
if not gemini_api_key:
    raise ValueError("Google Gemini API key (GEMINI_API_KEY) not found.")

# The processor_instance is now always a GeminiProcessor
processor_instance = GeminiProcessor(api_key=gemini_api_key)