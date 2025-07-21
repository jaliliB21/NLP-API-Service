# This file stores all customizable LLM prompts.

# --- Prompts for Gemini ---
# Gemini works with a single prompt template instead of system/user pairs.
GEMINI_PROMPTS = {
    "sentiment_template": (
        "You are a highly accurate sentiment analysis AI. Analyze the sentiment of the following Persian text. "
        "Categorize it as 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'. "
        "Return ONLY a valid JSON object in the format: "
        "'{ \"sentiment\": \"CATEGORY\", \"score\": 0.95, \"notes\": \"A brief note about the analysis.\" }'.\n\n"
        "Text to analyze: \"{text}\""
    ),
    "summarization_template": (
        "You are a professional text summarizer. Summarize the following Persian text "
        "in approximately {max_words} words. Respond ONLY with the summarized Persian text "
        "and nothing else. Do not add any titles or introductory phrases.\n\n"
        "Text to summarize: \"{text}\""
    ),
}
