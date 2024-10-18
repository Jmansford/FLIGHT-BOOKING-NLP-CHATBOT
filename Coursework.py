import random
import re
from nltk import word_tokenize, ngrams
from datetime import datetime, timedelta

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

# Intent Matching with N-Grams and Query Expansion
def match_intent(user_input):
    tokens = preprocess_input(user_input)

    # Create bigrams and trigrams from tokens
    bigrams = list(ngrams(tokens, 2))
    trigrams = list(ngrams(tokens, 3))

    # Convert bigrams and trigrams to sets of strings for easier comparison
    bigram_strings = {" ".join(bigram) for bigram in bigrams}
    trigram_strings = {" ".join(trigram) for trigram in trigrams}

    # Define synonym expansion dictionary
    synonym_dict = {
        "book": ["reserve", "schedule"],
        "flight": ["ticket", "air travel"],
        "travel": ["journey", "trip"],
        "hello": ["hi", "hey", "greetings"],
        "goodbye": ["bye", "farewell", "see you"]
    }

    # Expand tokens with synonyms
    expanded_tokens = set(tokens)
    for token in tokens:
        if token in synonym_dict:
            expanded_tokens.update(synonym_dict[token])

    # Check for intents based on tokens, bigrams, and trigrams
    if set(tokens).intersection({'book', 'flight', 'travel', 'reserve', 'ticket', 'fly'}) or bigram_strings.intersection({'book flight', 'reserve ticket'}) or trigram_strings.intersection({'i want to book', 'can i reserve'}):
        return "booking"
    elif set(expanded_tokens).intersection({'hello', 'hi', 'hey', 'greetings', 'howdy'}) or bigram_strings.intersection({'hi there', 'hello bot'}):
        return "greeting"
    elif set(expanded_tokens).intersection({'thank', 'thanks', 'appreciate'}) or bigram_strings.intersection({'thank you', 'much appreciated'}):
        return "thanks"
    elif set(expanded_tokens).intersection({'bye', 'goodbye', 'see', 'later', 'quit', 'exit'}) or bigram_strings.intersection({'see you', 'goodbye bot'}) or trigram_strings.intersection({'talk to you later', 'see you soon'}):
        return "farewell"
    elif bigram_strings.intersection({'how are', 'whats up'}) or trigram_strings.intersection({'how is it', 'how do you'}):
        return "how_are_you"
    elif bigram_strings.intersection({'what can', 'help me'}) or trigram_strings.intersection({'what can you', 'how can you'}):
        return "capabilities"
    elif set(tokens).intersection({'what', 'is', 'my', 'name', 'who', 'am', 'i'}) or bigram_strings.intersection({'my name', 'who am'}) or trigram_strings.intersection({'what is my', 'do you know my'}):
        return "user_name"
    else:
        # Fallback logic using expanded tokens if no direct match is found
        if set(expanded_tokens).intersection({'book', 'flight', 'travel', 'reserve', 'ticket', 'fly', 'schedule', 'journey', 'trip'}):
            return "booking"
        else:
            return "unknown"

# Date Parsing Function
def parse_date(input_date, reference_date=None):
    input_date = input_date.lower()
    if not reference_date:
        reference_date = datetime.now()
    if input_date == "tomorrow":
        return reference_date + timedelta(days=1)
    elif "in" in input_date and "days" in input_date:
        try:
            days = int(re.search(r"\d+", input_date).group())
            return reference_date + timedelta(days=days)
        except AttributeError:
            return None
    elif "days later" in input_date:
        try:
            days = int(re.search(r"\d+", input_date).group())
            return reference_date + timedelta(days=days)
        except AttributeError:
            return None
    elif "next week" in input_date or "week later" in input_date:
        return reference_date + timedelta(weeks=1)
    else:
        try:
            return datetime.strptime(input_date, '%d-%m-%Y')
        except ValueError:
            return None

# Booking Flow
def booking_flow(name):
    print("Bot: Where are you flying from?")
    origin = input(f"\n{name}: ")
    print("Bot: Where are you flying to?")
    destination = input(f"\n{name}: ")
    
    # Handle departure date input
    while True:
        print("Bot: What is your departure date? (e.g., 15-11-2024, tomorrow, in 3 days)")
        departure_date = input(f"\n{name}: ")
        departure_date_obj = parse_date(departure_date)
        if departure_date_obj:
            break
        else:
            print("Bot: That doesn't seem like a valid date. Please try again.")
    
    # Handle return date input
    print("Bot: What is your return date? (e.g., one-way, 5 days later, one week later)")
    return_date = input(f"\n{name}: ")
    if return_date.lower() != 'one-way':
        return_date_obj = parse_date(return_date, reference_date=departure_date_obj)
        if not return_date_obj:
            print("Bot: That doesn't seem like a valid date. Defaulting to 'one-way'.")
            return_date = 'one-way'
    else:
        return_date_obj = None

    print("Bot: What class would you like to travel in? (economy, business, first)")
    travel_class = input(f"\n{name}: ")
    while travel_class.lower() not in ['economy', 'business', 'first']:
        travel_class = input("Bot: Please choose a valid class (economy, business, first): ")
    
    print(f"Bot: Let me check available flights from {origin} to {destination} on {departure_date_obj.strftime('%d-%m-%Y')} in {travel_class} class.")
    if return_date_obj:
        print(f"Bot: The return date is {return_date_obj.strftime('%d-%m-%Y')}.")
    # Simulate flight search
    print("Bot: I found a few options for you. Do you want me to book one? (yes/no)")
    confirm = input(f"\n{name}: ")
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
            booking_flow(name)
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
