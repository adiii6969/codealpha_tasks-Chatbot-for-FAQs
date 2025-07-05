import re
import math
from collections import Counter
from typing import List, Dict, Tuple, Optional
import json

class FAQChatbot:
    def __init__(self):
        self.faq_database = [
            {
                "question": "How do I reset my password?",
                "answer": "To reset your password: 1) Go to the login page, 2) Click 'Forgot Password', 3) Enter your email address, 4) Check your email for reset instructions, 5) Follow the link and create a new password.",
                "keywords": ["reset", "password", "forgot", "login", "email", "account", "access"]
            },
            {
                "question": "What are your business hours?",
                "answer": "Our business hours are Monday to Friday: 9:00 AM - 6:00 PM EST. We're closed on weekends and major holidays.",
                "keywords": ["hours", "time", "open", "closed", "schedule", "business", "monday", "friday", "weekend"]
            },
            {
                "question": "How do I contact support?",
                "answer": "You can contact our support team through: Email: support@company.com, Phone: 1-800-SUPPORT, Live chat on our website, or submit a ticket through your account dashboard.",
                "keywords": ["contact", "support", "help", "email", "phone", "chat", "ticket", "assistance"]
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major payment methods including: Credit cards (Visa, MasterCard, American Express), PayPal, Bank transfers, and digital wallets (Apple Pay, Google Pay).",
                "keywords": ["payment", "pay", "credit", "card", "paypal", "bank", "visa", "mastercard", "money", "billing"]
            },
            {
                "question": "How do I cancel my subscription?",
                "answer": "To cancel your subscription: 1) Log into your account, 2) Go to 'Account Settings', 3) Click 'Subscription', 4) Select 'Cancel Subscription', 5) Follow the confirmation steps.",
                "keywords": ["cancel", "subscription", "account", "billing", "end", "stop", "terminate", "unsubscribe"]
            },
            {
                "question": "What is your refund policy?",
                "answer": "We offer a 30-day money-back guarantee. To request a refund, contact support within 30 days of purchase with your order number.",
                "keywords": ["refund", "money", "back", "return", "guarantee", "policy", "purchase", "order"]
            }
        ]
        
        # Preprocess FAQ database
        self._preprocess_database()
    
    def _preprocess_database(self):
        """Preprocess all FAQ entries for better matching"""
        for faq in self.faq_database:
            faq['processed_question'] = self._preprocess_text(faq['question'])
            faq['processed_keywords'] = [self._preprocess_text(kw)[0] if self._preprocess_text(kw) else kw for kw in faq['keywords']]
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text using NLP techniques:
        - Convert to lowercase
        - Remove punctuation
        - Tokenize
        - Remove stop words and short words
        """
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Tokenize and filter
        words = [word for word in text.split() if len(word) > 2]
        
        # Simple stop words removal
        stop_words = {'the', 'and', 'are', 'you', 'for', 'can', 'how', 'what', 'where', 'when', 'why', 'with', 'this', 'that'}
        words = [word for word in words if word not in stop_words]
        
        return words
    
    def _calculate_cosine_similarity(self, vec1: List[str], vec2: List[str]) -> float:
        """Calculate cosine similarity between two text vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        # Convert to sets for intersection
        set1, set2 = set(vec1), set(vec2)
        intersection = len(set1.intersection(set2))
        
        # Calculate cosine similarity
        magnitude1 = math.sqrt(len(set1))
        magnitude2 = math.sqrt(len(set2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return intersection / (magnitude1 * magnitude2)
    
    def _calculate_jaccard_similarity(self, vec1: List[str], vec2: List[str]) -> float:
        """Calculate Jaccard similarity between two text vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        set1, set2 = set(vec1), set(vec2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_word_overlap(self, user_words: List[str], keywords: List[str]) -> float:
        """Calculate direct word overlap score"""
        if not user_words:
            return 0.0
        
        overlap_count = 0
        for word in user_words:
            for keyword in keywords:
                if word in keyword or keyword in word:
                    overlap_count += 1
                    break
        
        return overlap_count / len(user_words)
    
    def find_best_match(self, user_question: str) -> Optional[Dict]:
        """
        Find the best matching FAQ using multiple similarity techniques:
        - Cosine similarity
        - Jaccard similarity  
        - Keyword overlap
        - Question similarity
        """
        user_words = self._preprocess_text(user_question)
        
        if not user_words:
            return None
        
        best_match = None
        highest_score = 0.0
        
        for faq in self.faq_database:
            # Method 1: Keyword matching (cosine similarity)
            keyword_cosine = self._calculate_cosine_similarity(user_words, faq['processed_keywords'])
            
            # Method 2: Question similarity (cosine similarity)
            question_cosine = self._calculate_cosine_similarity(user_words, faq['processed_question'])
            
            # Method 3: Jaccard similarity with keywords
            keyword_jaccard = self._calculate_jaccard_similarity(user_words, faq['processed_keywords'])
            
            # Method 4: Direct word overlap
            word_overlap = self._calculate_word_overlap(user_words, faq['keywords'])
            
            # Weighted combination of all methods
            final_score = (
                keyword_cosine * 0.3 +
                question_cosine * 0.25 + 
                keyword_jaccard * 0.25 +
                word_overlap * 0.2
            )
            
            if final_score > highest_score:
                highest_score = final_score
                best_match = {
                    **faq,
                    'confidence': round(final_score * 100, 2),
                    'scores': {
                        'keyword_cosine': round(keyword_cosine, 3),
                        'question_cosine': round(question_cosine, 3),
                        'keyword_jaccard': round(keyword_jaccard, 3),
                        'word_overlap': round(word_overlap, 3),
                        'final_score': round(final_score, 3)
                    }
                }
        
        # Return match only if confidence is above threshold
        return best_match if highest_score > 0.15 else None
    
    def get_response(self, user_question: str) -> Dict:
        """Get chatbot response for user question"""
        match = self.find_best_match(user_question)
        
        if match and match['confidence'] > 30:
            return {
                'answer': match['answer'],
                'confidence': match['confidence'],
                'matched_question': match['question'],
                'scores': match['scores']
            }
        else:
            return {
                'answer': "I'm not sure about that specific question. Please try rephrasing or contact our support team at support@company.com",
                'confidence': 0,
                'matched_question': None,
                'scores': None
            }
    
    def chat(self):
        """Interactive chat interface"""
        print(" FAQ Chatbot")
        print("="*50)
        print("Ask me anything! Type 'quit' to exit.\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Bot: Goodbye! Have a great day! 👋")
                break
            
            if not user_input:
                continue
            
            response = self.get_response(user_input)
            print(f"\nBot: {response['answer']}")
            
            if response['confidence'] > 0:
                print(f"Confidence: {response['confidence']}%")
                print(f"Matched: {response['matched_question']}")
            
            print("-" * 50)

def main():
    """Main function to run the chatbot"""
    chatbot = FAQChatbot()
    
    # Example usage
    print("FAQ Chatbot Demo")
    print("="*50)
    
    # Test questions
    test_questions = [
        "How can I reset my password?",
        "What time are you open?", 
        "I need help with support",
        "What cards do you accept?",
        "How to cancel subscription?",
        "Random question about something else"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = chatbot.get_response(question)
        print(f"A: {response['answer']}")
        print(f"Confidence: {response['confidence']}%")
        print("-" * 30)
    
    # Start interactive chat
    print("\nStarting interactive mode...")
    chatbot.chat()

if __name__ == "__main__":
    main()
