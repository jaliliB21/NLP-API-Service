# NLP API Service

This project is a scalable Natural Language Processing (NLP) API service built with Django, designed to provide powerful text analysis capabilities. It features a modular architecture that supports various analysis types and external service integrations.

## ✨ Key Features


- **Multi-Type Analysis:** The service performs both individual (single comment) and aggregated (multiple comments) sentiment analysis.
- **Sentiment Classification:** Supports two distinct sentiment analysis modes:
  - **General Analysis:** Classifies sentiment as either positive or negative
  - **Business Analysis:** Identifies business-oriented sentiment, such as customer satisfaction or purchase intent.
- **Text Summarization:** Provides a dedicated endpoint for single-text summarization.
- **Caching & Efficiency:** Implements a three-layered caching and data retrieval system:
  - **Redis Cache:** Checks for a cached response for the given request.
  - **Database:** Verifies if the result has been stored previously in the database.
  - **External Service:** If not found in cache or database, a new request is made to an external NLP service.
- **Secure Authentication:** Integrates a robust authentication system using **JWT (Simple JWT)** for user registration, login, and password recovery.
- **Real-Time Updates:** Utilizes **WebSockets** to send real-time notifications to the frontend, allowing for immediate updates on user registrations or profile changes without page refreshes.



## ⚙️ Architectural Design
The project is built on a strong, scalable architecture:

- **Strategy Pattern:** The core analysis logic is designed using the Strategy design pattern, allowing for seamless integration with different external NLP services (e.g., Gemini, ChatGPT). This ensures the application is flexible and easy to extend with new models.
- **Task Processor:** **Celery** is used to manage **asynchronous email sending** via SMTP. This ensures the email sending process is performed in the background, so the user doesn't have to wait, and the main API remains responsive and fast.


## 🚀 Getting Started
To get the project up and running, follow these steps:

1.  Clone the repository.
2.  Install dependencies.
3.  Set up the PostgreSQL database.
4.  Run migrations.
5.  Start the development server.


Detailed instructions can be found in the `CONTRIBUTING.md` file.


## 🤝 Contributions
This project is under active development. Your contributions are highly welcome! Feel free to open issues, submit pull requests, or suggest new features.



