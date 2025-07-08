# AI-Powered NLP API Service

A robust Django REST Framework backend for Natural Language Processing (NLP) tasks. This service provides secure user authentication, sentiment analysis, and text summarization. It's built with modern practices like Docker and designed for scalability and future integration of advanced AI models.

## Key Features:

* **Secure User Authentication:** JWT-based user registration, login, and profile management.
* **NLP Capabilities:** API endpoints for Sentiment Analysis and Text Summarization (powered by external LLMs like Google Gemini initially).
* **Scalability & Deployment:** Built with Docker for containerization, ensuring easy setup and consistent environments.
* **Admin Panel:** Customized Django Admin for user and data management.

## Getting Started:

1.  **Clone the repository.**
2.  **Set up a virtual environment.**
3.  **Install dependencies** (`pip install -r requirements.txt`).
4.  **Configure `core/config.py`** with your `SECRET_KEY` and other sensitive settings (ensure it's in `.gitignore`).
5.  **Apply migrations** (`python manage.py migrate`).
6.  **Create a superuser** (`python manage.py createsuperuser`).
7.  **Run the development server** (`python manage.py runserver`).

More detailed documentation, API endpoints, and future enhancements will be added soon!
