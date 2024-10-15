import random
import re
from nltk import word_tokenize
from datetime import datetime

# Identity management
def get_user_name():
    name = input("Bot: What's your name? ")
    print(f"Bot: Nice to meet you, {name}!")
    return name

# Pre-processing user input
def preprocess_input(user_input):
    # Convert to lowercase
    user_input = user_input.lower()
    # Remove punctuation
    user_input = re.sub(r"['\.,!?]", "", user_input)
    # Remove newline characters
    user_input = user_input.replace("\n", " ")
    # Tokenize input
    tokens = word_tokenize(user_input)
    # Join tokens back into a processed string
    processed_input = " ".join(tokens)
    return processed_input

# Intent Matching
def match_intent(user_input):
    user_input = preprocess_input(user_input)
    if re.search(r'\bbook\b|\bflight\b|\btravel\b|\breserve\b|\bticket\b', user_input, re.IGNORECASE):
        return "booking"
    elif re.search(r'\bhello\b|\bhi\b|\bhey\b|\bgreetings\b|\bhowdy\b', user_input, re.IGNORECASE):
        return "greeting"
    elif re.search(r'\bthank\b|\bthanks\b|\bthank you\b|\bappreciate\b', user_input, re.IGNORECASE):
        return "thanks"
    elif re.search(r'\bbye\b|\bgoodbye\b|\bsee you\b|\blater\b|\bquit\b|\bexit\b', user_input, re.IGNORECASE):
        return "farewell"
    elif re.search(r'\bhow are you\b|\bhows it going\b|\bhow do you do\b|\bwhats up\b', user_input, re.IGNORECASE):
        return "how_are_you"
    elif re.search(r'\bwhat can you do\b|\bhelp\b|\babilities\b|\bfunctions\b', user_input, re.IGNORECASE):
        return "capabilities"
    elif re.search(r'\bwhat is my name\b|\bwho am i\b|\bdo you know my name\b', user_input, re.IGNORECASE):
        return "user_name"
    else:
        return "unknown"

# Booking Flow
def booking_flow():
    origin = input("Bot: Where are you flying from? ")
    destination = input("Bot: Where are you flying to? ")
    
    # Handle date input with error checking
    while True:
        departure_date = input("Bot: What is your departure date? (e.g., 15-11-2024) ")
        try:
            departure_date_obj = datetime.strptime(departure_date, '%d-%m-%Y')
            break
        except ValueError:
            print("Bot: That doesn't seem like a valid date format. Please enter it in DD-MM-YYYY format.")
    
    return_date = input("Bot: What is your return date? (or type 'one-way' for a one-way trip) ")
    if return_date.lower() != 'one-way':
        try:
            return_date_obj = datetime.strptime(return_date, '%d-%m-%Y')
        except ValueError:
            print("Bot: That doesn't seem like a valid date format. Defaulting to 'one-way'.")
            return_date = 'one-way'

    travel_class = input("Bot: What class would you like to travel in? (economy, business, first) ")
    while travel_class.lower() not in ['economy', 'business', 'first']:
        travel_class = input("Bot: Please choose a valid class (economy, business, first): ")
    
    print(f"Bot: Let me check available flights from {origin} to {destination} on {departure_date} in {travel_class} class.")
    # Simulate flight search
    print("Bot: I found a few options for you. Do you want me to book one? (yes/no)")
    confirm = input("You: ")
    if confirm.lower() in ['yes', 'y']:
        print("Bot: Your flight has been booked successfully!")
    else:
        print("Bot: No problem, let me know if you need anything else.")

# Chatbot Main Loop
def chatbot():
    print("Bot: Hello! Welcome to the Travel Booking Assistant.")
    name = get_user_name()
    print("Bot: You can ask me to book a flight, say hello, thank me, or say goodbye.")
    while True:
        user_input = input(f"{name}: ")
        intent = match_intent(user_input)
        
        if intent == "greeting":
            print(f"Bot: Hello {name}, how can I assist you today?")
        elif intent == "booking":
            booking_flow()
        elif intent == "thanks":
            print("Bot: You're welcome! Happy to help.")
        elif intent == "farewell":
            print(f"Bot: Goodbye {name}, have a great day!")
            break
        elif intent == "how_are_you":
            print("Bot: I'm just a bot, but I'm here to help you!")
        elif intent == "capabilities":
            print("Bot: I can help you book a flight, tell you your name, and answer simple questions.")
        elif intent == "user_name":
            print(f"Bot: Your name is {name}.")
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()