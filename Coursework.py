import random
import re
from nltk import word_tokenize, ngrams
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
    return tokens

# Intent Matching with N-Grams
def match_intent(user_input):
    tokens = preprocess_input(user_input)

    # Create bigrams and trigrams from tokens
    bigrams = list(ngrams(tokens, 2))
    trigrams = list(ngrams(tokens, 3))

    # Convert bigrams and trigrams to sets of strings for easier comparison
    bigram_strings = {" ".join(bigram) for bigram in bigrams}
    trigram_strings = {" ".join(trigram) for trigram in trigrams}

    # Check for intents based on tokens, bigrams, and trigrams
    if set(tokens).intersection({'book', 'flight', 'travel', 'reserve', 'ticket'}) or bigram_strings.intersection({'book flight', 'reserve ticket'}) or trigram_strings.intersection({'i want to book', 'can i reserve'}):
        return "booking"
    elif set(tokens).intersection({'hello', 'hi', 'hey', 'greetings', 'howdy'}) or bigram_strings.intersection({'hi there', 'hello bot'}):
        return "greeting"
    elif set(tokens).intersection({'thank', 'thanks', 'appreciate'}) or bigram_strings.intersection({'thank you', 'much appreciated'}):
        return "thanks"
    elif set(tokens).intersection({'bye', 'goodbye', 'see', 'later', 'quit', 'exit'}) or bigram_strings.intersection({'see you', 'goodbye bot'}) or trigram_strings.intersection({'talk to you later', 'see you soon'}):
        return "farewell"
    elif bigram_strings.intersection({'how are', 'whats up'}) or trigram_strings.intersection({'how is it', 'how do you'}):
        return "how_are_you"
    elif bigram_strings.intersection({'what can', 'help me'}) or trigram_strings.intersection({'what can you', 'how can you'}):
        return "capabilities"
    elif set(tokens).intersection({'what', 'is', 'my', 'name', 'who', 'am', 'i'}) or bigram_strings.intersection({'my name', 'who am'}) or trigram_strings.intersection({'what is my', 'do you know my'}):
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