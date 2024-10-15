import random
import re
from nltk import word_tokenize

# Identity management
def get_user_name():
    name = input("Bot: What's your name? ")
    print(f"Bot: Nice to meet you, {name}!")
    return name

# Intent Matching
def match_intent(user_input):
    user_input = user_input.lower()
    if re.search(r'\bbook\b|\bflight\b|\btravel\b', user_input):
        return "booking"
    elif re.search(r'\bhello\b|\bhi\b|\bhey\b', user_input):
        return "greeting"
    elif re.search(r'\bthank\b|\bthanks\b', user_input):
        return "thanks"
    elif re.search(r'\bbye\b|\bgoodbye\b', user_input):
        return "bye"
    else:
        return "unknown"

# Booking Flow
def booking_flow():
    origin = input("Bot: Where are you flying from? ")
    destination = input("Bot: Where are you flying to? ")
    departure_date = input("Bot: What is your departure date? (e.g., 15-11-2024) ")
    return_date = input("Bot: What is your return date? (or type 'one-way' for a one-way trip) ")
    print(f"Bot: Let me check available flights from {origin} to {destination} on {departure_date}.")
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
    while True:
        user_input = input(f"{name}: ")
        intent = match_intent(user_input)
        
        if intent == "greeting":
            print(f"Bot: Hello {name}, how can I assist you today?")
        elif intent == "booking":
            booking_flow()
        elif intent == "thanks":
            print("Bot: You're welcome! Happy to help.")
        elif intent == "bye":
            print(f"Bot: Goodbye {name}, have a great day!")
            break
        else:
            print("Bot: I'm not sure I understand. Could you please clarify?")

# Run the chatbot
if __name__ == "__main__":
    chatbot()