from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import re
import math
from typing import List, Dict, Optional

app = Flask(__name__)
CORS(app)

class FAQChatbot:
    def __init__(self):
        self.faq_database = [
            {
                "question": "How do I reset my password?",
                "answer": "To reset your password: 1) Go to the login page, 2) Click 'Forgot Password', 3) Enter your email address, 4) Check your email for reset instructions, 5) Follow the link and create a new password. If you don't receive the email, check your spam folder.",
                "keywords": ["reset", "password", "forgot", "login", "email", "account", "access"]
            },
            {
                "question": "What are your business hours?",
                "answer": "Our business hours are Monday to Friday: 9:00 AM - 6:00 PM EST. We're closed on weekends and major holidays. For urgent matters outside business hours, please use our emergency contact form.",
                "keywords": ["hours", "time", "open", "closed", "schedule", "business", "monday", "friday", "weekend"]
            },
            {
                "question": "How do I contact support?",
                "answer": "You can contact our support team through: 1) Email: support@company.com, 2) Phone: 1-800-SUPPORT, 3) Live chat on our website, 4) Submit a ticket through your account dashboard. Average response time is 2-4 hours.",
                "keywords": ["contact", "support", "help", "email", "phone", "chat", "ticket", "assistance"]
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major payment methods including: Credit cards (Visa, MasterCard, American Express), PayPal, Bank transfers, and digital wallets (Apple Pay, Google Pay). All payments are processed securely.",
                "keywords": ["payment", "pay", "credit", "card", "paypal", "bank", "visa", "mastercard", "money", "billing"]
            },
            {
                "question": "How do I cancel my subscription?",
                "answer": "To cancel your subscription: 1) Log into your account, 2) Go to 'Account Settings', 3) Click 'Subscription', 4) Select 'Cancel Subscription', 5) Follow the confirmation steps. You'll retain access until your current billing period ends.",
                "keywords": ["cancel", "subscription", "account", "billing", "end", "stop", "terminate", "unsubscribe"]
            },
            {
                "question": "How do I update my profile information?",
                "answer": "To update your profile: 1) Sign in to your account, 2) Click on your profile picture or name, 3) Select 'Edit Profile', 4) Update your information, 5) Click 'Save Changes'. Changes take effect immediately.",
                "keywords": ["update", "profile", "edit", "information", "details", "account", "personal", "change"]
            },
            {
                "question": "What is your refund policy?",
                "answer": "We offer a 30-day money-back guarantee. To request a refund: 1) Contact support within 30 days of purchase, 2) Provide your order number, 3) Explain the reason for refund. Refunds are processed within 5-7 business days.",
                "keywords": ["refund", "money", "back", "return", "guarantee", "policy", "purchase", "order"]
            },
            {
                "question": "How do I upgrade my plan?",
                "answer": "To upgrade your plan: 1) Go to 'Account Settings', 2) Click 'Subscription', 3) Choose 'Upgrade Plan', 4) Select your desired plan, 5) Complete payment. Upgrades are effective immediately with prorated billing.",
                "keywords": ["upgrade", "plan", "subscription", "premium", "account", "billing", "features", "tier"]
            }
        ]
        self._preprocess_database()
    
    def _preprocess_database(self):
        for faq in self.faq_database:
            faq['processed_question'] = self._preprocess_text(faq['question'])
            faq['processed_keywords'] = [self._preprocess_text(kw)[0] if self._preprocess_text(kw) else kw for kw in faq['keywords']]
    
    def _preprocess_text(self, text: str) -> List[str]:
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = [word for word in text.split() if len(word) > 2]
        stop_words = {'the', 'and', 'are', 'you', 'for', 'can', 'how', 'what', 'where', 'when', 'why', 'with', 'this', 'that'}
        words = [word for word in words if word not in stop_words]
        return words
    
    def _calculate_cosine_similarity(self, vec1: List[str], vec2: List[str]) -> float:
        if not vec1 or not vec2:
            return 0.0
        set1, set2 = set(vec1), set(vec2)
        intersection = len(set1.intersection(set2))
        magnitude1 = math.sqrt(len(set1))
        magnitude2 = math.sqrt(len(set2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return intersection / (magnitude1 * magnitude2)
    
    def _calculate_word_overlap(self, user_words: List[str], keywords: List[str]) -> float:
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
        user_words = self._preprocess_text(user_question)
        if not user_words:
            return None
        
        best_match = None
        highest_score = 0.0
        
        for faq in self.faq_database:
            keyword_score = self._calculate_cosine_similarity(user_words, faq['processed_keywords'])
            question_score = self._calculate_cosine_similarity(user_words, faq['processed_question'])
            overlap_score = self._calculate_word_overlap(user_words, faq['keywords'])
            
            final_score = (keyword_score * 0.4) + (question_score * 0.3) + (overlap_score * 0.3)
            
            if final_score > highest_score:
                highest_score = final_score
                best_match = {**faq, 'confidence': round(final_score * 100, 2)}
        
        return best_match if highest_score > 0.15 else None
    
    def get_response(self, user_question: str) -> Dict:
        match = self.find_best_match(user_question)
        if match and match['confidence'] > 30:
            return {
                'answer': match['answer'],
                'confidence': match['confidence'],
                'matched_question': match['question']
            }
        else:
            return {
                'answer': "I'm not sure about that specific question. Here are some ways I can help you:<br><br>• Try rephrasing your question<br>• Use the quick questions below<br>• Contact our support team at support@company.com<br>• Call us at 1-800-SUPPORT<br><br>Is there anything else I can help you with?",
                'confidence': 0,
                'matched_question': None
            }

# Initialize chatbot
chatbot = FAQChatbot()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
        }
        .chat-container { 
            width: 90%; 
            max-width: 800px; 
            height: 80vh; 
            background: rgba(255, 255, 255, 0.95); 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); 
            display: flex; 
            flex-direction: column; 
            overflow: hidden; 
            backdrop-filter: blur(10px); 
        }
        .chat-header { 
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); 
            padding: 20px; 
            text-align: center; 
            color: white; 
            position: relative; 
        }
        .chat-header h1 { font-size: 24px; margin-bottom: 5px; }
        .chat-header p { opacity: 0.9; font-size: 14px; }
        .status-indicator { 
            position: absolute; 
            top: 20px; 
            right: 20px; 
            width: 12px; 
            height: 12px; 
            background: #4CAF50; 
            border-radius: 50%; 
            animation: pulse 2s infinite; 
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .chat-messages { 
            flex: 1; 
            padding: 20px; 
            overflow-y: auto; 
            display: flex; 
            flex-direction: column; 
            gap: 15px; 
        }
        .message { 
            max-width: 80%; 
            padding: 12px 18px; 
            border-radius: 18px; 
            animation: slideIn 0.3s ease-out; 
        }
        @keyframes slideIn { 
            from { opacity: 0; transform: translateY(10px); } 
            to { opacity: 1; transform: translateY(0); } 
        }
        .user-message { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            align-self: flex-end; 
            margin-left: auto; 
        }
        .bot-message { 
            background: #f1f3f4; 
            color: #333; 
            align-self: flex-start; 
            border: 1px solid #e0e0e0; 
        }
        .chat-input-container { 
            padding: 20px; 
            background: white; 
            border-top: 1px solid #e0e0e0; 
            display: flex; 
            gap: 10px; 
            align-items: center; 
        }
        .chat-input { 
            flex: 1; 
            padding: 12px 18px; 
            border: 2px solid #e0e0e0; 
            border-radius: 25px; 
            font-size: 16px; 
            outline: none; 
            transition: all 0.3s ease; 
        }
        .chat-input:focus { 
            border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); 
        }
        .send-button { 
            padding: 12px 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px; 
            transition: all 0.3s ease; 
        }
        .send-button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); 
        }
        .confidence-score { font-size: 12px; color: #888; margin-top: 5px; }
        .welcome-message { text-align: center; color: #666; font-style: italic; margin: 20px 0; }
        .quick-questions { 
            padding: 15px 20px; 
            background: #f8f9fa; 
            border-top: 1px solid #e0e0e0; 
        }
        .quick-questions h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
        .quick-question-buttons { display: flex; flex-wrap: wrap; gap: 8px; }
        .quick-question-btn { 
            padding: 8px 16px; 
            background: white; 
            border: 1px solid #ddd; 
            border-radius: 20px; 
            cursor: pointer; 
            font-size: 12px; 
            color: #666; 
            transition: all 0.3s ease; 
        }
        .quick-question-btn:hover { 
            background: #667eea; 
            color: white; 
            transform: translateY(-1px); 
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="status-indicator"></div>
            <h1> FAQ CHATBOT</h1>
           
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                 Welcome! I'm your FAQ assistant. Ask me anything or try the quick questions below!
            </div>
        </div>
        <div class="quick-questions">
            <h3> Quick Questions:</h3>
            <div class="quick-question-buttons">
                <button class="quick-question-btn" onclick="askQuestion('How do I reset my password?')">Reset Password</button>
                <button class="quick-question-btn" onclick="askQuestion('What are your business hours?')">Business Hours</button>
                <button class="quick-question-btn" onclick="askQuestion('How do I contact support?')">Contact Support</button>
                <button class="quick-question-btn" onclick="askQuestion('What payment methods do you accept?')">Payment Methods</button>
                <button class="quick-question-btn" onclick="askQuestion('How do I cancel my subscription?')">Cancel Subscription</button>
            </div>
        </div>
        <div class="chat-input-container">
            <input type="text" id="chatInput" class="chat-input" placeholder="Type your question here..." onkeypress="handleKeyPress(event)">
            <button class="send-button" onclick="sendMessage()">Send </button>
        </div>
    </div>

    <script>
        function addMessage(content, isUser = false, confidence = null) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            let messageContent = content;
            if (!isUser && confidence && confidence > 0) {
                messageContent += `<div class="confidence-score">Confidence: ${confidence}%</div>`;
            }
            messageDiv.innerHTML = messageContent;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (question === '') return;
            
            addMessage(question, true);
            input.value = '';
            
            // Add thinking indicator
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'message bot-message';
            thinkingDiv.innerHTML = ' Thinking...';
            thinkingDiv.id = 'thinking';
            document.getElementById('chatMessages').appendChild(thinkingDiv);
            document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });
                
                // Remove thinking indicator
                document.getElementById('thinking').remove();
                
                const data = await response.json();
                addMessage(data.answer, false, data.confidence);
            } catch (error) {
                document.getElementById('thinking').remove();
                addMessage('Sorry, there was an error processing your request. Please try again.', false);
            }
        }

        function askQuestion(question) {
            document.getElementById('chatInput').value = question;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') { 
                sendMessage(); 
            }
        }

        window.onload = function() {
            document.getElementById('chatInput').focus();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_question = data.get('question', '')
    
    if not user_question:
        return jsonify({'error': 'No question provided'}), 400
    
    response = chatbot.get_response(user_question)
    return jsonify(response)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'message': 'FAQ Chatbot is running!',
        'total_faqs': len(chatbot.faq_database)
    })

if __name__ == '__main__':
    print(" FAQ Chatbot Server Starting...")
    print(" Features: NLP preprocessing, cosine similarity, intent matching")
    print(" Access at: http://localhost:5000")
    print(" Try questions like: 'How do I reset my password?'")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
