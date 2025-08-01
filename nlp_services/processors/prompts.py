# This file stores all customizable LLM prompts.

# --- Prompts for Gemini ---
# Gemini works with a single prompt template instead of system/user pairs.
GEMINI_PROMPTS = {
    "sentiment_template_general": (
        "You are a highly accurate sentiment analysis AI. Analyze the sentiment of the following Persian text. "
        "Categorize it as 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'. "
        "Return ONLY a valid JSON object in the format: "
        "'{ \"sentiment\": \"CATEGORY\", \"score\": 0.95, \"notes\": \"A brief note about the analysis.\" }'.\n\n"
        "Text to analyze: \"{text}\""
    ),

    "sentiment_template_business": (
        "You are an AI specialized in analyzing customer feedback for business insights. For the following Persian text, "
        "determine the customer's intent. Categorize it as 'SATISFIED', 'DISSATISFIED', 'INQUIRY', or 'OTHER'. "
        "Return ONLY a valid JSON object in the format: "
        "'{ \"sentiment\": \"CATEGORY\", \"score\": 0.90, \"notes\": \"Customer is happy with the delivery speed.\" }'.\n\n"
        "Text to analyze: \"{text}\""
    ),

    "summarization_template": (
        "You are a professional text summarizer. Summarize the following Persian text "
        "in approximately {max_words} words. Respond ONLY with the summarized Persian text "
        "and nothing else. Do not add any titles or introductory phrases.\n\n"
        "Text to summarize: \"{text}\""
    ),
}

# --- Prompts for Aggregate (List) Analysis ---
GEMINI_PROMPTS_AGGREGATE = {
    "aggregate_sentiment_general": (
        "You are an AI that analyzes a list of comments and provides a general statistical sentiment summary. "
        "Analyze the following list of Persian comments. "
        "Return ONLY a valid JSON object with the following structure: "
        "'{{ \"overall_sentiment\": \"POSITIVE\", \"satisfaction_score\": 82, \"key_positives\": [], \"key_negatives\": [], \"summary\": \"Overall, 82% of comments were evaluated as positive.\" }}'.\n\n"
        "Comments to analyze:\n{texts}"
    ),
    "aggregate_sentiment_business": (
        "You are an AI specialized in extracting business insights from customer feedback. Analyze the following list of Persian comments. "
        "Return ONLY a valid JSON object with the following structure: "
        "'{{ \"overall_sentiment\": \"MIXED\", \"satisfaction_score\": 65, \"key_positives\": [\"Build Quality\", \"Shipping Speed\"], \"key_negatives\": [\"Poor Battery Life\", \"High Price\"], \"summary\": \"Customers praise the build quality but complain about poor battery life.\" }}'.\n\n"
        "Comments to analyze:\n{texts}"
    ),
}