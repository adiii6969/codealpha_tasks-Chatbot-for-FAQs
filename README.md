# **codealpha_tasks-Chatbot-for-FAQs**
****FAQ Chatbot****
A smart, responsive FAQ chatbot built with advanced Natural Language Processing (NLP) techniques. The chatbot uses multiple similarity algorithms to provide accurate answers to user questions with confidence scoring.

Features
Advanced NLP Processing: Uses cosine similarity, Jaccard similarity, and word overlap algorithms
Multiple Interfaces: Standalone HTML, Python CLI, and Flask web application
Confidence Scoring: Shows confidence levels for each response
Real-time Processing: Instant responses with thinking indicators
Responsive Design: Beautiful, modern UI with glassmorphism effects
Quick Questions: Pre-defined common questions for easy access
Extensible FAQ Database: Easy to add new questions and answers

Live Features:
🔍 Smart question matching
📊 Confidence scoring
💬 Interactive chat interface
🎨 Modern glassmorphism design
📱 Mobile-responsive layout

Quick Start

Clone the repository
bashgit clone https://github.com/yourusername/faq-chatbot.git
cd faq-chatbot

Install dependencies
bashpip install -r requirements.txt

Run the application
Option 1: Flask Web App (Recommended)
bashpython app.py
Open your browser and go to http://localhost:5000

Option 2: Python CLI
bashpython chatbot.py

Option 3: Standalone HTML
bash# Open the HTML file directly in your browser
open index.html

Project Structure
faq-chatbot/
├── app.py                 # Flask web application
├── chatbot.py            # Python CLI version
├── index.html            # Standalone HTML version
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── screenshots/         # Demo screenshots

Example Questions

"How do I reset my password?"
"What are your business hours?"
"How do I contact support?"
"What payment methods do you accept?"
"How do I cancel my subscription?"

Adding New FAQs

{
    "question": "Your new question?",
    "answer": "Your detailed answer here...",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}
