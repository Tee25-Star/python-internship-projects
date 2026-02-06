from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# FAQ Database - You can expand this with more questions
FAQ_DATABASE = {
    "greeting": {
        "patterns": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
        "responses": [
            "Hello! ?? Welcome to our company. How can I assist you today?",
            "Hi there! I'm here to help answer your questions. What would you like to know?",
            "Greetings! Feel free to ask me anything about our company."
        ]
    },
    "hours": {
        "patterns": ["hours", "open", "closed", "when", "time", "business hours", "working hours"],
        "responses": [
            "Our business hours are Monday to Friday, 9:00 AM - 6:00 PM EST. We're closed on weekends and public holidays.",
            "We're open Monday through Friday from 9 AM to 6 PM Eastern Time. Need help outside these hours? Leave us a message!"
        ]
    },
    "contact": {
        "patterns": ["contact", "phone", "email", "address", "reach", "get in touch", "support"],
        "responses": [
            "You can reach us at:\n?? Email: support@company.com\n?? Phone: +1 (555) 123-4567\n?? Address: 123 Business St, City, State 12345",
            "Contact us via:\n• Email: support@company.com\n• Phone: +1 (555) 123-4567\n• Live chat: Available during business hours"
        ]
    },
    "products": {
        "patterns": ["product", "service", "offer", "what do you sell", "what services"],
        "responses": [
            "We offer a wide range of products and services including:\n• Product A - Description\n• Product B - Description\n• Service C - Description\n\nWould you like more details about any specific product?",
            "Our main products and services include innovative solutions for your business needs. Visit our Products page for detailed information!"
        ]
    },
    "pricing": {
        "patterns": ["price", "cost", "pricing", "how much", "fee", "charge", "payment"],
        "responses": [
            "Our pricing varies based on the product or service. For detailed pricing information, please contact our sales team at sales@company.com or call +1 (555) 123-4567.",
            "Pricing depends on your specific needs. We offer custom quotes tailored to your requirements. Would you like to schedule a consultation?"
        ]
    },
    "shipping": {
        "patterns": ["shipping", "delivery", "ship", "deliver", "when will i receive", "track"],
        "responses": [
            "We offer standard shipping (5-7 business days) and express shipping (2-3 business days). You'll receive a tracking number once your order ships.",
            "Shipping options:\n• Standard: 5-7 business days\n• Express: 2-3 business days\n• Overnight: Available for select items\n\nAll orders include tracking information."
        ]
    },
    "returns": {
        "patterns": ["return", "refund", "exchange", "cancel", "send back"],
        "responses": [
            "We offer a 30-day return policy. Items must be in original condition with tags attached. Contact support@company.com to initiate a return.",
            "Returns are accepted within 30 days of purchase. Please contact our customer service team to process your return or exchange."
        ]
    },
    "account": {
        "patterns": ["account", "login", "sign in", "password", "register", "sign up", "create account"],
        "responses": [
            "To create an account, click the 'Sign Up' button on our website. For login issues, use the 'Forgot Password' link or contact support.",
            "You can create an account by clicking 'Sign Up' in the top right corner. Need help with your account? Our support team is here to assist!"
        ]
    },
    "default": {
        "responses": [
            "I'm not sure I understand. Could you rephrase your question? I can help with:\n• Business hours\n• Contact information\n• Products & Services\n• Pricing\n• Shipping & Returns\n• Account questions",
            "I didn't catch that. Try asking about our hours, contact info, products, pricing, shipping, or account help. What would you like to know?",
            "Let me help you better. You can ask me about:\n• Our business hours\n• How to contact us\n• Our products and services\n• Pricing information\n• Shipping and delivery\n• Returns and refunds\n• Account management"
        ]
    }
}

def preprocess_text(text):
    """Clean and normalize user input"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def find_best_match(user_input):
    """Find the best matching FAQ category"""
    user_input = preprocess_text(user_input)
    words = user_input.split()
    
    best_match = None
    best_score = 0
    
    for category, data in FAQ_DATABASE.items():
        if category == "default":
            continue
        
        score = 0
        for pattern in data["patterns"]:
            if pattern in user_input:
                score += len(pattern.split())  # Weight by word count
            for word in words:
                if word in pattern:
                    score += 1
        
        if score > best_score:
            best_score = score
            best_match = category
    
    return best_match if best_score > 0 else "default"

def get_response(user_input):
    """Get response based on user input"""
    category = find_best_match(user_input)
    responses = FAQ_DATABASE[category]["responses"]
    
    # Simple round-robin or you could use random
    import random
    return random.choice(responses)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'response': "Please enter a message.",
                'timestamp': datetime.now().strftime('%H:%M')
            })
        
        # Get bot response
        bot_response = get_response(user_message)
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
    
    except Exception as e:
        return jsonify({
            'response': "I'm sorry, I encountered an error. Please try again.",
            'timestamp': datetime.now().strftime('%H:%M')
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
